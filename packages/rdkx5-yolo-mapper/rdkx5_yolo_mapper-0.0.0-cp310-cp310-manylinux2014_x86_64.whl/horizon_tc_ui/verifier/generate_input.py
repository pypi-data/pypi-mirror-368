# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.
import logging

import numpy as np

from horizon_tc_ui.utils.data import Data
from horizon_tc_ui.utils.model_utils import ModelInfo
from horizon_tc_ui.hb_binruntime import HbBinRuntime


def save_input_file(prefix: str, input_name: str, input_data: np.ndarray,
                    output_dir: str) -> None:
    input_image_name = output_dir + f"/{prefix}_input_{input_name}.bin"
    input_data.tofile(input_image_name)


def get_model_info(model: str) -> dict:
    model_obj = ModelInfo(model)
    base_info_dict = model_obj.get_base_info_for_verifier()
    for input_name, input_shape in model_obj.get_input_shapes().items():
        base_info_dict[input_name]['input_shape'] = input_shape

    return base_info_dict


def get_input_data_by_model(output_dir: str, bin_models: list,
                            onnx_models: list, raw_input_data: dict) -> dict:
    input_data_dict = {}

    _base_info = {}
    _bin_input_data = {}
    input_sources = {}
    for bin_model in bin_models:
        model_info_dict = get_model_info(bin_model)
        input_sources = HbBinRuntime(bin_model=bin_model).get_input_source()
        for input_name, base_dict in model_info_dict.items():
            logging.info(f"bin model input {input_name} "
                         f"shape: {base_dict['input_shape']}")
            data = Data(march=base_dict["march"],
                        input_type_rt=base_dict["input_type_rt"],
                        input_layout_rt=base_dict["input_layout_rt"],
                        input_batch=base_dict["input_batch"],
                        input_name=input_name,
                        input_shape=base_dict["input_shape"],
                        image=raw_input_data[input_name],
                        input_source=input_sources[input_name])
            input_data = data.get_input_data_for_bin()
            logging.info(
                f"bin input {input_name} data shape: {input_data.shape}"
            )  # noqa

            _bin_input_data[input_name] = input_data
            save_input_file('bin', input_name, input_data, output_dir)

        input_data_dict[bin_model] = _bin_input_data
        _base_info = model_info_dict

    for onnx_model in onnx_models:
        model_info_dict = get_model_info(onnx_model)

        _onnx_input_data = {}
        for input_name, base_dict in model_info_dict.items():
            input_shape = base_dict["input_shape"]
            if _base_info:
                base_dict = _base_info[input_name]

            march = base_dict["march"]
            input_type_rt = base_dict["input_type_rt"]
            input_layout_rt = base_dict["input_layout_rt"]
            input_batch = base_dict["input_batch"]

            if _bin_input_data:
                image = _bin_input_data[input_name]
            else:
                image = raw_input_data[input_name]
            logging.info(f"onnx input {input_name} shape: {input_shape}")

            data = Data(march=march,
                        input_type_rt=input_type_rt,
                        input_layout_rt=input_layout_rt,
                        input_batch=input_batch,
                        input_name=input_name,
                        input_shape=input_shape,
                        image=image,
                        input_source=input_sources[input_name])
            input_data = data.get_input_date_for_onnx()
            logging.info(
                f"onnx input {input_name} data shape: {input_data.shape}")
            _onnx_input_data[input_name] = input_data
            save_input_file('onnx', input_name, input_data, output_dir)

        input_data_dict[onnx_model] = _onnx_input_data

    return input_data_dict
