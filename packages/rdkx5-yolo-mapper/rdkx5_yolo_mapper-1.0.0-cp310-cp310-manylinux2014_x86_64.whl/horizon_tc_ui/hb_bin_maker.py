#  Copyright (c) 2021 Horizon Robotics.All Rights Reserved.
#  #
#  The material in this file is confidential and contains trade secrets
#  of Horizon Robotics Inc. This is proprietary information owned by
#  Horizon Robotics Inc. No part of this work may be disclosed,
#  reproduced, copied, transmitted, or used in any way for any purpose,
#  without the express written permission of Horizon Robotics Inc.

import os
import click
import logging

import onnx
from horizon_tc_ui.version import __version__
from horizon_tc_ui.hbdtort.onnx2horizonrt import build_runtime_model_wrapper
from horizon_tc_ui.utils.tool_utils import on_exception_exit, init_root_logger
from horizon_tc_ui.config.mapper_consts import input_type_rt_list, layout_list
from horizon_tc_ui.config.mapper_consts import march_list


@click.command()
@click.help_option('--help', '-h')
@click.version_option(version=__version__)
@click.argument('onnx_model_path', type=str)
@click.option('--bin_file_name', '-b', type=str, help='Saved bin model name.')
@click.option('--march',
              '-m',
              type=click.Choice(march_list),
              required=True,
              help='Micro arch')
@click.option('--input_name_and_type_and_layout',
              '-n',
              type=(str, str, str),
              required=True,
              multiple=True,
              help='Input name and type.')
@click.option('--output_layout', type=str, hidden=True)
@on_exception_exit
def cmd_main(onnx_model_path, bin_file_name, march,
             input_name_and_type_and_layout, output_layout):
    """
    Example: hb_bin_maker xx.onnx -n data yuv444 NHWC  -m bayes
    """
    cmd_wrapper(onnx_model_path, bin_file_name, march,
                input_name_and_type_and_layout, output_layout)


def cmd_wrapper(onnx_model_path, bin_file_name, march,
                input_name_and_type_and_layout, output_layout):
    init_root_logger('hb_bin_maker', logging.INFO)
    logging.debug(f"onnx_model_path: {onnx_model_path}")
    logging.debug(f"bin_file_name: {bin_file_name}")
    logging.debug(f"march: {march}")
    logging.debug(
        f"input_name_and_type_and_layout: {input_name_and_type_and_layout}")
    logging.debug(f"output_layout: {output_layout}")

    logging.info("start convert to *.bin file....")

    onnx_model = onnx.load(onnx_model_path)
    if not bin_file_name:
        filename = os.path.basename(onnx_model_path)
        bin_file_name = filename.split(".")[0] + ".bin"
        logging.debug(f"bin_file_name generated: {bin_file_name}")

    input_type_rts = {}
    input_layout_rt = []
    for name, input_type, input_layout in input_name_and_type_and_layout:
        if input_type not in input_type_rt_list:
            raise ValueError(f"Invalid input type: {input_type}")
        input_layout = input_layout.upper()
        if input_layout not in layout_list:
            raise ValueError(f"Invalid input layout: {input_layout}")
        input_type_rts.update({name: input_type})
        input_layout_rt.append(input_layout)

    model_deps_info = {}
    model_deps_info["hb_mapper_version"] = __version__
    model_deps_info["march"] = march

    build_runtime_model_wrapper(onnx_model=onnx_model,
                                rt_bin_file=bin_file_name,
                                input_type=input_type_rts,
                                input_layout_rt=input_layout_rt,
                                model_deps_info=model_deps_info,
                                output_layout=output_layout)
