# Copyright (c) 2022 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import logging
import copy

import click

import horizon_tc_ui.version as hb_mapper_version
from horizon_tc_ui.config.mapper_conf_parser import get_list_from_txt
from horizon_tc_ui.config.mapper_consts import removal_list
from horizon_tc_ui.hbdtort import runtime_pb2
from horizon_tc_ui.utils import tool_utils
from horizon_tc_ui.utils.model_utils import (
    DataType, find_initializer_by_name, find_input, find_node, find_output,
    delete_value_info, list_to_str, model_input_connects_to_multiple_nodes,
    node_adjacent_input_or_output, keep_output_or_input,
    node_related_other_node_input_and_output, construct_json_from_node,
    InputDataType, tensor_datatype_to_input_datatype)


@click.command(help=f'''
A Tool used to modify the bin model. \n
This tool can remove {', '.join(removal_list)} nodes''')
@click.help_option('--help', '-h')
@click.version_option(version=hb_mapper_version.__version__)
@click.argument('bin_file', type=str)
@click.option('-r',
              type=str,
              default=[],
              multiple=True,
              help='remove certain nodes from bin model.')
@click.option('-o', type=str, default="", help='modified model name')
@click.option('-a',
              "--all",
              default=[],
              multiple=True,
              type=click.Choice(removal_list),
              help='node type')
@click.option('-i',
              "--ignore-order",
              type=bool,
              default=False,
              hidden=True,
              help="Ignore order or not")
@tool_utils.on_exception_exit
def cmd_main(bin_file, r, o, all, ignore_order):
    main(bin_file, r, o, all, ignore_order)


def main(bin_file, r, o, all, ignore_order=False):
    tool_utils.init_root_logger("hb_model_modifier")

    # parse parameters
    node_names = list(r)
    output_name = o.strip()
    delete_all_type = list(all)
    if ignore_order and not delete_all_type:
        delete_all_type = copy.deepcopy(removal_list)

    # validation
    if not bin_file.endswith(".bin"):
        raise ValueError(f"bin file name {bin_file} invalid")

    if output_name:
        save_name = output_name
    else:
        save_name = bin_file[:-4] + "_modified.bin"

    with open(bin_file, 'rb') as model_file:
        bin_str = model_file.read()
        bin_model = runtime_pb2.ModelProto()
        bin_model.ParseFromString(bin_str)

        # log model proto info
        log_model_info(bin_file, bin_model)
        if len(bin_model.graphs) > 1:
            raise ValueError(
                "Pack model detected. Packed model is not supported.")
        if bin_model.HasField('graph'):
            raise ValueError("Old model detected. Please use the latest tool "
                             "and compile the model again.")
    if ignore_order:
        node_dict = get_node_info(bin_model)
        for graph in bin_model.graphs:
            for input in graph.input:
                can_delete_node(node_dict, input.name, "input",
                                delete_all_type, node_names)
        for graph in bin_model.graphs:
            for output in graph.output:
                can_delete_node(node_dict, output.name, "output",
                                delete_all_type, node_names)
    else:
        if delete_all_type:
            logging.info(
                f"Tool will remove {delete_all_type} nodes from this model")
            for remove_type in delete_all_type:
                for node_item in bin_model.graphs[0].node:
                    if node_item.op_type == remove_type and \
                            node_item.name not in node_names:
                        node_names.append(node_item.name)
    if node_names:
        logging.info(
            f"Nodes that will be removed from this model: {node_names}")
        for nodename in node_names:
            _, node = find_node(bin_model.graphs[0], nodename)
            if not node:
                logging.warning(
                    f"Node {nodename} is not found in the model! Skipped!")
                continue
            if not node_adjacent_input_or_output(bin_model.graphs[0], node):
                logging.warning(
                    f"Node {nodename} is not adjacent to input or output. "
                    "It can not be removed! Skipped!")
                continue
            if node_related_other_node_input_and_output(
                    bin_model.graphs[0], node):
                logging.warning(
                    f"Node {nodename} input and output are connected to "
                    "other nodes. It can not be removed! Skipped!")
                continue
            remove_node(nodename, bin_model)
        with open(save_name, 'wb') as save_file:
            save_file.write(bin_model.SerializeToString())
        logging.info(f"modified model saved as {save_name}")
    else:
        show_nodes(bin_model)


