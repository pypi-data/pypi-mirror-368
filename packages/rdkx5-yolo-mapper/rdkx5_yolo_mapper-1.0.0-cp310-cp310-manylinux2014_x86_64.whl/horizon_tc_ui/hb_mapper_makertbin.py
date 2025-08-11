# Copyright (c) 2022 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import logging
import os
import subprocess
import sys

import numpy as np
import onnx
from hbdk import __version__ as hbdk_version
from horizon_nn.api import build_caffe, build_onnx
from horizon_nn.api import version as horizon_nn_version
from horizon_nn.custom.op_registration import op_register

from horizon_tc_ui.config import mapper_consts
from horizon_tc_ui.config.mapper_conf_parser import MpConf
from horizon_tc_ui.data import data_loader_factory as dlf
from horizon_tc_ui.data.transformer import (F32ToS8Transformer,
                                            F32ToU8Transformer)
from horizon_tc_ui.hbdtort.onnx2horizonrt import build_runtime_model_wrapper
from horizon_tc_ui.helper import get_default_transformer, get_raw_transformer
from horizon_tc_ui.utils.tool_utils import (CStdOutHook, edit_logger,
                                            get_all_data, get_hw_index)


class MakertbinRunner:
    def __init__(self, conf_file, model_type) -> None:
        """
        :param conf_file:  config_file path
        :param model_type: model type
        """
        self.conf_file = conf_file
        self.model_type = model_type
        self.mp_conf = None
        self.model = None  # type: ModelProtoBase
        self.sample_dir = os.getcwd()

    def _parse_conf(self):
        if self.mp_conf is not None:
            return
        try:
            self.mp_conf = MpConf(self.conf_file, self.model_type)
        except Exception as e:
            logging.error("yaml file parse failed. " +
                          "Please double check your config file inputs")
            raise e
        edit_logger(logging.DEBUG)
        logging.debug("Dump config:")
        logging.debug(self.mp_conf)

    def _parse_model(self):
        self._parse_conf()
        for name in self.mp_conf.model.get_input_names():
            logging.debug(f"input '{name}' : original model shape: " +
                          f"{self.mp_conf.model.get_input_shape(name)}")

    # return n, h, w, c value in NHWC sequence
    def _get_nhwc_num(self, shape, layout):
        if len(shape) != 4:
            logging.warning(f"can not get nhwc info from shape: {shape}")
            return None, None, None, None,
        if layout == "NHWC":
            return shape[0], shape[1], shape[2], shape[3]
        elif layout == "NCHW":
            return shape[0], shape[2], shape[3], shape[1]
        else:
            raise ValueError(f"unsupported layout: '{layout}'")

    def _get_index_from_name(self, input_name):
        input_index = -1
        for name_item in self.mp_conf.input_names:
            input_index += 1
            if name_item == input_name:
                return input_index
        logging.error(f"input_name '{input_name}' does not exist in " +
                      f"model input names: {self.mp_conf.input_names} ")
        raise ValueError(f"invalid input name: {input_name}")

    def _get_name_from_index(self, input_index):
        try:
            input_name = self.mp_conf.input_names[input_index]
        except BaseException:
            logging.error(f"input index '{input_index}' invalid." +
                          f"model input names: {self.mp_conf.input_names} ")
            raise ValueError(f"invalid input index: {input_index}")
        return input_name

    def _get_build_input_param(self, input_name):
        input_index = self._get_index_from_name(input_name)
        input_type_rt = self.mp_conf.input_type_rt[input_index]
        input_type_train = self.mp_conf.input_type_train[input_index]
        input_layout_train = self.mp_conf.input_layout_train[input_index]
        input_shape = self.mp_conf.input_shapes[input_index]
        norm_type = self.mp_conf.norm_type[input_index]

        build_input_dict = {
            'input_shape': input_shape,
        }

        if self.mp_conf.input_batches:
            input_batch = self.mp_conf.input_batches[0]
            build_input_dict.update({'input_batch': int(input_batch)})

        if not input_type_rt.startswith('featuremap'):
            build_input_dict.update({
                'expected_input_type':
                    mapper_consts.input_type_rt_parse_dict[input_type_rt],
                'original_input_type':
                    mapper_consts.
                    input_type_train_parse_dict[input_type_train],
            })

        build_input_dict.update({'original_input_layout': input_layout_train})

        if input_type_rt.startswith("featuremap") and norm_type in [
                'data_mean', 'data_scale', 'data_mean_and_scale'
        ]:
            logging.warning(f"input type rt is set as '{input_type_rt}'' " +
                            f"and norm_type is set as '{norm_type}'")
            logging.warning("featuremap usually should use 'no_preprocess'. " +
                            "Please double check 'norm_type' setting")

        _, _, _, channel_num = self._get_nhwc_num(input_shape,
                                                  input_layout_train)

        if channel_num and norm_type in [
                'data_mean', 'data_scale', 'data_mean_and_scale'
        ] and channel_num != 1 and channel_num != 3:
            logging.error(f"input '{input_name}' has {channel_num} channel")
            logging.error(
                "this could be resulted from wrong input_layout_train " +
                f"{input_index}: {input_layout_train}")
            raise ValueError(
                f"{norm_type} only works when input channel num " +
                f"equals to 1 or 3, not {channel_num}")

        if 'mean' in norm_type:
            mean_value = np.asarray(self.mp_conf.mean_value[input_index],
                                    dtype=np.float32)
            build_input_dict.update({'means': mean_value})

        if 'scale' in norm_type:
            scale_value = np.asarray(self.mp_conf.scale_value[input_index],
                                     dtype=np.float32)
            build_input_dict.update({'scales': scale_value})

        return build_input_dict

    def _get_build_input_params(self):
        build_input_dict = {}
        for name in self.mp_conf.input_names:
            build_input_dict[name] = self._get_build_input_param(name)

        return build_input_dict

    def _get_cali_data_loader(self, input_name):
        """
        获取input_name代表的输入的dataloader。
        根据input_type/input_shape/preprocess_on/cal_data_dir
        来确定loader和transformer
        :param input_name:
        :return:
        """
        input_index = self._get_index_from_name(input_name)
        input_type_rt = self.mp_conf.input_type_rt[input_index]
        input_type_train = self.mp_conf.input_type_train[input_index]
        input_layout_train = self.mp_conf.input_layout_train[input_index]
        input_shape = self.mp_conf.input_shapes[input_index]
        preprocess_on = self.mp_conf.preprocess_on

        cal_data_dir = self.mp_conf.cal_data_dir[input_index]
        if self.mp_conf.cal_data_type:
            cal_data_type = self.mp_conf.cal_data_type[input_index]
        else:
            cal_data_type = None

        dtype = None
        dtype_map = {
            "float32": np.float32,
            "uint8": np.uint8,
            "int32": np.int32,
            "int16": np.int16,
            "int8": np.int8
        }
        if cal_data_type in dtype_map:
            dtype = dtype_map[cal_data_type]

        if not dtype:
            if cal_data_dir.endswith('_f32'):
                dtype = np.float32
            else:
                dtype = np.uint8

            logging.warning(
                f'Please note that the calibration file data type is set to'
                f' {dtype.__name__}, '
                f'determined by the name of the calibration dir name suffix.')
            logging.warning('if you need to set it explicitly, '
                            'please configure the value of cal_data_type '
                            'in the calibration_parameters group in yaml.')

        height_index, width_index = get_hw_index(input_layout_train)

        if preprocess_on:
            transformers = get_default_transformer(input_type_rt,
                                                   input_type_train,
                                                   input_layout_train,
                                                   input_shape[height_index],
                                                   input_shape[width_index])
            gray = False if input_type_rt != "gray" else True
            data_loader = \
                dlf.get_image_dir_loader(transformers, cal_data_dir, gray=gray)
        else:
            if input_type_rt.startswith('featuremap'):
                transformers = []
                if input_type_rt.endswith("s8"):
                    transformers.append(F32ToS8Transformer())
                if input_type_rt.endswith("u8"):
                    transformers.append(F32ToU8Transformer())
            else:
                transformers = get_raw_transformer(input_type_rt,
                                                   input_type_train,
                                                   input_layout_train,
                                                   input_shape[height_index],
                                                   input_shape[width_index])

            data_loader = dlf.get_raw_image_dir_loader(transformers,
                                                       cal_data_dir,
                                                       input_shape, dtype)

        return data_loader

    def _op_register(self):
        if not self.mp_conf.custom_op:
            return None

        cop_method = self.mp_conf.custom_op_method
        if "register" != cop_method:
            logging.error(f"custom op method: {cop_method} not recognized")
            raise ValueError(f"custom op method: {cop_method} not recognized")

        sys.path.append('..')
        cop_register_files = self.mp_conf.cop_register_files
        cop_dir = self.mp_conf.custom_op_dir
        # if cop dir exist, user folder name as prefix
        if cop_dir:
            cop_dir_prefix = cop_dir.lstrip("./") + '.'
        else:
            cop_dir_prefix = ''
        for cop_module in cop_register_files:
            if cop_module.endswith(".py"):
                cop_module = os.path.splitext(cop_module)[0]
            op_register(f"{cop_dir_prefix}{cop_module}")
            logging.info(f"{cop_dir} op : {cop_module} registered")

    def _get_build_calibration_params(self):
        if self.mp_conf.calibration_type == "skip":
            self._op_register()
            logging.info("The calibration_type you specified is skip, "
                         "the skip uses max+random data for calibration")
            return {
                'calibration_type': "max",
            }

        cal_data = None
        cal_type = self.mp_conf.calibration_type
        if cal_type != "load":
            cal_data = {}
            loaders = {}
            for name in self.mp_conf.input_names:
                loaders[name] = self._get_cali_data_loader(name)

            # check custom op section
            self._op_register()
            try:
                for input_name in self.mp_conf.input_names:
                    cal_data.update(
                        {input_name: get_all_data(loaders[input_name])})

            except Exception as e:
                logging.error(f"load cal data for input '{input_name}' error")
                raise e
        ret_dict = {
            'calibration_type': cal_type,
            # 'calibration_loader': loaders,
            'calibration_data': cal_data,
        }
        # deprecated
        # if finetune_level > -1:
        #     ret_dict['finetune_level'] = str(finetune_level)
        if self.mp_conf.per_channel:
            ret_dict['per_channel'] = self.mp_conf.per_channel
        if self.mp_conf.max_percentile:
            ret_dict['max_percentile'] = self.mp_conf.max_percentile
        return ret_dict

    def _get_build_hbdk_params(self) -> dict:
        """Generate hbdk pass through params

        Returns:
            dict: hbdk build params
        """

        build_hbdk_params_parse = {'hbdk_pass_through_params': ''}

        if self.mp_conf.optimize_level:
            build_hbdk_params_parse['hbdk_pass_through_params'] += \
                f'--{self.mp_conf.optimize_level} '

        if self.mp_conf.optimize_level == 'O3' \
           and self.mp_conf.march == 'bayes':
            build_hbdk_params_parse['hbdk_pass_through_params'] += \
                f'--cache {self.mp_conf.working_dir}/cache.json '

        if self.mp_conf.input_source:
            build_hbdk_params_parse["input-source"] = self.mp_conf.input_source

        if self.mp_conf.compile_debug_mode:
            build_hbdk_params_parse['hbdk_pass_through_params'] += '--debug '

        if self.mp_conf.ability_entry:
            build_hbdk_params_parse['hbdk_pass_through_params'] += \
                f'--ability-entry {self.mp_conf.ability_entry} '

        if self.mp_conf.core_num:
            build_hbdk_params_parse['hbdk_pass_through_params'] += \
                f'--core-num {self.mp_conf.core_num} '

        if self.mp_conf.compile_mode:
            if self.mp_conf.compile_mode == 'bandwidth':
                build_hbdk_params_parse['hbdk_pass_through_params'] += '--ddr '
            elif self.mp_conf.compile_mode == 'balance':
                build_hbdk_params_parse['hbdk_pass_through_params'] += \
                    f'--balance {self.mp_conf.balance_factor} '
            else:
                build_hbdk_params_parse[
                    'hbdk_pass_through_params'] += '--fast '

        if self.mp_conf.max_time_per_fc:
            build_hbdk_params_parse['hbdk_pass_through_params'] += \
                f'--max-time-per-fc {self.mp_conf.max_time_per_fc} '

        if self.mp_conf.jobs:
            build_hbdk_params_parse[
                'hbdk_pass_through_params'] += f'--jobs {self.mp_conf.jobs} '

        if self.mp_conf.advice:
            build_hbdk_params_parse['hbdk_pass_through_params'] \
                += f'--advice {self.mp_conf.advice} '
        return build_hbdk_params_parse

    def _get_output_nodes(self):
        output_dict = []
        if self.mp_conf.output_nodes:
            output_dict = self.mp_conf.output_nodes
        return output_dict

    def _get_debug_mode(self) -> list:
        debug_mode = []
        if self.mp_conf.layer_out_dump:
            debug_mode.append("dump_all_models")
            debug_mode.append("dump_all_layers_output")
            debug_mode.append("check_model_output_consistency")

        if self.mp_conf.model_debug_mode:
            debug_mode.append(self.mp_conf.model_debug_mode)
        return debug_mode

    def _get_build_node_params(self):
        ret_val = {}

        if self.mp_conf.node_dict:
            ret_val = self.mp_conf.node_dict

        if self.mp_conf.run_on_cpu:
            for item in self.mp_conf.run_on_cpu:
                val_dict = ret_val.get(item, {})
                if not val_dict or "ON" not in val_dict:
                    val_dict["ON"] = "CPU"

                ret_val[item] = val_dict

        if self.mp_conf.run_on_bpu:
            for item in self.mp_conf.run_on_bpu:
                val_dict = ret_val.get(item, {})
                if not val_dict or "ON" not in val_dict:
                    val_dict["ON"] = "BPU"

                ret_val[item] = val_dict

        return ret_val

    # 检测指定 CPU/BPU 运行节点是否存在
    # 参考代码：
    # http://gitlab.hobot.cc/ptd/ap/toolchain/model_convert/blob/develop/compiler/hybrid_builder.cc#L27
    def post_check(self, hybrid_model):
        # modify input name sequence and corresponding confs
        init_names = [init.name for init in hybrid_model.graph.initializer]
        model_names = [
            i.name for i in hybrid_model.graph.input
            if i.name not in init_names
        ]
        if len(model_names) != len(self.mp_conf.input_names):
            raise ValueError(
                f"Wrong num of input names received. "
                f"Num of input names given: {len(self.mp_conf.input_names)}, "
                f"while hybrid model file has {len(model_names)} inputs")
        # if hybrid model input name not equal onnx or caffe model
        # this step will refresh mp_conf
        if model_names != self.mp_conf.input_names:
            input_type_rt_list = []
            input_space_and_range_list = []
            input_layout_rt_list = []
            input_type_train_list = []
            input_layout_train_list = []
            input_shape_list = []
            norm_type_list = []
            mean_value_list = []
            scale_value_list = []
            cal_data_list = []
            cal_data_type_list = []

            for name_item in model_names:
                name_index = self.mp_conf.input_names.index(name_item)
                input_type_rt_list.append(
                    self.mp_conf.input_type_rt[name_index])
                input_space_and_range_list.append(
                    self.mp_conf.input_space_and_range[name_index])
                input_layout_rt_list.append(
                    self.mp_conf.input_layout_rt[name_index])
                input_type_train_list.append(
                    self.mp_conf.input_type_train[name_index])
                input_layout_train_list.append(
                    self.mp_conf.input_layout_train[name_index])
                input_shape_list.append(self.mp_conf.input_shapes[name_index])
                norm_type_list.append(self.mp_conf.norm_type[name_index])
                mean_value_list.append(self.mp_conf.mean_value[name_index])
                scale_value_list.append(self.mp_conf.scale_value[name_index])
                # when calibration_type is load or skip, cal_data_dir might be
                # none
                if self.mp_conf.calibration_type not in ['load', 'skip']:
                    cal_data_list.append(self.mp_conf.cal_data_dir[name_index])
                    cal_data_type_list.append(
                        self.mp_conf.cal_data_type[name_index])

            self.mp_conf.input_names = model_names
            self.mp_conf.input_type_rt = input_type_rt_list
            self.mp_conf.input_space_and_range = input_space_and_range_list
            self.mp_conf.input_layout_rt = input_layout_rt_list
            self.mp_conf.input_type_train = input_type_train_list
            self.mp_conf.input_layout_train = input_layout_train_list
            self.mp_conf.input_shapes = input_shape_list
            self.mp_conf.norm_type = norm_type_list
            self.mp_conf.mean_value = mean_value_list
            self.mp_conf.scale_value = scale_value_list
            self.mp_conf.cal_data_dir = cal_data_list
            self.mp_conf.cal_data_type = cal_data_type_list

        # check run on CPU/BPU nodes
        prefix = self.mp_conf.output_model_file_prefix
        model_name = f'{prefix}_quantized_model.onnx'
        quanti_model = onnx.load(model_name)
        cpu_nodes = dict()
        bpu_nodes = dict()
        graph_nodes = list()
        for node in quanti_model.graph.node:
            if node.op_type in mapper_consts.BPU_OP_TYPES:
                # 特殊情况，当op为以下类型时需要保证所有输入的类型均为int8
                # input type
                # 可以在horizon_tc_ui.hbdtort.runtime.proto.TensorTypeProto中查看
                if node.op_type in ["Concat", "HzSElementWiseAdd"]:
                    for _input in quanti_model.graph.input:
                        if _input.type != 3:
                            cpu_nodes.update({node.name: node.op_type})
                elif node.op_type in mapper_consts.BPU_OP_TYPES_UNIQUE:
                    if quanti_model.graph.input[0].type != 3:
                        cpu_nodes.update({node.name: node.op_type})
                bpu_nodes.update({node.name: node.op_type})
            else:
                cpu_nodes.update({node.name: node.op_type})
            graph_nodes.append(node.name)
        if self.mp_conf.run_on_cpu:
            for item in self.mp_conf.run_on_cpu:
                if item in graph_nodes:
                    if not cpu_nodes.get(item):
                        logging.warning(
                            f"expected cpu node: {item} does not exist")
                else:
                    logging.warning(f"node: {item} does not exist," +
                                    "please double check your input")

        if self.mp_conf.run_on_bpu:
            for item in self.mp_conf.run_on_bpu:
                if item in graph_nodes:
                    if not bpu_nodes.get(item) and cpu_nodes.get(item):
                        logging.warning(
                            f"expected bpu node: {item} does not exist")
                else:
                    logging.warning(f"node: {item} does not exist, " +
                                    "please double check your input")

    # def need_save_model(self):
    #     # log_level 是warning时不输出额外的模型。
    #     # 如果用户设置layer_out_dump为True, 同时需要打开save_mode用于保存输出接口映射表
    #     if not self.mp_conf.layer_out_dump and \
    #             self.mp_conf.log_level is logging.WARN:
    #         return False

    #     return True

    @staticmethod
    def _debug_build_param_log(build_params):
        logging.debug("call build params:\n %s" % build_params)

    def run(self, version):
        """
        1. 初始化日志，以及工作目录
        2. 获取传递给build接口的input参数
        3. 获取传递给build接口的校准相关参数
        4. 获取传递给build接口的hbdk相关参数
        5. 获取layer扩展参数: 是否output、run_on_cpu
        """
        # Create build input params
        logging.info("Start Model Convert....")
        self._parse_model()

        os.chdir(self.mp_conf.working_dir)

        build_input_params = self._get_build_input_params()
        build_cal_params = self._get_build_calibration_params()
        build_hbdk_params = self._get_build_hbdk_params()
        build_node_params = self._get_build_node_params()
        # build_layer_params = {'run_on_cpu': self.mp_conf.get_run_on_cpu()}
        build_output_nodes = self._get_output_nodes()
        build_debug_mode = self._get_debug_mode()
        build_params = {
            'march': self.mp_conf.march,
            'save_model': True,  # self.need_save_model(),
            'name_prefix': self.mp_conf.output_model_file_prefix,
            'input_dict': build_input_params,
            'cali_dict': build_cal_params,
            'hbdk_dict': build_hbdk_params,
            'node_dict': build_node_params,
            "check_mode": self.mp_conf.calibration_type == "skip"
            # 'enable_int16': self.mp_conf.enable_int16,
            # 'layer_dict': build_layer_params,
        }

        if self.mp_conf.enable_int16:
            build_params["enable_int16"] = self.mp_conf.enable_int16

        if self.mp_conf.calibration_optimization:
            build_params[
                'optimization'] = self.mp_conf.calibration_optimization

        if len(build_output_nodes) != 0:
            build_params['output_nodes'] = build_output_nodes

        if build_debug_mode:
            build_params['debug_mode'] = build_debug_mode

        self._debug_build_param_log(build_params)
        # Start to call build_caffe
        with CStdOutHook(logging, sys.stdout, True) as stdhook:  # noqa
            if self.model_type == 'caffe':
                try:
                    hybrid_model = build_caffe(
                        prototxt_file=self.mp_conf.caffe_prototxt,
                        caffemodel_file=self.mp_conf.caffe_model,
                        **build_params)
                except Exception as e:
                    if "ERROR-OCCUR-DURING" in str(e):
                        raise ValueError(str(e))

                    raise ValueError(
                        "*** ERROR-OCCUR-DURING {horizon_nn.build_caffe} ***,"
                        + f" error message: {str(e)}")
            elif self.model_type == 'onnx':
                try:
                    hybrid_model = build_onnx(
                        onnx_file=self.mp_conf.onnx_model, **build_params)
                except Exception as e:
                    if "ERROR-OCCUR-DURING" in str(e):
                        raise ValueError(str(e))

                    raise ValueError(
                        "*** ERROR-OCCUR-DURING {horizon_nn.build_onnx} ***," +
                        f" error message: {str(e)}")
            else:
                raise ValueError(f"wrong model type {self.model_type}")

        self.post_check(hybrid_model)

        # Convert hybrid model to runtime bin file
        logging.info("start convert to *.bin file....")
        input_names = []
        input_type_rts = {}
        input_type_rts_info = []
        input_space_and_range = []
        input_type_trains = []
        input_layout_train = []
        input_layout_rt = []
        norm_types = []
        scale_value = []
        mean_value = []
        input_shapes = []
        input_batches = []
        cal_dir = []
        for name in self.mp_conf.input_names:
            input_names.append(name)
            input_index = self._get_index_from_name(name)
            input_type_rts_info.append(self.mp_conf.input_type_rt[input_index])
            input_type_rts.update(
                {name: self.mp_conf.input_type_rt[input_index]})
            if self.mp_conf.input_space_and_range:
                input_space_and_range.append(
                    self.mp_conf.input_space_and_range[input_index])
            input_type_trains.append(
                self.mp_conf.input_type_train[input_index])
            input_layout_train.append(
                self.mp_conf.input_layout_train[input_index])
            input_layout_rt.append(self.mp_conf.input_layout_rt[input_index])

            norm_types.append(self.mp_conf.norm_type[input_index])
            scale_item = ""
            if self.mp_conf.norm_type[input_index] in [
                    'data_scale', 'mean_file_and_scale', 'data_mean_and_scale'
            ]:
                for item in self.mp_conf.scale_value[input_index]:
                    scale_item += str(item) + ','
            scale_value.append(scale_item)
            mean_item = ""
            if self.mp_conf.norm_type[input_index] in [
                    'mean_file', 'data_mean', 'mean_file_and_scale',
                    'data_mean_and_scale'
            ]:
                for item in self.mp_conf.mean_value[input_index]:
                    mean_item += str(item) + ','
            mean_value.append(mean_item)
            input_shape = self.mp_conf.input_shapes[input_index]
            input_shapes.append("x".join(str(e) for e in input_shape))
            if self.mp_conf.input_batches:
                input_batch = self.mp_conf.input_batches[0]
                input_batches.append(input_batch)
            if self.mp_conf.calibration_type in mapper_consts.autoq_caltype_list:  # noqa
                cal_dir.append(self.mp_conf.cal_data_dir[input_index])
        model_deps_info = {}
        model_deps_info["hb_mapper_version"] = version
        try:
            cp = subprocess.run("hbdk-cc --version",
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                timeout=10)
            hbdk_runtime_version = cp.stdout.decode('UTF-8').split(
                '\n')[1].split(":")[-1]
            # -------------------------------------
            model_deps_info["hbdk_version"] = hbdk_version
            model_deps_info["hbdk_runtime_version"] = hbdk_runtime_version
            model_deps_info["horizon_nn_version"] = horizon_nn_version
            # -------------------------------------
            if self.mp_conf.model_type == 'caffe':
                model_deps_info["caffe_model"] = self.mp_conf.caffe_model
                model_deps_info["prototxt"] = self.mp_conf.caffe_prototxt
            else:
                model_deps_info["onnx_model"] = self.mp_conf.onnx_model
            model_deps_info["march"] = self.mp_conf.march
            model_deps_info["layer_out_dump"] = self.mp_conf.layer_out_dump
            model_deps_info["log_level"] = logging.getLevelName(
                self.mp_conf.log_level)
            model_deps_info["working_dir"] = self.mp_conf.working_dir
            model_deps_info[
                "model_prefix"] = self.mp_conf.output_model_file_prefix
            if self.mp_conf.output_nodes:
                model_deps_info["output_nodes"] = self.mp_conf.output_nodes
            if self.mp_conf.remove_node_type:
                model_deps_info[
                    "remove_node_type"] = self.mp_conf.remove_node_type
            if self.mp_conf.remove_node_name:
                model_deps_info[
                    "remove_node_name"] = self.mp_conf.remove_node_name

            if self.mp_conf.set_node_data_type:
                model_deps_info[
                    "set_node_data_type"] = self.mp_conf.set_node_data_type

            if self.mp_conf.node_info:
                model_deps_info["node_info"] = self.mp_conf.node_info

            if self.mp_conf.model_debug_mode:
                model_deps_info["debug_mode"] = self.mp_conf.model_debug_mode
            # -------------------------------------
            model_deps_info["input_names"] = input_names
            model_deps_info["input_type_rt"] = input_type_rts_info
            model_deps_info["input_space_and_range"] = input_space_and_range
            model_deps_info["input_type_train"] = input_type_trains
            model_deps_info["input_layout_rt"] = input_layout_rt
            model_deps_info["input_layout_train"] = input_layout_train
            model_deps_info["norm_type"] = norm_types
            model_deps_info["scale_value"] = scale_value
            model_deps_info["mean_value"] = mean_value
            model_deps_info["input_shape"] = input_shapes
            model_deps_info["input_batch"] = input_batches
            # -------------------------------------
            if self.mp_conf.custom_op:
                model_deps_info[
                    "custom_op_method"] = self.mp_conf.custom_op_method
                model_deps_info["custom_op_dir"] = self.mp_conf.custom_op_dir
                model_deps_info[
                    "op_register_files"] = self.mp_conf.cop_register_files
            # -------------------------------------
            model_deps_info["cal_dir"] = cal_dir
            if self.mp_conf.cal_data_type:
                model_deps_info["cal_data_type"] = self.mp_conf.cal_data_type
            model_deps_info["preprocess_on"] = self.mp_conf.preprocess_on
            model_deps_info["calibration_type"] = self.mp_conf.calibration_type

            model_deps_info["per_channel"] = str(self.mp_conf.per_channel)
            if self.mp_conf.max_percentile:
                model_deps_info["max_percentile"] = self.mp_conf.max_percentile
            if self.mp_conf.calibration_optimization:
                model_deps_info[
                    "optimization"] = self.mp_conf.calibration_optimization
            if self.mp_conf.run_on_cpu:
                model_deps_info["run_on_cpu"] = self.mp_conf.run_on_cpu
            if self.mp_conf.run_on_bpu:
                model_deps_info["run_on_bpu"] = self.mp_conf.run_on_bpu
            if self.mp_conf.enable_int16:
                model_deps_info["enable_int16"] = self.mp_conf.enable_int16
            # -------------------------------------
            model_deps_info["hbdk_params"] = build_hbdk_params
            model_deps_info["debug"] = self.mp_conf.compile_debug_mode
            model_deps_info["compile_mode"] = self.mp_conf.compile_mode
        except Exception as e:
            logging.warning("model info gather error: " + str(e) +
                            ", will skip loading deps info")
        # add modelname to profiler log to distinguish model

        hybrid_model.graph.name = self.mp_conf.output_model_file_prefix

        file_name = self.mp_conf.output_model_file_prefix + ".bin"
        try:
            build_runtime_model_wrapper(hybrid_model, file_name,
                                        input_type_rts, input_layout_rt,
                                        model_deps_info)
        except Exception as e:
            raise ValueError(
                "*** ERROR-OCCUR-DURING {runtime.runtime_model_generation} ***"
                + f", error message: {str(e)}")

        if self.mp_conf.remove_node_type:
            cmd_option = ""
            for node_type in self.mp_conf.remove_node_type:
                cmd_option += f" -a {node_type} "
            if self.mp_conf.calibration_optimization:
                if 'run_fast' in self.mp_conf.calibration_optimization:
                    cmd_option += " --ignore-order true "
            ret = os.system(
                f"hb_model_modifier {file_name} {cmd_option} -o {file_name}")
            if ret:
                raise ValueError(
                    "delete node failed. please check your remove_node_type " +
                    f"input: {self.mp_conf.remove_node_type} is valid, " +
                    f"Expected input: {mapper_consts.removal_list}")
        if self.mp_conf.remove_node_name:
            cmd_option = ""
            for node_name in self.mp_conf.remove_node_name:
                cmd_option += f" -r {node_name} "

            ret = os.system(
                f"hb_model_modifier {file_name} {cmd_option} -o {file_name}")
            if ret:
                raise ValueError("delete node failed. "
                                 "please check your remove_node_name input: "
                                 f"{self.mp_conf.remove_node_name} is valid")

        logging.info("Convert to runtime bin file successfully!")
        logging.info("End Model Convert")


def makertbin_imp(config, model_type, version) -> None:
    runner = MakertbinRunner(config, model_type)
    workspace = os.getcwd()
    runner.run(version)
    os.chdir(workspace)
