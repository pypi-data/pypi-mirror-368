# Copyright (c) 2023 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import os
import yaml
import shutil
import logging
from schema import Schema
from horizon_tc_ui import __file__ as tc_ui_root_file
from horizon_tc_ui.parser.caffe_parser import CaffeProto
from horizon_tc_ui.parser.onnx_parser import OnnxModel
from horizon_tc_ui.config.mapper_conf_parser import conf_schema_dict


class YamlBuilder:
    def __init__(self, mode: str, proto: str, model: str, model_type: str,
                 march: str, input_shape: tuple) -> None:
        if mode not in ['fast_perf']:
            raise ValueError("mode only supports fast_perf")

        self.mode = mode
        self.proto_path = proto
        self.model_path = model
        self.model_type = model_type
        self.march = march
        self.input_shape = input_shape
        tc_ui_path = os.path.abspath(os.path.dirname(tc_ui_root_file))
        self.template_path = os.path.join(tc_ui_path, 'config/')
        self.workspace = os.path.join(os.getcwd(), '.' + self.mode)
        self.model = None
        self.config = None
        self.model_name = None
        self.yaml_path = None
        self.input_num = None
        self.model_input_shapes = []

        self.validate()
        return None

    def validate(self) -> None:
        if not self.model_type:
            raise ValueError(
                'model_type only supports onnx/caffe, please check the param')
        if self.model_type == 'caffe' and not self.proto_path:
            raise ValueError('model type is caffe but proto file missing')
        return None

    def get_template_config(self) -> None:
        fast_perf_template_path = os.path.join(self.template_path,
                                               f"{self.mode}_template.yaml")
        with open(fast_perf_template_path, 'r') as stream:
            self.config = yaml.safe_load(stream)
        logging.debug(self.config)
        logging.info(f"{self.mode} template yaml load success")
        return None

    def prepare_env(self) -> None:
        model_file_name = os.path.basename(self.model_path)
        self.model_name = os.path.splitext(model_file_name)[0]
        self.yaml_path = os.path.join(self.workspace,
                                      f'{self.model_name}_config.yaml')
        if os.path.exists(self.workspace):
            shutil.rmtree(self.workspace)
        os.makedirs(self.workspace, exist_ok=True)

    def model_parser(self) -> None:
        if self.model_type == 'onnx':
            self.model = OnnxModel(model_file=self.model_path)
        else:
            self.model = CaffeProto(prototxt=self.proto_path)

        self.input_names = self.model.get_input_names()
        self.input_num = len(self.input_names)
        return None

    def update_params(self) -> None:
        self.get_template_config()
        self.update_model_params()
        self.update_input_name_and_shape()

        if self.mode == "fast_perf":
            self.update_params_of_fast_perf()

        return None

    def update_model_params(self) -> None:
        cwd = os.getcwd()
        model_abs_path = os.path.join(cwd, self.model_path)
        model_params = self.config["model_parameters"]
        if self.model_type == "caffe":
            proto_abs_path = os.path.join(cwd, self.proto_path)
            model_params["caffe_model"] = model_abs_path
            model_params["prototxt"] = proto_abs_path
        if self.model_type == "onnx":
            model_params["onnx_model"] = model_abs_path
        model_params["march"] = self.march
        model_params["output_model_file_prefix"] = self.model_name
        model_params["working_dir"] = os.path.join(cwd, "model_output")
        self.config["model_parameters"].update(model_params)
        return None

    def update_input_name_and_shape(self) -> None:
        input_params = self.config["input_parameters"]
        input_params["input_name"] = ';'.join(self.input_names)
        input_shapes = []
        for name in self.input_names:
            shape = 'x'.join(map(str, self.model.get_input_shape(name)))
            input_shapes.append(shape)
            self.model_input_shapes.append(shape)
        input_params["input_shape"] = ';'.join(input_shapes)

        if not self.input_shape:
            self.config["input_parameters"].update(input_params)
            return None

        input_name = input_params["input_name"].split(';')
        input_shape = input_params["input_shape"].split(';')
        for name, shape in self.input_shape:
            if name not in input_name:
                raise ValueError(f'Your input name {name} '
                                 'not in model inputs, '
                                 'please double check your input')
            idx = input_name.index(name)
            input_shape[idx] = shape
        input_params["input_name"] = ';'.join(input_name)
        input_params["input_shape"] = ';'.join(input_shape)
        self.config["input_parameters"].update(input_params)
        return None

    def update_params_of_fast_perf(self) -> None:
        input_type_rt = ['featuremap'] * self.input_num
        input_type_train = ['featuremap'] * self.input_num
        input_layout_train = ['NCHW'] * self.input_num
        for idx, input_name in enumerate(self.input_names):
            shape = self.model.get_input_shape(input_name)
            # Data is not four-dimensional or channel dimension is not 3
            if len(shape) != 4 or (shape[1] != 3 and shape[3] != 3):
                continue
            # NCHW, NHWC
            h_idx, w_idx, c_idx = (2, 3, 1) if shape[1] == 3 else (1, 2, 3)
            if shape[h_idx] % 2 != 0 or shape[w_idx] % 2 != 0:
                continue

            input_type_rt[idx] = "nv12"
            input_type_train[idx] = "bgr"
            input_layout_train[idx] = "NCHW" if c_idx == 1 else "NHWC"

        input_params = self.config["input_parameters"]
        input_params["input_type_rt"] = ';'.join(input_type_rt)
        input_params["input_type_train"] = ';'.join(input_type_train)
        # To be consistent with the original layout, do not do Transpose
        input_params["input_layout_rt"] = ';'.join(input_layout_train)
        input_params["input_layout_train"] = ';'.join(input_layout_train)

        norm_type = ';'.join(['no_preprocess'] * self.input_num)
        input_params["norm_type"] = norm_type
        self.config["input_parameters"].update(input_params)
        # check input_shape
        parsed_shapes = [
            input_shape.split('x') for input_shape in
            self.config["input_parameters"]['input_shape'].split(';')
        ]
        parsed_names = self.config["input_parameters"]['input_name'].split(';')
        for idx_shape, current_shape in enumerate(parsed_shapes):
            for idx_dim, dim_value in enumerate(current_shape):
                if dim_value in ['?', '-1', '0']:
                    if idx_dim == 0:
                        logging.warning(
                            f'The input {parsed_names[idx_shape]} has '
                            'dynamic input_shape, the first dim of the '
                            f'{self.model_input_shapes[idx_shape]} '
                            'will be set to 1')
                        parsed_shapes[idx_shape][idx_dim] = '1'
                    else:
                        raise ValueError(
                            f'The input {parsed_names[idx_shape]} '
                            'has the dynamic input_shape '
                            f'{self.model_input_shapes[idx_shape]} but the '
                            'dynamic batch dim is not the first dim, '
                            'please configure the input_shape option '
                            'and specify all the dynamic dims of this input')
        self.config["input_parameters"]['input_shape'] = ';'.join(
            ["x".join(input_shape) for input_shape in parsed_shapes])
        return None

    def dump(self) -> None:
        logging.info(f"Updated yaml config info: {self.config}")
        validated_config = Schema(conf_schema_dict).validate(self.config)
        with open(self.yaml_path, 'w') as f:
            yaml.safe_dump(validated_config, f)
        return self.yaml_path

    def build(self) -> str:
        self.prepare_env()
        self.model_parser()
        self.update_params()
        return self.dump()