def save_del_op_info(op_type: str, del_node, target_model) -> None:
    """add del op info in metadata_props_info"""
    input_list = list(del_node.input)
    output_list = list(del_node.output)
    if len(input_list) <= 2:
        input_list.append('')
    info_list = []
    if op_type in ["Dequantize", "DequantizeFilter"]:
        if op_type == "Dequantize":
            head_prefix = 'DN_D'
        elif op_type == "DequantizeFilter":
            head_prefix = 'DN_F'
        name_prefix = input_list[0]
        info_list.append(output_list[0])
        info_list.append(input_list[1])
        info_list.append(input_list[2])
    elif op_type == "Quantize":
        head_prefix = 'DN_Q'
        name_prefix = output_list[0]
        info_list.append(input_list[0])
        info_list.append(input_list[1])
        info_list.append(input_list[2])
    else:
        raise ValueError(
            f'Invalid op type {op_type}, only support Dequantize, '
            'DequantizeFilter and Quantize')
    target_model.metadata_props_info[0].model_info[
        f'{head_prefix}_{name_prefix}_valueinfo'] = info_list[0]
    target_model.metadata_props_info[0].model_info[
        f'{head_prefix}_{name_prefix}_scale'] = info_list[1]
    target_model.metadata_props_info[0].model_info[
        f'{head_prefix}_{name_prefix}_zeropoint'] = info_list[2]

    # add axis info
    add_axis_info = False
    for attr in del_node.attribute:
        if attr.name == 'axis':
            target_model.metadata_props_info[0].model_info[
                f'{head_prefix}_{name_prefix}_axis'] = str(attr.i)
            add_axis_info = True
    if not add_axis_info:
        logging.warning(f'node name is {del_node.name}, op type is {op_type}, '
                        'no axis information')


