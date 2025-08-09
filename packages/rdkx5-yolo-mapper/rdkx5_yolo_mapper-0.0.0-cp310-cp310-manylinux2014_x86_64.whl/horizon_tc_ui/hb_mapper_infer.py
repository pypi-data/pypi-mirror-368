# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import logging
import os

import numpy as np
import onnx
from horizon_nn.executor import ORTExecutor

from horizon_tc_ui.config.mapper_conf_parser import MpConf
from horizon_tc_ui.data import data_loader_factory as dlf
from horizon_tc_ui.helper import get_raw_transformer
from horizon_tc_ui.parser.caffe_parser import CaffeProto
from horizon_tc_ui.parser.onnx_parser import OnnxModel
from horizon_tc_ui.utils.model_utils import add_model_output
from horizon_tc_ui.utils.tool_utils import get_hw_index, init_root_logger


class InferRunner:
    def __init__(self, conf_file, model_file, model_type, image_file_input,
                 input_layout, output_dir):
        self.conf_file = conf_file
        self.input_names = []
        self.image_files_dict = {}
        for input_name, image_file in image_file_input:
            if not os.path.isfile(image_file):
                raise ValueError('image_file not exists.')
            if input_name in self.input_names:
                raise ValueError('input file given already to %s' % input_name)
            self.input_names.append(input_name)
            self.image_files_dict[input_name] = os.path.abspath(image_file)
        if not os.path.isfile(model_file):
            raise ValueError('model_file not exists.')
        if not model_file.endswith(".onnx"):
            raise ValueError(
                f"model_file {model_file} should be an onnx model file")

        self.model_file = os.path.abspath(model_file)
        self.model_type = model_type
        self.output_dir = os.path.abspath(output_dir)
        self.mp_conf = None  # type: MpConf
        self.model = None
        self.input_layout = input_layout

    def _parse_model(self):
        self._parse_conf()
        if self.model is not None:
            return
        if self.mp_conf.model_type == 'caffe':
            self.model = CaffeProto(self.mp_conf.caffe_prototxt)
        else:
            self.model = OnnxModel(self.mp_conf.onnx_model)

    def _parse_conf(self):
        if self.mp_conf is not None:
            return
        self.mp_conf = MpConf(self.conf_file, self.model_type)
        logging.debug("Dump config:")
        logging.debug(self.mp_conf)
        self.march = self.mp_conf.march

    def _init_logger(self):
        log_level = self.mp_conf.log_level
        init_root_logger("hb_mapper_infer", file_level=log_level)

    def _get_index_from_name(self, input_name):
        input_index = 0
        try:
            for name_item in self.mp_conf.input_names:
                if name_item == input_name:
                    return input_index
                input_index += 1
        except Exception:
            logging.error(f"input_name '{input_name}' does not exist in "
                          f"model input names: {self.mp_conf.input_names} ")
            raise ValueError(f"invalid input name: {input_name}")
        return input_index

    def _load_input_data(self, name):
        input_index = self._get_index_from_name(name)
        # infer命令可以不填input_shape, 输入大小信息可从模型文件获取
        input_shape_from_cfg = None
        if self.mp_conf.input_shapes:
            input_shape_from_cfg = self.mp_conf.input_shapes[input_index]
        input_shape_from_model = self.model.get_input_shape(name)
        input_shape = input_shape_from_cfg if input_shape_from_cfg is not None else input_shape_from_model  # noqa
        if input_shape is None:
            # model file also do not contain shape info
            raise ValueError('no input shape from cfg file and model file')
        input_type_rt = self.mp_conf.input_type_rt[input_index]
        input_type_train = self.mp_conf.input_type_train[input_index]
        input_layout_train = self.mp_conf.input_layout_train[input_index]
        height_index, width_index = get_hw_index(input_layout_train)

        cal_data_dir = self.mp_conf.cal_data_dir[input_index]
        if self.mp_conf.cal_data_type and int(input_index) < len(
                self.mp_conf.cal_data_type):
            cal_data_type = self.mp_conf.cal_data_type[input_index]
        else:
            cal_data_type = None

        if cal_data_dir.endswith('_f32'):
            folder_suffix = 'float32'
        else:
            folder_suffix = None
        if cal_data_type:
            if folder_suffix:
                if cal_data_type != folder_suffix:
                    logging.warning(
                        'The calibration dir name suffix is not the same as '
                        f'the value {cal_data_type} of the parameter '
                        f'cal_data_type, the parameter setting will prevail')
                else:
                    logging.info(
                        'The calibration dir name suffix is the same as the '
                        f'value {cal_data_type} of the cal_data_type parameter'
                        ' and will be read with the value of cal_data_type')
            if cal_data_type == 'float32':
                dtype = np.float32
            elif cal_data_type == 'uint8':
                dtype = np.uint8
        else:
            if cal_data_dir.endswith('_f32'):
                dtype = np.float32
            else:
                dtype = np.uint8
            logging.warning(
                'Please note that the input file data type is set to '
                f'{dtype.__name__}, determined by the name of the calibration'
                ' dir name suffix')
            logging.warning(
                'if you need to set it explicitly, please configure the value'
                ' of cal_data_type in the calibration_parameters group in yaml'
            )

        shape = input_shape[1:]  # 最高维度是batch
        input_type_train = self.mp_conf.input_type_train[input_index]
        input_layout_train = self.mp_conf.input_layout_train[input_index]
        transformers = get_raw_transformer(input_type_rt, input_type_train,
                                           input_layout_train,
                                           input_shape[height_index],
                                           input_shape[width_index])
        data_loader = dlf.get_raw_single_loader(transformers,
                                                self.image_files_dict[name],
                                                shape, dtype)
        return np.array(next(data_loader)), input_layout_train

    def pack_layers_output(self, pred_onx_dict):
        for output_name, layer_data in pred_onx_dict.items():
            # Create file name
            file_name = output_name.replace('/', '_') + ".bin"
            file_name = os.path.join(self.output_dir, file_name)
            logging.info("Dump layer data file: {}".format(file_name))
            layer_data.tofile(file_name)

    def _check_input_names(self):
        print("_check_input_names")
        self._parse_model()
        model_input_names = self.model.get_input_names()
        print(model_input_names)
        for name in self.input_names:
            if name not in model_input_names:
                message = 'wrong input name: %s, available: %s' % (
                    name, model_input_names)
                raise ValueError(message)
        return

    def _dump_for_runtime(self, data, input_type_rt, name):
        if input_type_rt not in ['featuremap']:
            data = data.astype(np.int8)
            data = (data + 128).astype(np.uint8)
        elif input_type_rt in ['featuremap']:
            data = data.astype(np.float32)
        data.tofile('%s_input_for_runtime.bin' % name)

    def run(self):
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)
        self._parse_conf()
        self._init_logger()
        self._check_input_names()

        inf_cmp_dict = {}

        for index, name in enumerate(self.input_names):
            input_data, data_input_layout = self._load_input_data(name)
            input_type_rt = \
                self.mp_conf.input_type_rt[self._get_index_from_name(name)]
            if data_input_layout != self.input_layout:
                if data_input_layout == "NHWC" and self.input_layout == "NCHW":
                    input_data = input_data.transpose([0, 3, 1, 2])
                else:
                    input_data = input_data.transpose([0, 2, 3, 1])

            if 'quanti' in self.model_file:
                self._dump_for_runtime(input_data, input_type_rt, name)
            if 'quanti' in self.model_file and \
                    input_type_rt not in ['featuremap']:
                input_data = input_data.astype(np.int8)
            inf_cmp_dict.update({name: input_data})

        if 'quanti' in self.model_file:
            inference_inst = ORTExecutor(self.model_file)
        else:
            model = onnx.load(self.model_file)
            graph = model.graph
            input_names = {input.name for input in graph.input}
            output_names = {output.name for output in graph.output}
            intermediate_nodes = []
            for node in model.graph.node:
                for output in node.output:
                    if output not in input_names and output not in output_names:  # noqa
                        intermediate_nodes.append(node)

            model = add_model_output(model,
                                     [n.name for n in intermediate_nodes])

            inference_inst = ORTExecutor(model)

        output_dict = inference_inst.inference(inf_cmp_dict)
        self.pack_layers_output(output_dict)


def infer_imp(config, model_file, model_type, image_file, input_layout,
              output_dir):
    runner = InferRunner(config, model_file, model_type, image_file,
                         input_layout, output_dir)
    runner.run()
