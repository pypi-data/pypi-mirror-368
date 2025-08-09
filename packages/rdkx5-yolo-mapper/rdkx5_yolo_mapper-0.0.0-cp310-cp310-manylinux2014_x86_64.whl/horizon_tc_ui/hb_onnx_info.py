# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import logging
import os

import click
import onnx

import horizon_tc_ui.version as hb_mapper_version
from horizon_tc_ui.utils import tool_utils


def log_model_info(onnx_model):
    logging.debug("*******************************")
    logging.debug("======== model basic info start ========")
    logging.debug(f"ir_version: {onnx_model.ir_version}")
    logging.debug(f"opset_import: {onnx_model.opset_import}")
    logging.debug(f"producer_name: {onnx_model.producer_name}")
    logging.debug(f"producer_version: {onnx_model.producer_version}")
    logging.debug(f"domain: {onnx_model.domain}")
    logging.debug(f"model_version: {onnx_model.model_version}")
    logging.debug(f"doc_string: {onnx_model.doc_string}")
    logging.debug("======== model basic info end ========")
    onnx_graph = onnx_model.graph
    logging.debug(f"======== graph info: {onnx_graph.name} start ========")

    logging.debug("--------input----------")
    for item in onnx_graph.input:
        logging.debug(item)

    logging.debug("--------output----------")
    for item in onnx_graph.output:
        logging.debug(item)

    logging.debug("--------node----------")
    for item in onnx_graph.node:
        logging.debug(item)

    logging.debug("--------value_info----------")
    for item in onnx_graph.value_info:
        logging.debug(item)

    logging.debug("--------initializer----------")
    for item in onnx_graph.initializer:
        logging.debug(f"name: {item.name}")
        logging.debug(f"type: {item.data_type}")
        logging.debug(f"shape: {item.dims}")

    logging.debug("--------doc string-----------")
    logging.debug(f"doc string: {onnx_model.doc_string}")

    logging.debug("--------graph doc string-----------")
    logging.debug(f"doc string: {onnx_graph.doc_string}")

    logging.debug(f"========= graph info: {onnx_graph.name} end ========")


@click.command(help='''
A Tool used to get the deps info and compile info
''')
@click.help_option('--help', '-h')
@click.version_option(version=hb_mapper_version.__version__)
@tool_utils.on_exception_exit
@click.argument('onnx_model', type=str)
def cmd_main(onnx_model):
    filename = os.path.basename(onnx_model).split(".")[0]
    tool_utils.init_root_logger(filename)

    logging.info("Start hb_onnx_info....")
    logging.info(f"hb_onnx_info version {hb_mapper_version.__version__}\n\n")
    logging.info(f"onnx_model path: {onnx_model}")

    model = onnx.load(onnx_model)
    log_model_info(model)


if __name__ == '__main__':
    cmd_main()