def remove_node(node_name, bin_model):
    runtime_graph = bin_model.graphs[0]
    target_index, target_node = find_node(runtime_graph, node_name)
    if not target_node:
        raise ValueError(f"node {node_name} not found!!!")
    if target_node.op_type not in removal_list:
        raise ValueError(
            f"node {node_name} has op type {target_node.op_type}, "
            "this tool does not support this op type!!! "
            f"Supported op type: {removal_list}")
    logging.info(f"Node '{target_node.name}' found, its OP type is "
                 f"'{target_node.op_type}'")

    input_index, model_input = find_input(runtime_graph, target_node.input[0])
    output_index, model_output = find_output(runtime_graph,
                                             target_node.output[0])

    if model_input_connects_to_multiple_nodes(runtime_graph, model_input):
        raise ValueError(
            f"Node {node_name}'s input {model_input.name} connects to "
            "more than 1 node")

    # 删除 Quantize 节点
    if target_node.op_type == "Quantize":
        save_del_op_info(op_type=target_node.op_type,
                         del_node=target_node,
                         target_model=bin_model)
        quantize_output = delete_value_info(runtime_graph,
                                            target_node.output[0])
        elem_type = quantize_output.type.elem_type
        model_input.type.elem_type = elem_type

        # convert tensor.DataType to InputType
        if runtime_graph.input_type[input_index] == InputDataType.F32.value:
            elem_type = DataType(elem_type)
            if elem_type in [DataType.INT8, DataType.UINT8, DataType.INT16]:
                runtime_graph.input_type[input_index] = \
                    tensor_datatype_to_input_datatype[elem_type].value
                rt_type_list = get_list_from_txt(
                    bin_model.metadata_props_info[0].
                    model_info["INPUT_TYPE_RT"])
                rt_type_list[input_index] = "featuremap"
                bin_model.metadata_props_info[0].model_info[
                    "INPUT_TYPE_RT"] = list_to_str(rt_type_list)
            else:
                raise ValueError(f"Invalid elem_type {elem_type} output from "
                                 "Quantize node")
        # replace_input(runtime_graph, quantize_output.name, model_input.name)

        # runtime require HBM node input name same with hbm file input name.
        # So the hbm input name need to remain and replace the bin model input.

    # 删除 Transpose 节点

    if target_node.op_type == "Transpose":
        # 试着从graph.input中找target_node的input_tensor，如果找到，将target_node的output_tensor的name和dim赋给input_tensor的name和dim,同时从graph.value_info中删除target_node的output_tensor
        if model_input:
            transpose_output = delete_value_info(runtime_graph,
                                                 target_node.output[0])

            model_input.type.dim[:] = transpose_output.type.dim[:]

            # NHWC
            if runtime_graph.input_layout[input_index] == 1:
                runtime_graph.input_layout[input_index] = 2
            # NCHW
            elif runtime_graph.input_layout[input_index] == 2:
                runtime_graph.input_layout[input_index] = 1
            else:
                raise ValueError(
                    f"runtime_graph.input_layout {input_index} "
                    f"is invald: {runtime_graph.input_layout[input_index]}")

        # 试着从graph.output中找target_node的output_tensor，如果找到，将target_node的input_tensor的name和dim赋给output_tensor的name和dim,同时从graph.value_info中删除target_node的input_tensor
        elif model_output:
            transpose_input = delete_value_info(runtime_graph,
                                                target_node.input[0])
            model_output.type.dim[:] = transpose_input.type.dim[:]

        else:
            raise ValueError(
                f"Transpose node {target_node.name} is not adjacent to "
                "input or output")

    # 删除 dequanti 及后续节点
    if target_node.op_type == "Dequantize":
        save_del_op_info(op_type=target_node.op_type,
                         del_node=target_node,
                         target_model=bin_model)
        dequantize_input = delete_value_info(runtime_graph,
                                             target_node.input[0])
        elem_type = dequantize_input.type.elem_type
        model_output.type.elem_type = elem_type

    if target_node.op_type == "DequantizeFilter":
        save_del_op_info(op_type=target_node.op_type,
                         del_node=target_node,
                         target_model=bin_model)
        for node_output in target_node.output:
            delete_value_info(runtime_graph, node_output)
        node_input = delete_value_info(runtime_graph, target_node.input[0])
        new_output = runtime_graph.output.add()
        new_output.name = node_input.name
        new_output.type.elem_type = node_input.type.elem_type
        new_output.type.dim[:] = node_input.type.dim[:]

    # 删除 Cast 节点
    if target_node.op_type == "Cast":

        if model_input:
            cast_output = delete_value_info(runtime_graph,
                                            target_node.output[0])
            model_input.type.elem_type = cast_output.type.elem_type
        elif model_output:
            cast_input = delete_value_info(runtime_graph, target_node.input[0])
            model_output.type.elem_type = cast_input.type.elem_type
        else:
            raise ValueError(
                f"Cast node {target_node.name} is not adjacent to "
                "input or output")

    # 删除 Reshape 节点
    if target_node.op_type == "Reshape":
        if model_input:
            reshape_output = delete_value_info(runtime_graph,
                                               target_node.output[0])
            model_input.type.dim[:] = reshape_output.type.dim[:]
        elif model_output:
            reshape_input = delete_value_info(runtime_graph,
                                              target_node.input[0])
            model_output.type.dim[:] = reshape_input.type.dim[:]
        else:
            raise ValueError(
                f"Reshape node {target_node.name} is not adjacent to "
                "input or output")

    # 删除 Softmax 节点
    if target_node.op_type == "Softmax":
        softmax_input = delete_value_info(runtime_graph, target_node.input[0])
        model_output.type.dim[:] = softmax_input.type.dim[:]

    if target_node.op_type != "DequantizeFilter":
        # keep model input or output name never change
        keep_output_or_input(runtime_graph, target_node)

    node_info = ""
    if target_node.op_type == "Quantize":
        init_info = find_initializer_by_name(runtime_graph.initializer,
                                             target_node.input[1])
        if len(target_node.input) >= 3:
            zero_point = target_node.input[2]
        else:
            zero_point = 0

        node_info += \
            f"{target_node.name}: scale: {str(init_info.float_data)}; " \
            "zero point: {zero_point}"
        logging.info(
            f"scale: {target_node.input[1]}; zero point: {zero_point}. "
            "node info details are stored in hb_model_modifier log file")

    elif target_node.op_type in ["Dequantize", "DequantizeFilter"]:
        init_info = find_initializer_by_name(runtime_graph.initializer,
                                             target_node.input[1])
        if len(target_node.input) >= 3:
            zero_point = target_node.input[2]
        else:
            zero_point = 0

        node_info += \
            f"{target_node.name}: scale: {str(init_info.float_data)}; " \
            "zero point: {zero_point}"
        logging.info(
            f"scale: {target_node.input[1]}; zero point: {zero_point}. "
            "node info details are stored in hb_model_modifier log file")

    elif target_node.op_type == "Transpose":
        node_info += target_node.name + ": " + str(
            target_node.attribute[0].ints)
    elif target_node.op_type == "Cast":
        node_info += target_node.name + ": " + str(target_node.attribute)
    elif target_node.op_type == "Reshape":
        node_info += target_node.name + ": " + str(target_node.attribute)
    elif target_node.op_type == "Softmax":
        node_info += target_node.name + ": " + str(target_node.attribute)
    else:
        raise ValueError(f"invalid op type {target_node.op_type}")

    bin_model.metadata_props_info[0].model_info[
        "DELETED_NODES"] = bin_model.metadata_props_info[0].model_info.get(
            "DELETED_NODES", "") + node_name + " "

    deleted_info = bin_model.metadata_props_info[0].model_info.get(
        "DELETED_NODE_INFO", "")
    bin_model.metadata_props_info[0].model_info[
        "DELETED_NODE_INFO"] = construct_json_from_node(
            target_node, deleted_info)

    if model_input:
        bin_model.metadata_props_info[0].model_info[
            f"DN_M_{model_input.name}"] = target_node.output[0]

    if model_output:
        bin_model.metadata_props_info[0].model_info[
            f"DN_M_{model_output.name}"] = target_node.input[0]

    bin_model.metadata_props_info[0].model_info["NODE_" +
                                                node_name] = node_info

    logging.debug(f"Node {node_name} info: '{node_info}'")
    del runtime_graph.node[target_index]
    logging.info(f"Node '{node_name}' is removed")


