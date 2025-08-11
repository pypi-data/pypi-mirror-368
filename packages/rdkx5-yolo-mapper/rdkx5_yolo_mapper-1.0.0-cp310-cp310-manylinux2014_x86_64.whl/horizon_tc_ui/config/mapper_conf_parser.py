# Copyright (c) 2022 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import os
import copy
import logging
import re
import yaml
from schema import Schema, Optional, Use, And, Or

from horizon_tc_ui.config import mapper_consts as mconsts
from horizon_tc_ui.parser.onnx_parser import OnnxModel
from horizon_tc_ui.parser.caffe_parser import CaffeProto
from horizon_tc_ui.utils.tool_utils import get_list_from_txt, \
    get_item_from_string

conf_schema_dict = {
    'model_parameters': {
        Optional('onnx_model'): str,
        Optional('caffe_model'): str,
        Optional('prototxt'): str,
        Optional('march'): str,  # required
        Optional('log_level'): str,
        Optional('layer_out_dump', default=False): bool,
        Optional('working_dir', default='./model_output'): str,
        Optional('output_model_file_prefix', default='model'): str,
        Optional('output_nodes'): str,
        Optional('remove_node_type'): str,
        Optional('remove_node_name'): str,
        Optional('set_node_data_type'): Or(str, dict),
        Optional('debug_mode'): Or(str, dict),
        Optional('node_info'): Or(str, dict),
    },
    'input_parameters': {
        Optional('input_name'): Use(str),
        Optional('input_type_rt'): str,  # required
        Optional('input_space_and_range'): Use(str),
        Optional('input_layout_rt'): Use(str),
        Optional('input_type_train'): str,  # required
        Optional('input_layout_train'): str,  # required
        Optional('norm_type'): Use(str),
        Optional('input_shape'): Use(str),
        Optional('input_batch'): Use(str),
        Optional('mean_value'): Use(str),
        Optional('scale_value'): Use(str),
    },
    Optional('custom_op'): {
        Optional("op_register_files"): str,
        Optional("custom_op_method"): str,
        Optional("custom_op_dir"): str,
    },
    Optional('calibration_parameters', default={}): {
        Optional('cal_data_dir'): And(str, len),
        Optional('calibration_type'): str,
        Optional('preprocess_on'): bool,
        Optional('per_channel'): bool,
        Optional('max_percentile'): Use(float),
        Optional('run_on_cpu'): Use(str),
        Optional('run_on_bpu'): Use(str),
        Optional('enable_int16'): bool,
        Optional('optimization'): str,
        Optional('cal_data_type'): str,
    },
    Optional('compiler_parameters', default={}): {
        Optional('compile_mode'): str,
        Optional('balance_factor'): int,
        Optional('debug'): bool,
        Optional('optimize_level'): str,
        Optional("ability_entry"): str,
        Optional("core_num"): int,
        Optional("max_time_per_fc"): int,
        Optional("jobs"): int,
        Optional('input_source'): Or(str, dict),
        Optional('advice'): int,
    },
}


