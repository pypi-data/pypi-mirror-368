# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

from horizon_tc_ui.hbdtort import runtime_pb2

# 不可修改该定义，如果非要修改，必须和horizonRT协定统一好
HORIZONRT_FUSED_QUANTIZE_ATTR_NAME = 'horizonrt_fused_quantize_scale_list'
# 不可修改该定义，如果非要修改，必须和horizonRT协定统一好
HORIZONRT_FUSED_OUTPUT_FORMAT_ATTR_NAME = 'horizonrt_fused_output_data_format_list'
# 不可修改该定义，如果非要修改，必须和horizonRT协定统一好
HORIZONRT_FUSED_COPY_OP_NAME = 'HorizonrtFusedCopy'


def construct_node2index(runtime_graph):
    node2index = {}
    for node_index in range(len(runtime_graph.node)):
        node2index[runtime_graph.node[node_index].name] = node_index
    return node2index


def construct_output2consumers(runtime_graph):
    output2consumers = {}
    for value_info in runtime_graph.value_info:
        for node in runtime_graph.node:
            if value_info.name in node.input:
                output2consumers.setdefault(value_info.name,
                                            []).append(node.name)
    return output2consumers


def update_node2index(node_index, node2index):
    for node, index in node2index.items():
        if index > node_index:
            node2index[node] = node2index[node] - 1