def log_model_info(bin_file, bin_model):
    logging.debug(f"storing info of model: {bin_file}")
    runtime_graph = bin_model.graphs[0]

    logging.debug("--------input----------")
    for item in runtime_graph.input:
        logging.debug(item)
    logging.debug("--------output----------")
    for item in runtime_graph.output:
        logging.debug(item)
    logging.debug("--------value_info----------")
    for item in runtime_graph.value_info:
        logging.debug(item)
    logging.debug("--------node----------")
    for item in runtime_graph.node:
        logging.debug(item)
    logging.debug("--------input_type----------")
    for item in runtime_graph.input_type:
        logging.debug(item)
    logging.debug("--------input_layout----------")
    for item in runtime_graph.input_layout:
        logging.debug(item)


def show_nodes(bin_model):
    runtime_graph = bin_model.graphs[0]
    res_list = []
    for item in runtime_graph.node:
        if item.op_type not in removal_list:
            continue
        if not node_adjacent_input_or_output(runtime_graph, item):
            continue
        if node_related_other_node_input_and_output(runtime_graph, item):
            continue
        res_list.append(item.name)
    if res_list:
        logging.info(f"Nodes that can be deleted: {res_list}")
    else:
        logging.info("No nodes available")


def set_node_dict(node, name_list, node_dict):
    for name in name_list:
        if name in node_dict:
            node_list = list(node_dict[name])
            node_list.append(node)
            node_dict[name] = node_list
        else:
            node_dict[name] = [node]


def get_node_info(bin_model) -> dict:
    node_dict = {'input': {}, 'output': {}}

    for graph in bin_model.graphs:
        for node in graph.node:
            input_name_list = node.input
            set_node_dict(node, input_name_list, node_dict['input'])

            output_name_list = node.output
            set_node_dict(node, output_name_list, node_dict['output'])

    return node_dict


def can_delete_node(node_info_dict, node_name, mode, delete_all_type,
                    can_delete_node_name):
    node_dict = node_info_dict[mode]
    node_list = node_dict.get(node_name, [])

    for node in node_list:
        if node.op_type in delete_all_type:
            can_delete_node_name.append(node.name)
            if mode == 'input':
                for output in node.output:
                    can_delete_node(node_info_dict, output, mode,
                                    delete_all_type, can_delete_node_name)
            else:
                for input in node.input:
                    can_delete_node(node_info_dict, input, mode,
                                    delete_all_type, can_delete_node_name)
