# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import sys
import logging
import click
import subprocess
from pathlib import Path

from hbdk import __version__ as hbdk_version
from horizon_nn.api import version as horizon_nn_version
from horizon_nn.api import build_caffe, build_onnx

from horizon_tc_ui.version import __version__
from horizon_tc_ui.parser.caffe_parser import CaffeProto
from horizon_tc_ui.parser.onnx_parser import OnnxModel
from horizon_tc_ui.hbdtort.onnx2horizonrt import build_runtime_model_wrapper
from horizon_tc_ui.utils.tool_utils import (CStdOutHook, init_root_logger,
                                            parse_input_shape_str)
from horizon_tc_ui.config.mapper_consts import march_list


@click.command()
@click.help_option('--help', '-h')
@click.version_option(version=__version__)
@click.argument('modelname', type=click.Path(exists=True))
@click.option('-p', '--proto', type=str, help='caffe prototxt file')
@click.option('--march',
              type=click.Choice(march_list),
              default='bernoulli2',
              help='microchip architecture')
@click.option('-i',
              '--input_shape',
              type=(str, str),
              default=[],
              multiple=True,
              help="""
    input model_inputname and model_input_shape. model_input_shape should be
    seperated by "x", e.g. "input1 1x3x224x224"
    """)
@click.option('--optimization_level',
              type=click.Choice(['O0', 'O1', 'O2', 'O3']),
              default='O0',
              help='model compilation optimization level')
def cmd_main(modelname, proto, march, input_shape, optimization_level):
    """hb_checker is an quick offline model check tool
    provided by horizon."""
    logging.info("Start hb_checker....")
    init_root_logger("hb_mapper_checker", file_level=logging.DEBUG)
    logging.info("hbdk version %s" % hbdk_version)
    cp = subprocess.run("hbdk-cc --version",
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=10)
    hbdk_runtime_version = cp.stdout.decode('UTF-8').split('\n')[1].split(
        ":")[-1]
    logging.info("hbdk runtime version %s" % hbdk_runtime_version)
    logging.info("horizon_nn version %s" % horizon_nn_version)
    logging.info("hb_mapper version %s" % __version__)

    if modelname.endswith(".onnx"):
        model_type = "onnx"
        model = OnnxModel(modelname)
    elif modelname.endswith(".caffemodel"):
        model_type = "caffe"
        model = CaffeProto(proto)
    else:
        raise ValueError(
            f"Only Onnx/Caffe are supported. Invalid {modelname} given")

    addtional_param = {}
    if input_shape:
        user_input_shapes = {}
        user_input_names = []
        for input_name, input_shape_txt in input_shape:
            user_input_shapes[input_name] = parse_input_shape_str(
                input_shape_txt)
            user_input_names.append(input_name)
        addtional_param['input_dict'] = _get_input_dict(
            model, user_input_names, user_input_shapes)
    addtional_param["check_mode"] = True
    if optimization_level != 'O0':
        addtional_param['optimization_level'] = optimization_level
    hb_checker_output_path = "hb_checker_output"
    Path(hb_checker_output_path).mkdir(parents=True, exist_ok=True)

    with CStdOutHook(logging, sys.stdout, True) as stdhook:  # noqa F841
        if model_type == "caffe":
            hybrid_model = build_caffe(
                prototxt_file=proto,
                caffemodel_file=modelname,
                march=march,
                name_prefix=f"./{hb_checker_output_path}/",
                save_model=True,
                **addtional_param)
        elif model_type == "onnx":
            hybrid_model = build_onnx(
                onnx_file=modelname,
                march=march,
                name_prefix=f"./{hb_checker_output_path}/",
                save_model=True,
                **addtional_param)
    file_name = f"./{hb_checker_output_path}/checker.bin"
    input_type_rt_dict = {}
    input_type_rt_list = []
    input_layout_rt_list = []
    model_shapes_list = []
    norm_types_list = []
    cal_data_dir_list = []

    for name in model.get_input_names():
        input_type_rt_dict.update({name: "yuv444"})
        input_type_rt_list.append("yuv444")
        input_layout_rt_list.append("NHWC")
        model_shapes_list.append(model.get_input_shape(name))
        norm_types_list.append("no_preprocess")
        cal_data_dir_list.append("N/A")

    build_runtime_model_wrapper(
        hybrid_model, file_name, input_type_rt_dict, input_layout_rt_list, {
            "hb_mapper_version": __version__,
            "hbdk_version": hbdk_version,
            "hbdk_runtime_version": hbdk_runtime_version,
            "horizon_nn_version": horizon_nn_version,
            "march": march,
            "input_names": model.get_input_names(),
            "input_type_rt": input_type_rt_list,
            "input_layout_rt": input_layout_rt_list,
            "input_type_train": input_type_rt_list,
            "input_layout_train": input_layout_rt_list,
            "input_shape": model_shapes_list,
            "norm_type": norm_types_list,
            "cal_dir": cal_data_dir_list,
        })
    logging.info("End model checking....")


def _get_input_dict(model, user_input_names, user_input_shapes) -> dict:
    model_input_name = model.get_input_names()
    # check input model name validity
    for name in user_input_names:
        if name not in model_input_name:
            message = 'wrong input name: %s, available: %s' % (
                name, model_input_name)
            raise ValueError(message)
    input_dict = {}
    for input_name, input_shape in user_input_shapes.items():
        input_shape_model = model.get_input_dims(input_name)
        # check user input_shape and model_input_shape to see if same
        if input_shape != input_shape_model:
            logging.warning(
                f"for input {input_name}, user input_shape: {input_shape} "
                f"is not same with model input_shape: {input_shape_model}")
        input_dict[input_name] = {'input_batch': int(input_shape[0])}
        input_shape[0] = 1
        input_dict[input_name].update({'input_shape': input_shape})

    return input_dict


if __name__ == '__main__':
    sys.exit(cmd_main())