def fuse_bpu_input(runtime_graph, node2index, output2consumers):
    i = 0
    del_value_infos = []

    def get_graph_input(node):
        graph_inputs = runtime_graph.input
        for ele_graph_input in graph_inputs:
            if node.input[0] == ele_graph_input.name:
                return ele_graph_input
        return None

    def modify_value_info_by_graph_input(value_info_name, graph_input):
        is_found = False
        for idx in range(len(runtime_graph.value_info)):
            if runtime_graph.value_info[idx].name == value_info_name:
                is_found = True
                runtime_graph.value_info[
                    idx].type.elem_type = graph_input.type.elem_type
                for i in range(len(graph_input.type.dim)):
                    runtime_graph.value_info[idx].type.dim[
                        i] = graph_input.type.dim[i]
        assert is_found == True

    def modify_value_info_by_name(dest_name, src_name):
        dest_idx = -1
        src_idx = -1
        for idx in range(len(runtime_graph.value_info)):
            if runtime_graph.value_info[idx].name == dest_name:
                dest_idx = idx
            if runtime_graph.value_info[idx].name == src_name:
                src_idx = idx
            if src_idx != -1 and dest_idx != -1:
                break
        assert src_idx != -1 or dest_idx != -1
        runtime_graph.value_info[
            dest_idx].type.elem_type = runtime_graph.value_info[
                src_idx].type.elem_type
        for i in range(len(runtime_graph.value_info[dest_idx].type.dim)):
            runtime_graph.value_info[dest_idx].type.dim[
                i] = runtime_graph.value_info[src_idx].type.dim[i]

    def get_input_from_node_name(input):
        for node in runtime_graph.node:
            i = 0
            for output in node.output:
                if output == input:
                    return node.name, i
                i = i + 1
        return None, -1

    while i < len(runtime_graph.node):
        is_match = False
        transpose_node_name = ''
        quantize_node_name = ''
        bpu_index = 0
        transpose_input_from_node_name = ''
        transpose_input_from_node_idx = -1
        if runtime_graph.node[i].op_type == "Transpose" and len(
                runtime_graph.node[i].output) == 1 and len(
                    runtime_graph.node[i].input) == 1:
            transpose_input_from_node_name, transpose_input_from_node_idx = get_input_from_node_name(
                runtime_graph.node[i].input[0])
            transpose_consumer_nodes = output2consumers.get(
                runtime_graph.node[i].output[0], None)
            if transpose_consumer_nodes and len(transpose_consumer_nodes) == 1:
                transpose_next_node_index = node2index[
                    transpose_consumer_nodes[0]]
                transpose_next_node = runtime_graph.node[
                    transpose_next_node_index]
                if transpose_next_node.op_type == "Quantize" and len(
                        transpose_next_node.output) == 1:
                    quantize_consumer_nodes = output2consumers.get(
                        transpose_next_node.output[0], None)
                    if quantize_consumer_nodes and len(
                            quantize_consumer_nodes) == 1:
                        quantize_next_node_index = node2index[
                            quantize_consumer_nodes[0]]
                        quantize_next_node = runtime_graph.node[
                            quantize_next_node_index]
                        # if we need to consider bpu input from many nodes??
                        if quantize_next_node.op_type == "BPU":
                            is_match = True
                            transpose_node_name = runtime_graph.node[i].name
                            quantize_node_name = transpose_next_node.name
                            bpu_index = quantize_next_node_index
        if is_match:
            one_graph_input = get_graph_input(runtime_graph.node[i])
            assert len(
                runtime_graph.node[node2index[quantize_node_name]].input) == 2
            assert len(
                runtime_graph.node[node2index[quantize_node_name]].output) == 1

            quantize_scale_list = []
            for one_attr in runtime_graph.node[bpu_index].attribute:
                if one_attr.name == HORIZONRT_FUSED_QUANTIZE_ATTR_NAME:
                    quantize_scale_list = one_attr.floats
                    break
            if len(quantize_scale_list) == 0:
                quantize_scale_list = list(
                    range(len(runtime_graph.node[bpu_index].input)))
                for index in range(len(quantize_scale_list)):
                    quantize_scale_list[index] = 0.0
                runtime_node_attribute = runtime_graph.node[
                    bpu_index].attribute.add()
                runtime_node_attribute.name = HORIZONRT_FUSED_QUANTIZE_ATTR_NAME
                runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOATS
                runtime_node_attribute.floats.extend(quantize_scale_list)
                quantize_scale_list = runtime_node_attribute.floats
            j = 0
            while j < len(runtime_graph.node[bpu_index].input):
                if runtime_graph.node[bpu_index].input[
                        j] == runtime_graph.node[
                            node2index[quantize_node_name]].output[0]:
                    if one_graph_input is not None:
                        runtime_graph.node[
                            node2index[transpose_node_name]].output[
                                0] = runtime_graph.node[bpu_index].input[j]
                        runtime_graph.node[node2index[
                            transpose_node_name]].op_type = HORIZONRT_FUSED_COPY_OP_NAME
                        modify_value_info_by_graph_input(
                            runtime_graph.node[
                                node2index[transpose_node_name]].output[0],
                            one_graph_input)
                    else:
                        origin_name = runtime_graph.node[
                            node2index[transpose_input_from_node_name]].output[
                                transpose_input_from_node_idx]
                        runtime_graph.node[
                            node2index[transpose_input_from_node_name]].output[
                                transpose_input_from_node_idx] = runtime_graph.node[
                                    bpu_index].input[j]
                        modify_value_info_by_name(
                            runtime_graph.node[
                                node2index[transpose_input_from_node_name]].
                            output[transpose_input_from_node_idx], origin_name)
                    quantize_node_input_name = runtime_graph.node[
                        node2index[quantize_node_name]].input[1]
                    is_found_initializer = False
                    for one_initialize in runtime_graph.initializer:
                        if one_initialize.name == quantize_node_input_name:
                            assert len(one_initialize.float_data) == 1
                            quantize_scale_list[j] = one_initialize.float_data[
                                0]
                            is_found_initializer = True
                            break
                    assert is_found_initializer == True
                    break
                j = j + 1
            if one_graph_input is not None:
                del_value_infos.append(runtime_graph.node[
                    node2index[quantize_node_name]].input[0])

                del runtime_graph.node[node2index[quantize_node_name]]
                update_node2index(node2index[quantize_node_name], node2index)
            else:
                del_value_infos.append(runtime_graph.node[
                    node2index[transpose_node_name]].input[0])
                del_value_infos.append(runtime_graph.node[
                    node2index[transpose_node_name]].output[0])

                del runtime_graph.node[node2index[transpose_node_name]]
                update_node2index(node2index[transpose_node_name], node2index)
                del runtime_graph.node[node2index[quantize_node_name]]
                update_node2index(node2index[quantize_node_name], node2index)

        i = i + 1

    for del_value_info in del_value_infos:
        value_info_index = 0
        while value_info_index < len(runtime_graph.value_info):
            if runtime_graph.value_info[
                    value_info_index].name == del_value_info:
                del runtime_graph.value_info[value_info_index]
                break
            value_info_index += 1
