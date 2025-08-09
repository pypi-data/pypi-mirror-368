# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import logging

import click
import onnx
import onnx.onnx_pb as onnx_pb2
from onnx.helper import make_node

import horizon_tc_ui.version as hb_mapper_version
from horizon_tc_ui.utils import tool_utils


def add_input_transpose(model, transpose_type):
    if transpose_type == "hwc2chw":
        logging.info("NHWC to NCHW transpose node will be added for input 0")
        input_info = model.graph.input[0]
        trans_name = f"transposed_{input_info.name}"
        transpose_node = make_node("Transpose",
                                   name="transpose_node_" + input_info.name +
                                   "2nchw",
                                   inputs=[trans_name],
                                   outputs=[input_info.name])

        node_attribute = transpose_node.attribute.add()
        node_attribute.name = 'perm'
        node_attribute.type = onnx_pb2.AttributeProto.INTS
        node_attribute.ints.append(0)
        node_attribute.ints.append(3)
        node_attribute.ints.append(1)
        node_attribute.ints.append(2)

        model.graph.node.insert(0, transpose_node)

        # 在graph input 中用trans_name 取代原输入节点
        input_info.name = trans_name
        tmp_lst = [
            input_info.type.tensor_type.shape.dim[2],
            input_info.type.tensor_type.shape.dim[3],
            input_info.type.tensor_type.shape.dim[1]
        ]

        input_info.type.tensor_type.shape.dim.remove(
            input_info.type.tensor_type.shape.dim[1])
        input_info.type.tensor_type.shape.dim.remove(
            input_info.type.tensor_type.shape.dim[1])
        input_info.type.tensor_type.shape.dim.remove(
            input_info.type.tensor_type.shape.dim[1])
        input_info.type.tensor_type.shape.dim.append(tmp_lst[0])
        input_info.type.tensor_type.shape.dim.append(tmp_lst[1])
        input_info.type.tensor_type.shape.dim.append(tmp_lst[2])
    elif transpose_type == "chw2hwc":
        logging.info("NCHW to NHWC transpose node will be added for input 0")
        input_info = model.graph.input[0]
        trans_name = f"transposed_{input_info.name}"
        transpose_node = make_node("Transpose",
                                   name="transpose_node_" + input_info.name +
                                   "2nhwc",
                                   inputs=[trans_name],
                                   outputs=[input_info.name])

        node_attribute = transpose_node.attribute.add()
        node_attribute.name = 'perm'
        node_attribute.type = onnx_pb2.AttributeProto.INTS
        node_attribute.ints.append(0)
        node_attribute.ints.append(2)
        node_attribute.ints.append(3)
        node_attribute.ints.append(1)

        model.graph.node.insert(0, transpose_node)

        # 在graph input 中用trans_name 取代原输入节点
        input_info.name = trans_name
        tmp_lst = [
            input_info.type.tensor_type.shape.dim[3],
            input_info.type.tensor_type.shape.dim[1],
            input_info.type.tensor_type.shape.dim[2]
        ]

        input_info.type.tensor_type.shape.dim.remove(
            input_info.type.tensor_type.shape.dim[1])
        input_info.type.tensor_type.shape.dim.remove(
            input_info.type.tensor_type.shape.dim[1])
        input_info.type.tensor_type.shape.dim.remove(
            input_info.type.tensor_type.shape.dim[1])
        input_info.type.tensor_type.shape.dim.append(tmp_lst[0])
        input_info.type.tensor_type.shape.dim.append(tmp_lst[1])
        input_info.type.tensor_type.shape.dim.append(tmp_lst[2])
    else:
        raise ValueError(
            f"transpose_type '{transpose_type}' is not supported for now ")


def log_model_info(onnx_model):
    logging.debug("*******************************\n\n")

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
    logging.debug(f"========= graph info: {onnx_graph.name} end ========")


@click.command(help='''
A Tool used to get the deps info and compile info
''')
@click.version_option(version=hb_mapper_version.__version__)
@tool_utils.on_exception_exit
@click.option('-a',
              '--action',
              type=click.Choice(['add', 'remove'], case_sensitive=False),
              required=True,
              help='Action done to the onnx model')
@click.option('-p',
              '--position',
              type=click.Choice(['input', 'output'], case_sensitive=False),
              required=True,
              help='Whether modify the input or output')
@click.option('-t',
              '--transpose',
              type=click.Choice(
                  ['hwc2chw', 'chw2hwc', 'nhwc2nchw', 'nchw2nhwc'],
                  case_sensitive=False),
              required=True,
              help='what kind of transpose op to be performed')
@click.argument('onnx_model', type=str)
def cmd_main(onnx_model, action, position, transpose):
    tool_utils.init_root_logger("onnx_layout_util")
    logging.info(f"onnx_model: {onnx_model}")
    model = onnx.load(onnx_model)
    log_model_info(model)

    if action == "add" and position == "input" and transpose.lower() in [
            'hwc2chw', 'chw2hwc', 'nhwc2nchw', 'nchw2nhwc'
    ]:
        add_input_transpose(model, transpose.lower())
    else:
        raise ValueError(f"action {action}, position {position}, "
                         f"transpose {transpose} not supported yet")

    logging.debug(
        f"model.graph.node after modification: \n {model.graph.node}")

    onnx.save(
        model,
        f"{onnx_model.split('.')[0]}_modified.{onnx_model.split('.')[1]}")
    logging.info(
        f"{onnx_model.split('.')[0]}_modified.{onnx_model.split('.')[1]} saved"
    )


if __name__ == '__main__':
    cmd_main()