class MpConf:
    """This class will parse hb_mapper yaml config
    and check whether the content is correct,
    """
    def __init__(self, yaml_file, model_type="") -> None:
        self._yaml_file = os.path.abspath(yaml_file)
        self._mp_conf = {}
        self.model = None
        self.input_num = -1
        self.model_type = model_type
        with open(self._yaml_file, 'r', encoding='UTF-8') as f:
            self._mp_conf = yaml.safe_load(f)

        self._validate_parameters()

    def _validate_parameters(self):
        schema_dict = copy.deepcopy(conf_schema_dict)
        self._mp_conf = Schema(schema_dict).validate(self._mp_conf)

        # --------- validate model_parameters -------------------------------
        try:
            logging.debug("validating model_parameters...")
            self._validate_model_file()
            self._validate_march()
            self._validate_working_dir()
            self._validate_output_model_file_prefix()
            self._validate_output_nodes()
            self._validate_remove_node_type()
            self._validate_remove_node_name()
            self._validate_model_debug_mode()
            self._validate_node_info()
        except Exception as e:
            logging.error("Parse 'model_parameters' failed!")
            raise e
        else:
            logging.debug("validating model_parameters finished")

        # --------- validate input_parameters -------------------------------
        try:
            logging.debug("validating input_parameters...")
            self._validate_input_name()
            self._validate_input_shape()
            self._validate_fast_perf()
            self._validate_input_batch()
            self._validate_input_type_and_layout()
            self._validate_norm_type()
            self._validate_odd_shape()
        except Exception as e:
            logging.error("Parse 'input_parameters' failed!")
            raise e
        else:
            logging.debug("validating input_parameters finished")

        # --------- validate calibration_parameters --------------------------
        try:
            logging.debug("validating calibration_parameters...")
            self._validate_calibration_type()
            self._validate_calibration_optimization()
            self._validate_cal_data_dir()
            self._validate_cal_data_type()
            self._validate_cal_data_dir_and_cal_data_type()

            self._validate_per_channel()
            self._validate_max_percentile()
            self._validate_run_on_cpu()
            self._validate_run_on_bpu()
            self._validate_enable_int16()
        except Exception as e:
            logging.error("Parse 'calibration_parameters' failed!")
            raise e
        else:
            logging.debug("validating calibration_parameters finished")

        # --------- validate custom_op -------------------------------
        try:
            logging.debug("validating custom_op...")
            self._validate_custom_op()
        except Exception as e:
            logging.error("Parse 'custom_op' failed!")
            raise e
        else:
            logging.debug("validating custom_op finished")
        # --------- validate compiler_parameters -----------------------------
        try:
            logging.debug("validating compiler_parameters...")
            self._validate_optimize_level()
            self._validate_input_source()
            self._validate_compile_debug_mode()
            self._validate_ability_entry()
            self._validate_core_num()
            self._validate_compile_mode()
            self._validate_balance_factor()
            self._validate_max_time_per_fc()
            self._validate_jobs()
            self._validate_advice()
        except Exception as e:
            logging.error("Parse 'compiler_parameters' failed!")
            raise e
        else:
            logging.debug("validating compiler_parameters finished")

        # --------- validate deprecated parameters ---------------------------
        try:
            logging.debug("validating deprecated parameters...")
            self._validate_deprecated_params()
        except Exception as e:
            logging.error("Parse 'deprecated parameters' failed!")
            raise e
        else:
            logging.debug("validating deprecated parameters finished")

    # --------- validate model_parameters -------------------------------
    """
    1) check model type from yaml.
    2) check if model file exist and valid.
    """

    def _validate_model_file(self):
        if self.model_type == 'caffe':
            if not self._mp_conf['model_parameters'].get("caffe_model"):
                raise ValueError(
                    "model type is caffe but can not find caffe_model "
                    "in config yaml, "
                    "please check 'caffe_model' in model_parameters")
        elif self.model_type == 'onnx':
            if not self._mp_conf['model_parameters'].get("onnx_model"):
                raise ValueError(
                    "model type is onnx but can not find onnx_model "
                    "in config yaml, "
                    "please check 'onnx_model' in model_parameters")
        elif self._mp_conf['model_parameters'].get("caffe_model"):
            self.model_type = 'caffe'
        elif self._mp_conf['model_parameters'].get("onnx_model"):
            self.model_type = 'onnx'
        else:
            raise ValueError(
                "Missing model file input. "
                "Please input caffe_model or onnx_model in yaml config file")
        if self.model_type == "caffe":
            self.caffe_model = self._get_abspath(
                self._mp_conf['model_parameters']['caffe_model'])
            if not self.caffe_model.endswith(".caffemodel"):
                raise ValueError(
                    f"Caffe model file invalid: '{self.caffe_model}' . "
                    f"It should be a '.caffemodel' file")
            if not os.path.isfile(self.caffe_model):
                raise ValueError(
                    f"Can not find caffemodel file given: {self.caffe_model}, "
                    f"please check 'caffe_model' in model_parameters")

            self.caffe_prototxt = self._get_abspath(
                self._mp_conf['model_parameters']['prototxt'])
            if not self.caffe_prototxt.endswith(".prototxt"):
                raise ValueError(
                    f"Caffe prototxt file invalid: '{self.caffe_prototxt}' . "
                    f"It should be a '.prototxt' file")
            if not os.path.isfile(self.caffe_prototxt):
                raise ValueError(
                    f"Can not find caffe prototxt file given: "
                    f"{self.caffe_prototxt}, "
                    f"please check 'prototxt' in model_parameters")

            logging.info(f"Using caffe model file: {self.caffe_model} "
                         f"and prototxt file: {self.caffe_prototxt}")
            self.model = CaffeProto(self.caffe_prototxt)
        if self.model_type == "onnx":
            self.onnx_model = self._get_abspath(
                self._mp_conf['model_parameters']['onnx_model'])
            if not self.onnx_model.endswith(".onnx"):
                raise ValueError(f"Onnx file invalid: '{self.onnx_model}' . "
                                 f"It should be a '.onnx' file")
            if not os.path.isfile(self.onnx_model):
                raise ValueError(
                    f"Can not find onnx_model file given: {self.onnx_model}, "
                    "please check 'onnx_model' in model_parameters")

            logging.info(f"Using onnx model file: {self.onnx_model}")
            self.model = OnnxModel(self.onnx_model)

        self.input_num = self.model.input_num()
        logging.info(
            f"Model has {self.input_num} inputs according to model file")

    """
    march is short for micro archetecture.
    """

    def _validate_march(self):
        self.march = self._mp_conf['model_parameters']['march']
        if self.march not in mconsts.march_list:
            raise ValueError(f"User input march invalid: '{self.march}' . "
                             f"It should in list {mconsts.march_list}")

    """
    working_dir is the folder that all the generated
    files(original float, optimized float, quantized models) saved.
    """

    def _validate_working_dir(self):
        self.working_dir = self._get_abspath(
            self._mp_conf['model_parameters'].get('working_dir',
                                                  './model_output'))
        if not os.path.exists(self.working_dir):
            logging.info("working_dir does not exist. "
                         f"Creating working_dir: {self.working_dir}")
            os.makedirs(self.working_dir, exist_ok=True)

    """
    output_model_file_prefix is the prefix for all the generated models.
    """

    def _validate_output_model_file_prefix(self):

        self.output_model_file_prefix_full = self.working_dir + "/" + \
                                             self._mp_conf[
                                                 'model_parameters'][
                                                 'output_model_file_prefix']
        self.output_model_file_prefix = self._mp_conf['model_parameters'][
            'output_model_file_prefix']

    """
    output_nodes will modify the model.
    It will add the listed nodes as model
    output and remove the original model output.
    """

    def _validate_output_nodes(self):
        self.output_nodes = get_list_from_txt(
            self._mp_conf['model_parameters'].get("output_nodes"))

    """
    remove_node_type will modify the bin model.
    It will remove the certain type of nodes in the generated bin model.
    """

    def _validate_remove_node_type(self):
        self.remove_node_type = get_list_from_txt(
            self._mp_conf['model_parameters'].get("remove_node_type"))

    """
    remove_node_name will modify the bin model.
    It will remove the certain nodes in the generated bin model by name.
    """

    def _validate_remove_node_name(self):
        self.remove_node_name = get_list_from_txt(
            self._mp_conf['model_parameters'].get("remove_node_name"))

    def __get_node_dict_by_str(self, param_value: str):
        _dict = {}
        value_list = []
        if ";" in param_value:
            value_list += param_value.split(';')
        else:
            value_list.append(param_value)

        for value in value_list:
            if not value:
                continue
            if ":" not in value or len(param_value.split(':')) != 2:
                raise ValueError(f"The format you gave is {param_value}, "
                                 "currently we only support "
                                 "Conv_0:int16;Conv_1:int16")

            node_name, data_type = param_value.split(':')
            if data_type.strip() not in mconsts.node_data_type_list:
                raise ValueError("Currently only support is "
                                 f"{mconsts.node_data_type_list}")

            _dict[node_name.strip()] = {"OutputType": data_type.strip()}

        return _dict

    def __get_node_dict_by_dict(self, param_value: dict):
        for node, value_dict in param_value.items():
            if not isinstance(value_dict, dict):
                raise ValueError(
                    f"The format you gave is {value_dict}"
                    f"({type(value_dict)}), currently we only support "
                    "{Conv_0:{'InputType0':'int16','OutputType':'int16'}}")

            for key, value in value_dict.items():
                if key not in ["ON", "OutputType", "InputType"] and \
                        not re.search(r'^InputType\d+$', key):
                    raise ValueError(
                        f"The format you gave is {key},"
                        "currently we only support ON、OutputType and "
                        r"InputType\d+")

                if key == "ON" and value not in mconsts.run_on_list:
                    raise ValueError("Currently only support is "
                                     f"{mconsts.run_on_list}")
                if key != "ON" and \
                        value.strip() not in mconsts.node_data_type_list:
                    raise ValueError("Currently only support is "
                                     f"{mconsts.node_data_type_list}")
        return param_value

    def __get_node_dict(self, node_dict: dict, param_value: str or dict):
        _dict = {}
        if isinstance(param_value, str):
            _dict = self.__get_node_dict_by_str(param_value)

        if isinstance(param_value, dict):
            _dict = self.__get_node_dict_by_dict(param_value)

        if _dict:
            for key, value in _dict.items():
                if key in node_dict:
                    node_dict[key].update(value)
                else:
                    node_dict[key] = value

        return node_dict

    def _validate_node_info(self):
        self.node_dict = {}

        self.set_node_data_type = \
            self._mp_conf['model_parameters'].get("set_node_data_type")
        if self.set_node_data_type:
            self.node_dict = self.__get_node_dict(self.node_dict,
                                                  self.set_node_data_type)

        self.node_info = self._mp_conf['model_parameters'].get("node_info")
        if self.node_info:
            self.node_dict = self.__get_node_dict(self.node_dict,
                                                  self.node_info)

        if self.set_node_data_type and self.node_info:
            logging.warning(
                "You configured both parameter set_node_data_type "
                "and parameter node_info. "
                "We will use the configuration of parameter node_info "
                "as the highest priority")

        if self.march != "bernoulli2" and get_list_from_txt(
            self._mp_conf['calibration_parameters'].get('run_on_cpu')) \
                and self.node_info:
            logging.warning(
                "You configured both parameter run_on_cpu "
                "and parameter node_info. "
                "We will use the configuration of parameter node_info "
                "as the highest priority")

        if self.march != "bernoulli2" and get_list_from_txt(
            self._mp_conf['calibration_parameters'].get('run_on_bpu')) \
                and self.node_info:
            logging.warning(
                "You configured both parameter run_on_bpu "
                "and parameter node_info. "
                "We will use the configuration of parameter node_info "
                "as the highest priority")

        logging.debug("node_dict: {self.node_dict}")

    """
    debug_mode dumps some things that are needed for debugging.
    """

    def _validate_model_debug_mode(self):
        self.model_debug_mode = \
            self._mp_conf['model_parameters'].get("debug_mode")

        if self.model_debug_mode and \
                self.model_debug_mode not in mconsts.model_debug_mode_list:
            raise ValueError(
                f"User input debug_mode invalid: '{self.model_debug_mode}'. "
                f"It should in list {mconsts.model_debug_mode_list}")

    # --------- validate input_parameters -------------------------------
    """
    input_name is the input name of the model.
    It can be omitted if there is only one input in the model,
    but is required when there are multiple inputs
    so that the following input param (input type, layout etc.)
    sequence will match.
    """

    def _validate_input_name(self) -> None:
        model_input_names = self.model.get_input_names()
        yaml_input_names = get_list_from_txt(
            self._mp_conf['input_parameters'].get('input_name'))

        if yaml_input_names:
            if len(yaml_input_names) != len(model_input_names):
                raise ValueError(
                    f"Wrong num of input names received. "
                    f"Num of input name given: {len(yaml_input_names)}, "
                    f"while model file has {len(model_input_names)} inputs")
            if len(yaml_input_names) != len(set(yaml_input_names)):
                raise ValueError(
                    f"Input names duplicated: '{yaml_input_names}' ")

            for name in yaml_input_names:
                if name not in model_input_names:
                    raise ValueError(
                        f"Input name does not exist in model file: {name}. "
                        f"name list: {model_input_names}")
            self.input_names = yaml_input_names

        else:
            if len(model_input_names) > 1:
                raise ValueError(
                    "Model has more than one input! "
                    "It is required to explicitly give input names "
                    "to ensure sequence is correct.")
            self.input_names = model_input_names
            logging.info(
                "Model name not given in yaml_file, "
                f"using model name from model file: {model_input_names}")

    """
    input_shape is the input shape of the model. It can be omitted.
    It the user input shape is different from the one parsed from the model,
    then it will use the user input as the final shape and throw a warning.
    """

    def _validate_input_shape(self):
        yaml_input_shape_txt = get_list_from_txt(
            self._mp_conf['input_parameters'].get('input_shape'))
        model_file_shape = [
            self.model.get_input_shape(name) for name in self.input_names
        ]

        if yaml_input_shape_txt and len(
                yaml_input_shape_txt) != self.input_num:
            raise ValueError(
                f"Num of input shape given: {len(yaml_input_shape_txt)}, "
                f"while model file has {self.input_num} inputs")

        if yaml_input_shape_txt:
            self.input_shapes = []
            try:
                for _, shape_item in enumerate(yaml_input_shape_txt):
                    self.input_shapes.append(
                        list(map(int,
                                 shape_item.strip().lower().split('x'))))
            except Exception:
                raise ValueError("Input shape parse failed. "
                                 f"Input: {shape_item}")

        else:
            for origin_input_shape in model_file_shape:
                for dim_value in origin_input_shape:
                    if int(dim_value) == 0:
                        raise ValueError("The input_shape "
                                         f"{origin_input_shape} of the model "
                                         "is a dynamic shape. "
                                         "Please configure the 'input_shape' "
                                         "option in 'input_parameters'")
            self.input_shapes = model_file_shape
            logging.info("Model input shape not given in yaml_file, "
                         f"using shape from model file: {model_file_shape}")
        for index, shape_item in enumerate(self.input_shapes):
            if len(shape_item) != 4:
                logging.info(
                    f"Input shape {shape_item} has length: {len(shape_item)}, "
                    "make sure it is a featuremap input")
            if self.input_shapes[index] != model_file_shape[index]:
                logging.warning(
                    f"For input {index}: user input shape: "
                    f"{self.input_shapes[index]} is different "
                    f"from model file input shape: {model_file_shape[index]}. "
                    "Using user input info")

    """
    input_batch is the input batch of the model. It can be omitted it is 1.
    Note bernoulli2, bayes and bayes-e has different batch range
    only applicable to single-input models and the first dimension
    of input_shape must be 1.
    """

    def _validate_input_batch(self) -> None:
        """
        validate input_batch parameter
        """
        self.input_batches = get_list_from_txt(
            self._mp_conf['input_parameters'].get('input_batch'))
        if not self.input_batches:
            return None
        if len(self.input_batches) != 1:
            raise ValueError("input_batch option can only receive one input. "
                             f"There are {len(self.input_batches)} given")
        for idx, input_shape in enumerate(self.input_shapes):
            if input_shape[0] != 1:
                raise ValueError(
                    "'input_batch' option in 'input_parameters' is configured."
                    " This option only works when model has the "
                    "first dimensional of its input must be 1. "
                    f"Current model has input_shape: {self.input_shapes}")
        for input_index, input_batch_item in enumerate(self.input_batches):
            if self.march == "bernoulli2" and (int(input_batch_item) <= 0
                                               or int(input_batch_item) > 128):
                raise ValueError("Input_batch value should between 1 and 128, "
                                 f"got {int(input_batch_item)}")
            if self.march in [
                    "bayes", "bayes-e"
            ] and (int(input_batch_item) <= 0 or int(input_batch_item) > 4096):
                raise ValueError(
                    "Input_batch value should between 1 and 4096, "
                    f"got {int(input_batch_item)}")
            input_shape_item = self.input_shapes[input_index]
            if input_shape_item[0] != 1 and \
                    input_shape_item[0] != input_batch_item:
                logging.warning(f"For input {input_index}: "
                                "Model shape and input batch conflict. "
                                "Model shape indicates input batch is "
                                f"{input_shape_item[0]} and input_batch is "
                                f"{input_batch_item}. Using input_batch "
                                f"{input_batch_item} as final batch num input")

    """
    input_type_train is the type the data that the original model
    was trained with.
    input_layut_train is the layout the original model was trained with.
    Usually NCHW for pytorch model and NHWC for tensorflow model.
    input_type_rt is the type of the data that feeds to the generated model.
    input_layout_rt is the layout of the data that feeds
    to the generated model.
    """

    def _validate_input_type_and_layout(self):
        # parse input type rt
        self.input_type_rt = get_list_from_txt(
            self._mp_conf['input_parameters'].get('input_type_rt'))
        if len(self.input_type_rt) != self.input_num:
            raise ValueError(
                "Wrong num of input_type_rt received. "
                f"num of input_type_rt given: {len(self.input_type_rt)}, "
                f"expect: {self.input_num}")
        for rt_type_item in self.input_type_rt:
            if rt_type_item not in mconsts.input_type_rt_list:
                raise ValueError(
                    "Invalid input_type_rt received. "
                    f"input type rt: '{rt_type_item}' should in list "
                    f"{mconsts.input_type_rt_open_list}")
        # parse input layout rt
        self.input_layout_rt = get_list_from_txt(
            self._mp_conf['input_parameters'].get('input_layout_rt'))
        if self.input_layout_rt and len(
                self.input_layout_rt) != self.input_num:
            raise ValueError(
                "Wrong num of input_layout_rt received. "
                "num of input_layout_rt given: "
                f"{len(self.input_layout_rt)}, expect: {self.input_num}")
        for rt_layout_item in self.input_layout_rt:
            if rt_layout_item not in mconsts.layout_list:
                raise ValueError("Invalid input_layout_rt received. "
                                 f"input layout rt: '{rt_layout_item}' "
                                 f"should in list {mconsts.layout_list}")
        if not self.input_layout_rt:
            for input_index, input_type_item in enumerate(self.input_type_rt):
                if input_type_item == "nv12":
                    self.input_layout_rt.append("")
                    logging.info("nv12 input type rt received.")
                else:
                    raise ValueError(
                        "Input_layout_rt missing. "
                        f"input {input_index} input_type_rt is: "
                        f"{input_type_item}. "
                        "input_layout_rt is required for this type")
        self.input_layout_rt = [item.upper() for item in self.input_layout_rt]

        # parse input type train
        self.input_type_train = get_list_from_txt(
            self._mp_conf['input_parameters'].get('input_type_train'))
        if len(self.input_type_train) != self.input_num:
            raise ValueError(
                "Wrong num of input_type_train received. "
                "num of input_type_train given: "
                f"{len(self.input_type_train)}, expect: {self.input_num}")
        for train_type_item in self.input_type_train:
            if train_type_item not in mconsts.input_type_train_list:
                raise ValueError(
                    "Invalid input_type_train received. "
                    f"input type train: '{train_type_item}' "
                    f"should in list {mconsts.input_type_train_open_list}")
        # parse input layout train
        self.input_layout_train = get_list_from_txt(
            self._mp_conf['input_parameters'].get('input_layout_train'))

        if not self.input_layout_train:
            raise ValueError(
                "Input_layout_train missing. "
                "Please add'input_layout_train' in 'input_parameters' section")

        if self.input_layout_train and len(
                self.input_layout_train) != self.input_num:
            raise ValueError(
                "Wrong num of input_layout_train received. "
                "Num of input_layout_train given: "
                f"{len(self.input_layout_train)}, expect: {self.input_num}")
        for train_layout_item in self.input_layout_train:
            if train_layout_item not in mconsts.layout_list:
                raise ValueError("Invalid input_layout_train received. "
                                 f"Input layout train: '{train_layout_item}' "
                                 f"should in list {mconsts.layout_list}")
        self.input_layout_train = [
            item.upper() for item in self.input_layout_train
        ]
        # parse input space and range
        self.input_space_and_range = get_list_from_txt(
            self._mp_conf['input_parameters'].get('input_space_and_range'))
        if self.input_space_and_range and len(
                self.input_space_and_range) != self.input_num:
            raise ValueError(
                "Wrong num of input_space_and_range received. "
                "num of input_space_and_range given: "
                f"{len(self.input_space_and_range)}, expect: {self.input_num}")

        if not self.input_space_and_range:
            self.input_space_and_range = ["regular"] * self.input_num
        for input_index, input_space_and_range_item in enumerate(
                self.input_space_and_range):
            if input_space_and_range_item not in mconsts.input_space_and_range:
                raise ValueError(
                    "Invalid input_space_and_range received. "
                    "User input 'input_space_and_range': "
                    f"'{input_space_and_range_item}' invalid. "
                    f"It should in list {mconsts.input_space_and_range}")
            if input_space_and_range_item == "bt601_video" and \
                    self.input_type_rt[
                        input_index] != "nv12":
                raise ValueError(
                    "Input_type_rt and input_space_and_range "
                    "combination invalid. "
                    f"input_space_and_range: {input_space_and_range_item} "
                    f"and input_type_rt {self.input_type_rt[input_index]}")

        # check input_type_rt
        for index, type_rt_item in enumerate(self.input_type_rt):
            # nv12 data don't need layout info
            if type_rt_item == "nv12" and \
                    self.input_layout_rt[index]:
                logging.warning(
                    "Nv12 input layout info received. "
                    f"input type rt '{index}' is nv12 and layout "
                    f"'{self.input_layout_rt[index]}' is not needed.")

        # validate layout and type combo
        for input_index in range(self.input_num):
            train_type = self.input_type_train[input_index]
            rt_type = self.input_type_rt[input_index]
            train_layout = self.input_layout_train[input_index]
            rt_layout = self.input_layout_rt[input_index]
            space_and_range = self.input_space_and_range[input_index]
            input_shape = self.input_shapes[input_index]

            if rt_type == 'nv12' and space_and_range == "bt601_video":
                rt_type = "yuv420sp_bt601_video"
                self.input_type_rt[input_index] = "yuv420sp_bt601_video"

            if train_type in ["rgb", "bgr", "yuv444"]:
                if (train_layout == "NHWC"
                        and input_shape[3] != 3) or (train_layout == "NCHW"
                                                     and input_shape[1] != 3):
                    if (train_layout == "NHWC" and input_shape[1] == 3):
                        logging.error(
                            f"Input {input_index} has input_type_train "
                            f"{train_type} "
                            f"and input_layout_train {train_layout} "
                            f"but conflict with shape {input_shape}")
                        raise ValueError(
                            "Input_layout_train says NHWC "
                            "but seems like layout of input_shape is NCHW: "
                            f"{input_shape}, "
                            "try use NCHW in input_layout_train")

                    if (train_layout == "NCHW" and input_shape[3] == 3):
                        logging.error(
                            f"Input {input_index} has input_type_train "
                            f"{train_type} "
                            f"and input_layout_train {train_layout} "
                            f"but conflict with shape {input_shape}")
                        raise ValueError(
                            "Input_layout_train says NCHW "
                            "but seems like layout of input_shape is NHWC: "
                            f"{input_shape}, "
                            f"try use NHWC in input_layout_train")
                    raise ValueError(
                        f"Input_type_train {train_type} input_layout_train "
                        f"{train_layout} and input_shape "
                        f"{input_shape} "
                        "does not seem right. Please double check.")

            if train_type in ["gray"]:
                if (train_layout == "NHWC"
                        and input_shape[3] != 1) or (train_layout == "NCHW"
                                                     and input_shape[1] != 1):
                    if (train_layout == "NHWC" and input_shape[1] == 1):
                        logging.error(
                            f"Input {input_index} has input_type_train "
                            f"{train_type} and input_layout_train "
                            f"{train_layout} "
                            f"but conflict with shape {input_shape}")
                        raise ValueError(
                            "Input_layout_train says NHWC "
                            "but seems like layout of input_shape is NCHW: "
                            f"{input_shape}, "
                            "try use NCHW in input_layout_train")

                    if (train_layout == "NCHW" and input_shape[3] == 1):
                        logging.error(
                            f"Input {input_index} has input_type_train "
                            f"{train_type} and input_layout_train "
                            f"{train_layout} "
                            "but conflict with shape {input_shape}")
                        raise ValueError(
                            "Input_layout_train says NCHW "
                            "but seems like layout of input_shape is NHWC: "
                            f"{input_shape}, "
                            "try use NHWC in input_layout_train")
                    raise ValueError(
                        f"Input_type_train {train_type} input_layout_train "
                        f"{train_layout} and input_shape {input_shape} "
                        "does not seem right. Please double check.")

            if rt_type in [
                    "yuv444", "yuv444_128"
            ] and rt_layout == "NCHW" and self.march == "bernoulli2":
                raise ValueError(
                    f"Input {input_index} has input_type_rt {rt_type} "
                    "with input_layout_rt NCHW is not supported "
                    "on bernoulli2 for now.")

            if train_type == rt_type:
                continue
            if train_type not in mconsts.legal_trans_dict.keys(
            ) or rt_type not in mconsts.legal_trans_dict[train_type]:
                raise ValueError(
                    f"Input {input_index} has input_type_train '{train_type}' "
                    "is not supported transform to input_type_rt "
                    f"'{rt_type}' for now.")

    """
    when input_type_rt is set as nv12, then its size should be even.
    """

    def _validate_odd_shape(self):
        for index, input_type_rt in enumerate(self.input_type_rt):
            if input_type_rt == 'nv12':
                shape = self.input_shapes[index]
                if self.input_layout_train[index] == "NCHW":
                    h, w = shape[2], shape[3]
                else:
                    h, w = shape[1], shape[2]
                if h % 2 != 0 or w % 2 != 0:
                    raise ValueError(f'Invalid nv12 input shape: {shape}, '
                                     'nv12 type does not support odd size')

    """
    norm_type is the preprocess action done to the input data.
    This option will add a preprocess node to the model.
    """

    def _validate_norm_type(self):
        # parse norm type
        self.norm_type = get_list_from_txt(
            self._mp_conf['input_parameters'].get('norm_type'))
        if not self.norm_type:
            self.norm_type = ["no_preprocess"] * self.input_num
        if len(self.norm_type) != self.input_num:
            raise ValueError("Wrong norm_type num received. "
                             f"Num of norm_type given: {len(self.norm_type)} "
                             f"is not equal to input num {self.input_num}")
        # parse mean values
        mean_values = get_list_from_txt(
            self._mp_conf['input_parameters'].get('mean_value'))
        if not mean_values:
            mean_values = [None] * self.input_num
        if mean_values and len(mean_values) != self.input_num:
            raise ValueError("Wrong mean_value num received. "
                             f"input mean_value num {len(mean_values)} "
                             f"is not equal to input num {self.input_num}")
        self.mean_value = []
        # parse scale values
        scale_values = get_list_from_txt(
            self._mp_conf['input_parameters'].get('scale_value'))
        if not scale_values:
            scale_values = [None] * self.input_num
        if len(scale_values) != self.input_num:
            raise ValueError("Wrong scale_value num received. "
                             f"input scale_value num {len(scale_values)} "
                             f"is not equal to input num {self.input_num}")
        self.scale_value = []

        # parse strings to float num
        for norm_index, norm_item in enumerate(self.norm_type):
            mean_value = mean_values[norm_index]
            scale_value = scale_values[norm_index]
            if norm_item not in mconsts.norm_type_list:
                raise ValueError(
                    "Norm type given invalid: "
                    f"'{norm_item}' should in list {mconsts.norm_type_list}")
            if norm_item != 'no_preprocess' and \
               self.input_type_rt[norm_index] == 'featuremap':
                raise ValueError(
                    f"Input_type_rt {norm_index +1 } is featuremap, "
                    "this input only support norm_type no_preprocess")
            if 'mean' in norm_item:
                if not mean_value:
                    raise ValueError(
                        "Mean value not given: "
                        f"input {norm_index} norm type {self.norm_type} "
                        "require mean value input but not given ")
                try:
                    self.mean_value.append(
                        get_item_from_string(mean_value, func=float))
                except Exception:
                    raise ValueError(f"Wrong mean_value format {mean_value}, "
                                     f"please refer to user manual")
            else:
                self.mean_value.append(None)
            if 'scale' in norm_item:
                if not scale_value:
                    raise ValueError(
                        "Scale value not given: "
                        f"input {norm_index} norm type {self.norm_type} "
                        "require scale value input but not given ")
                try:
                    self.scale_value.append(
                        get_item_from_string(scale_value, func=float))
                except Exception:
                    raise ValueError(f"Wrong scale_value format {scale_value}")
            else:
                self.scale_value.append(None)

    # --------- validate calibration_parameters -------------------------------
    """
    calibration_type is the type used for quantization calibration.
    """

    def _validate_calibration_type(self):
        self.calibration_type = self._mp_conf['calibration_parameters'].get(
            'calibration_type', "default")
        if self.calibration_type not in mconsts.autoq_caltype_list and \
                self.calibration_type not in mconsts.preq_caltype_list:
            raise ValueError(
                "User input calibration_type invalid, "
                f"'{self.calibration_type}' should in list "
                f"{mconsts.autoq_caltype_list + mconsts.preq_caltype_list}")

    def _validate_calibration_optimization(self):
        """
        horizon_NN will check the legitimacy of this parameter
        """
        _calibration_optimizations = get_list_from_txt(
            self._mp_conf['calibration_parameters'].get('optimization'))
        if _calibration_optimizations:
            self.calibration_optimization = _calibration_optimizations
        else:
            self.calibration_optimization = None

    """
    cal_data_dir is the folder that the cal data is stored.
    """

    def _validate_cal_data_dir(self):
        if self.calibration_type in mconsts.preq_caltype_list:
            logging.info(
                f"Parameter calibration_type is {self.calibration_type}. "
                "cal_data_dir check skipped")
            self.cal_data_dir = []
            return

        self.cal_data_dir = get_list_from_txt(
            self._mp_conf['calibration_parameters'].get('cal_data_dir', None))
        if len(self.cal_data_dir) != self.input_num:
            raise ValueError(f"Wrong cal_dir num given, "
                             f"cal_dir num {len(self.cal_data_dir)} is "
                             f"not equal to input num {self.input_num}")

        for cal_index in range(self.input_num):
            self.cal_data_dir[cal_index] = self._get_abspath(
                self.cal_data_dir[cal_index])
            if not os.path.exists(self.cal_data_dir[cal_index]):
                raise ValueError("Cal_data_dir does not exist: "
                                 f"{self.cal_data_dir[cal_index]}")

    """
    cal_data_type is the file data type that the cal data is stored using numpy
    """

    def _validate_cal_data_type(self):
        self.cal_data_type = get_list_from_txt(
            self._mp_conf['calibration_parameters'].get('cal_data_type', None))
        if self.cal_data_type:
            if len(self.cal_data_type) != self.input_num:
                raise ValueError(
                    f"Wrong cal_data_type num given, "
                    f"cal_data_type num {len(self.cal_data_type)} is "
                    f"not equal to input num {self.input_num}")

            for cal_data_type in self.cal_data_type:
                if cal_data_type not in mconsts.cal_data_type_list:
                    raise ValueError(f"User input cal_data_type invalid, "
                                     f"'{cal_data_type}' should "
                                     f"in list {mconsts.cal_data_type_list}")

    def _validate_cal_data_dir_and_cal_data_type(self):
        if self.cal_data_dir and self.cal_data_type:
            if len(self.cal_data_dir) != len(self.cal_data_type):
                raise ValueError(
                    f"Wrong cal_dir num given, "
                    f"cal_data_dir num {len(self.cal_data_dir)} is not equal "
                    f"to cal_data_type num {len(self.cal_data_type)}")

            for i in range(len(self.cal_data_dir)):
                cal_data_dir = self.cal_data_dir[i]
                cal_data_type = self.cal_data_type[i]

                if cal_data_dir.endswith('_f32'):
                    cal_data_dir_suffix = 'float32'
                else:
                    cal_data_dir_suffix = 'uint8'

                if cal_data_type == "float32":
                    cal_data_type_suffix = 'float32'
                else:
                    cal_data_type_suffix = 'uint8'

                if cal_data_dir_suffix != cal_data_type_suffix:
                    logging.warning(
                        f"The calibration dir name suffix is not the same as "
                        f"the value {cal_data_type} "
                        f"of the parameter cal_data_type,"
                        f" the parameter setting will prevail")
                else:
                    logging.info(
                        f'The calibration dir name suffix is the '
                        f'same as the value {cal_data_type} of '
                        f'the cal_data_type parameter '
                        f'and will be read with the value of cal_data_type.')

    """
    per_channel is the calibration option for quantization.
    """

    def _validate_per_channel(self):
        self.per_channel = self._mp_conf['calibration_parameters'].get(
            'per_channel', False)

    """
    max_percentile is the max percentage option for max calibration method.
    """

    def _validate_max_percentile(self):
        self.max_percentile = self._mp_conf['calibration_parameters'].get(
            'max_percentile')
        if self.max_percentile:
            if self.max_percentile < 0 or self.max_percentile > 1:
                raise ValueError(
                    f"Invalid max_percentile: {self.max_percentile}, "
                    "avaliable range: 0~1")

    """
    run_on_cpu is the node that is forced to run on cpu
    """

    def _validate_run_on_cpu(self):
        self.run_on_cpu = get_list_from_txt(
            self._mp_conf['calibration_parameters'].get('run_on_cpu'))

    """
    run_on_bpu is the node that is forced to run on bpu
    """

    def _validate_run_on_bpu(self):
        self.run_on_bpu = get_list_from_txt(
            self._mp_conf['calibration_parameters'].get('run_on_bpu'))

    """
    enable_int16 will enable int16 output, only work on certain models on j5
    """

    def _validate_enable_int16(self):
        self.enable_int16 = self._mp_conf['calibration_parameters'].get(
            'enable_int16', None)

    # --------- validate custom op  -------------------------------
    """
    custom_op supports two methods,
    but should be change to support one method only.
    Only register method is needed. Manual input method should be deleted.
    So only op_register_files will be needed in yaml.
    other options should be removed.
    """

    def _validate_custom_op(self):
        if not self._mp_conf.get('custom_op', None):
            self.custom_op = False
            logging.info("custom_op does not exist, skipped")
            return
        self.custom_op = True
        self.custom_op_method = self._mp_conf['custom_op'].get(
            'custom_op_method', None)
        if self.custom_op_method is None:
            raise ValueError("Custom_op_method is not specified")

        if self.custom_op_method not in mconsts.custom_op_method_list:
            raise ValueError(
                f"Custom_op_method '{self.custom_op_method}' invalid, "
                f"available options: {mconsts.custom_op_method_list}")

        if (self.custom_op_method == "register"):
            self.custom_op_dir = self._mp_conf['custom_op'].get(
                'custom_op_dir', '')

            self.cop_register_files = get_list_from_txt(
                self._mp_conf['custom_op'].get('op_register_files', None))

            if self.custom_op_dir:
                if not os.path.exists(self.custom_op_dir):
                    raise ValueError(
                        f"Custom_op_dir '{self.custom_op_dir}' does not exist")

            for item in self.cop_register_files:
                if not item.endswith(".py"):
                    raise ValueError(f"File {item} is not a python file. "
                                     "Please fix its extension or remove it")
                if self.custom_op_dir:
                    if not os.path.exists(
                            self._get_abspath(f"{self.custom_op_dir}/{item}")):
                        raise ValueError(
                            f"'{item}' does not exist in {self.custom_op_dir}")
        else:
            raise ValueError("Invalid custom_op_method")

    # --------- validate compiler_parameters  -------------------------------
    """
    optimize_level is the hbdk-cc optimization option.
    """

    def _validate_optimize_level(self):
        self.optimize_level = self._mp_conf['compiler_parameters'].get(
            'optimize_level', "O0")
        if self.optimize_level not in mconsts.optimize_level:
            raise ValueError("User input optimize_level invalid, "
                             f"'{self.optimize_level}' should in list "
                             f"{mconsts.optimize_level}")

    """
    input_source is the rt model data input source.
    nv12 must come from pyramid.
    """

    def _validate_input_source(self) -> None:
        """compiler_parameters input_source verification
        """
        input_source_input = self._mp_conf['compiler_parameters'].get(
            "input_source", {})
        if not isinstance(input_source_input, dict):
            raise ValueError("Invalid input_source format received. "
                             "input_source should be a dict")
        self.input_source = {}

        for input_index, input_name in enumerate(self.input_names):
            input_type_rt = self.input_type_rt[input_index]
            input_source_item = input_source_input.get(input_name)
            # if input_source not received,
            # give default value according to input_type_rt
            if not input_source_item:
                if input_type_rt in \
                        mconsts.input_source_support_dict['pyramid']:
                    input_source_item = "pyramid"
                elif input_type_rt in mconsts.input_source_support_dict['ddr']:
                    input_source_item = "ddr"
                else:
                    raise ValueError(
                        "Invalid input_type_rt received. "
                        f"input type rt: '{input_type_rt}' should in list "
                        f"{mconsts.input_type_rt_open_list}")
                logging.warning(
                    f"Input node {input_name}'s input_source not set, "
                    f"it will be set to {input_source_item} by default")
            else:
                # if input_source received, check it if in input_source_range
                if input_source_item not in mconsts.input_source_range:
                    raise ValueError(
                        "Invalid input_source received. input_source "
                        f"{input_source_item} should in list "
                        f"{mconsts.input_source_range}")
                # if input_source right,
                # check input_type_rt if input_source is supported
                if input_type_rt not in \
                        mconsts.input_source_support_dict[input_source_item]:
                    raise ValueError(
                        "Wrong input_source received. input type rt : "
                        f"{input_type_rt} does not support "
                        f"input_source {input_source_item}")

            self.input_source[input_name] = input_source_item

        for input_name in input_source_input.keys():
            if input_name not in self.input_source:
                raise ValueError(
                    "Invalid input_source setting received, "
                    f"input name in 'input_source': '{input_name}' "
                    f"does not exist in model input names: {self.input_names}")
        self.input_source.update({'_default_value': 'ddr'})

    def _validate_compile_debug_mode(self):
        self.compile_debug_mode = self._mp_conf['compiler_parameters'].get(
            "debug", True)

    def _validate_ability_entry(self):
        self.ability_entry = self._mp_conf['compiler_parameters'].get(
            'ability_entry')

    def _validate_core_num(self):
        self.core_num = self._mp_conf['compiler_parameters'].get('core_num', 1)
        if self.core_num not in mconsts.core_num_range:
            raise ValueError(
                "Wrong core num setting given, "
                f"{self.core_num} should in range {mconsts.core_num_range}")

    def _validate_compile_mode(self):
        self.compile_mode = self._mp_conf['compiler_parameters'].get(
            'compile_mode', "latency")
        if self.compile_mode not in mconsts.compile_mode_list:
            raise ValueError(
                f"Invalid compile model received. {self.compile_mode} "
                f"is invalid, it should in list {mconsts.compile_mode_list}")

    def _validate_balance_factor(self) -> None:
        compile_mode = self._mp_conf['compiler_parameters'].get('compile_mode')
        self.balance_factor = self._mp_conf['compiler_parameters'].get(
            'balance_factor')
        if compile_mode != "balance" and self.balance_factor is None:
            return None
        if compile_mode != "balance" and self.balance_factor is not None:
            logging.warning("Parameter compile_mode is not set to balance, "
                            "balance_factor will not take effect.")
            return None
        if compile_mode == "balance" and self.balance_factor is None:
            raise ValueError("Parameter compile_mode is set to balance, "
                             "please set balance_factor to use this mode")
        if 0 > self.balance_factor or self.balance_factor > 100:
            raise ValueError(
                f"Invalid balance_factor received: {self.balance_factor}, "
                "value range is 0-100")

    """
    max_time_per_fc is the maximum function call time for this model.
    needs to be larger than 1000,
    otherwise function call time too small is not supported at hbdk side
    """

    def _validate_max_time_per_fc(self):
        self.max_time_per_fc = self._mp_conf['compiler_parameters'].get(
            'max_time_per_fc', 0)
        if self.max_time_per_fc and \
           (self.max_time_per_fc < 1000 or self.max_time_per_fc > 4294967295):
            raise ValueError("Parameter max_time_per_fc value check failed. "
                             "Please set it 0 or 1000-4294967295")

    def _validate_jobs(self):
        self.jobs = self._mp_conf['compiler_parameters'].get('jobs')

    def _validate_advice(self):
        self.advice = self._mp_conf['compiler_parameters'].get('advice')
        if self.advice and not str(self.advice).isdigit():
            raise ValueError("The parameter advice, "
                             "must be a positive integer")

    # --------- validate deprecated_parameters  -------------------------------
    """
    deprecated_parameters are the ones that no longer used and
    will be removed in the near future,
    but can not be removed now for compatibility reasons
    """

    def _validate_deprecated_params(self):
        """
        layer_out_dump enables to add an output for each conv node.
        This is only used for debug.
        """
        self.layer_out_dump = self._mp_conf['model_parameters'].get(
            'layer_out_dump', False)
        if self._mp_conf['model_parameters'].get('log_level'):
            logging.warning("User input 'log_level' is deprecated，"
                            "Console log level is set as info, "
                            "and logfile log level is set as debug.")
        self.log_level = logging.DEBUG
        self.preprocess_on = self._mp_conf['calibration_parameters'].get(
            'preprocess_on', False)
        if self.preprocess_on:
            logging.warning("User input 'preprocess_on' will be deprecated. "
                            "If you want to simplify the calibration process, "
                            "please use 'skip' in  'calibration_type' ")

    # --------- validate fast perf  -------------------------------

    @staticmethod
    def diff_dynamic_shape(before: list, after: list) -> bool:
        """
        Compare whether the difference between two Shapes in ['?', 0, -1]

        Returns:
            bool: Returns False if the modified range is not in ['?', 0, -1]
        """
        diff = list(
            map(
                lambda i: before[i] if before[i] not in ['?', 0, -1] and
                before[i] != after[i] else None, range(len(before))))
        diff = list(filter(lambda x: x is not None, diff))
        logging.debug(f'Shape diff result: {diff}')
        return len(diff) == 0

    def _validate_fast_perf(self) -> None:
        """
        validate fast perf input parameters
        """
        if self._mp_conf['calibration_parameters'].get('optimization') \
           != 'run_fast':
            return None
        model_input_names = self.model.get_input_names()
        yaml_input_names = get_list_from_txt(
            self._mp_conf['input_parameters'].get('input_name'))
        yaml_input_shapes_txt = get_list_from_txt(
            self._mp_conf['input_parameters'].get('input_shape'))
        yaml_input_shapes = []
        try:
            for shape_item in yaml_input_shapes_txt:
                yaml_input_shapes.append(
                    list(map(int,
                             str(shape_item).strip().lower().split('x'))))
        except Exception:
            raise ValueError('Failed to parse the input_shape, '
                             'please double check your input')
        model_file_shapes = [
            self.model.get_input_shape(name) for name in model_input_names
        ]

        for idx_yaml, yaml_name in enumerate(yaml_input_names):
            try:
                idx_model = model_input_names.index(yaml_name)
            except ValueError:
                raise ValueError(f'Your input name {yaml_name} '
                                 'not in model inputs')
            yaml_shape = yaml_input_shapes[idx_yaml]
            model_shape = model_file_shapes[idx_model]
            if len(yaml_shape) != len(model_shape):
                raise ValueError(
                    f'Input shape {yaml_shape} '
                    f'length not equal to model input shape {model_shape}')
            if not self.diff_dynamic_shape(model_shape, yaml_shape):
                raise ValueError(
                    f'Your input shape {yaml_shape} but model input shape is '
                    f'{model_shape}, we only supports modifying '
                    'the dim value of a dynamic batch')

    # ----------------------------------------------------------------------------

    def __getitem__(self, item):
        return self._mp_conf[item]

    def _get_abspath(self, path):
        if os.path.isabs(path):
            return path
        yaml_base_dir = os.path.dirname(self._yaml_file)
        new_path = os.path.abspath(os.path.join(yaml_base_dir, path))
        logging.debug(f"Using abs path {new_path}")
        return new_path

    def _get_layout_from_type(self, input_type):
        return ""

    def __str__(self):
        return yaml.safe_dump(self._mp_conf)

    def has(self, attr):
        return hasattr(self, attr)
