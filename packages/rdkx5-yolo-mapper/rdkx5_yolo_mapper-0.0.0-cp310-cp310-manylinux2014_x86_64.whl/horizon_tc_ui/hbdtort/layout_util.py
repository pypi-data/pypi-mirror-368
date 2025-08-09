# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.
import logging
from horizon_tc_ui.hbdtort import runtime_pb2


def set_featuremap_layout(model_deps_info, input_layout_rt, runtime_graph):
    input_type = model_deps_info.get("input_type_rt")
    march = model_deps_info.get("march")
    logging.debug("set_featuremap_layout start")
    if march is None:
        logging.debug("Parameter march info missing. layout setting skips")
        return

    if march in ["bayes", "bayes-e"]:
        rt_layout = model_deps_info.get('input_layout_rt', None)
        train_layout = model_deps_info.get('input_layout_train', None)
        if rt_layout == train_layout:
            return

    for index, type_item in enumerate(input_type):
        if type_item.startswith('featuremap'):
            logging.debug(f"type item {index}, {type_item}")
            if input_layout_rt[index].upper() == "NHWC":
                set_input_layout_nhwc(runtime_graph, index, model_deps_info)
            elif input_layout_rt[index].upper() == "NCHW":
                set_input_layout_nchw(runtime_graph, index, model_deps_info)
            else:
                raise ValueError(
                    f'Invalid output layout: {input_layout_rt[index]}')


def set_input_layout_nchw(runtime_graph, index, model_deps_info):
    '''set output layout nhwc'''
    input_info = runtime_graph.input[index]
    ndim = len(input_info.type.dim)
    if ndim != 4:
        logging.info(
            f"Input {input_info.name} has {ndim} dimension, not 4 dimension"
            "featuremap, layout adjustment skips")
        return
    input_node_index = -1
    # 倒着遍历避免在删除节点后, node_index 越界问题
    need_add_transpose_node_list = []
    for node_index in range(len(runtime_graph.node) - 1, -1, -1):
        if input_info.name in runtime_graph.node[node_index].input:
            input_node_index = node_index
            input_node = runtime_graph.node[input_node_index]
            quantize_layout = ""
            if input_node.op_type == "Quantize":
                for attr in input_node.attribute:
                    if attr.name == 'axis':
                        if attr.i == 1:
                            quantize_layout = 'NCHW'
                        elif attr.i == 3:
                            quantize_layout = 'NHWC'

            # 模型中原本存在一个输入为NCHW的dequanti节点, 所以什么都不做
            if input_node.op_type == "Quantize" and quantize_layout == "NCHW":
                logging.info(
                    f"The model's input {input_info.name} connects to node "
                    f"{input_node.name}, it is Quantize, its layout is "
                    "already NCHW. No action needed")
                return
            # 模型中原本存在一个NCHW2NHWC的transpose, 所以什么都不做
            elif input_node.op_type == "Transpose" and \
                    input_node.attribute[0].ints == [0, 2, 3, 1]:
                logging.info(
                    f"The model's input {input_info.name} connects to node"
                    f"{input_node.name}, it is Transpose NCHW2NHWC. "
                    f"No action needed")
                return
            # 模型中原本存在一个NHWC2NCHW的transpose, 所以可以把这个transpose删掉
            elif input_node.op_type == "Transpose" and \
                    input_node.attribute[0].ints == [0, 3, 1, 2]:
                logging.info(
                    f"The model's input {input_info.name} connects to node "
                    f"{input_node.name}, it is Transpose NHWC2NCHW. "
                    f"It will be removed in the bin model")
                # 删除tranpose node
                removed_transpose_name = input_node.name
                for node in runtime_graph.node:
                    if input_node.output[0] in node.input:
                        for index in range(len(node.input)):
                            if input_node.output[0] == node.input[index]:
                                node.input[index] = input_node.input[0]
                input_info.type.dim[1], input_info.type.dim[2], input_info.type.dim[3] = \
                    input_info.type.dim[3], input_info.type.dim[1], input_info.type.dim[2] # noqa E501
                # 删除value info中
                for i in range(len(runtime_graph.value_info)):
                    if runtime_graph.value_info[i].name == input_info.name:
                        del runtime_graph.value_info[i]
                        break
                del runtime_graph.node[input_node_index]
                model_deps_info[
                    "DELETED_NODES_IN_BUILD"] = model_deps_info.get(
                        "DELETED_NODES_IN_BUILD",
                        "") + removed_transpose_name + " "

                logging.info(f"{removed_transpose_name} removed")
            elif (input_node.op_type == "BPU"
                  or input_node.op_type == "HzBpuHBM") or (
                      input_node.op_type == "Quantize"
                      and quantize_layout == "NHWC"):
                logging.info(
                    f"The model's input {input_info.name} connects to node "
                    f"{input_node.name}, its layout is NHWC, "
                    "a NCHW2NHWC transpose node will be added.")
                need_add_transpose_node_list.append((node_index, input_node))

            else:
                logging.info(
                    f"input_node {input_node.name}'s layout is already NCHW")

    if need_add_transpose_node_list:
        # 加一个tranpose node，将原输入从 NHWC 变为 NCHW
        transpose_node = runtime_pb2.NodeProto()
        transpose_node.op_type = "Transpose"
        transpose_node.input.append(input_info.name)
        transpose_node.name = "transpose_node_" + input_info.name + "2nhwc"
        trans_out_name = transpose_node.name + "_output"
        transpose_node.output.append(trans_out_name)

        # Modify the first input name of target node
        # to be the name of new node output
        for _, input_node in need_add_transpose_node_list:
            input_node.input[0] = trans_out_name

        node_attribute = transpose_node.attribute.add()
        node_attribute.name = 'perm'
        node_attribute.type = runtime_pb2.AttributeProto.INTS
        node_attribute.ints.append(0)
        node_attribute.ints.append(2)
        node_attribute.ints.append(3)
        node_attribute.ints.append(1)
        runtime_graph.node.insert(0, transpose_node)
        model_deps_info["ADD_NODES_IN_BUILD"] = model_deps_info.get(
            "ADD_NODES_IN_BUILD", "") + transpose_node.name + " "

        # 在graph value_info 中添加原输入节点
        value_info_node = runtime_graph.value_info.add()
        value_info_node.name = trans_out_name
        value_info_node.type.elem_type = input_info.type.elem_type
        for dim in input_info.type.dim:
            value_info_node.type.dim.append(dim)

        input_info.type.dim[1], input_info.type.dim[2], input_info.type.dim[3] = \
            input_info.type.dim[3], input_info.type.dim[1], input_info.type.dim[2] # noqa E501


def set_input_layout_nhwc(runtime_graph, index, model_deps_info):
    '''set input layout nchw'''
    input_info = runtime_graph.input[index]
    ndim = len(input_info.type.dim)
    if ndim != 4:
        logging.info(f"Input {input_info.name} has {ndim} dimension, "
                     "not 4 dimension featuremap, layout adjustment skips")
        return
    input_node_index = -1
    need_add_transpose_node_list = []
    # 倒着遍历避免在删除节点后, node_index 越界问题
    for node_index in range(len(runtime_graph.node) - 1, -1, -1):
        if input_info.name in runtime_graph.node[node_index].input:
            input_node_index = node_index
            input_node = runtime_graph.node[input_node_index]
            quantize_layout = ""
            if input_node.op_type == "Quantize":
                for attr in input_node.attribute:
                    if attr.name == 'axis':
                        if attr.i == 1:
                            quantize_layout = 'NCHW'
                        elif attr.i == 3:
                            quantize_layout = 'NHWC'

            if input_node.op_type == "Transpose" and \
                    input_node.attribute[0].ints == [0, 2, 3, 1]:
                logging.info(
                    f"The model's input {input_info.name} connects to node "
                    f"{input_node.name}, it is Transpose NCHW2NHWC."
                    "It will be removed")
                # 用原tranpose node的下一节点代替graph.input中的transpose节点
                removed_transpose_name = input_node.name
                # input_info.name = input_node.output[0]
                for node in runtime_graph.node:
                    if input_node.output[0] in node.input:
                        for index in range(len(node.input)):
                            if input_node.output[0] == node.input[index]:
                                node.input[index] = input_node.input[0]

                input_info.type.dim[1], input_info.type.dim[2], input_info.type.dim[3] = \
                    input_info.type.dim[2], input_info.type.dim[3], input_info.type.dim[1] # noqa E501

                # 删除value info中的原下一节点
                for i in range(len(runtime_graph.value_info)):
                    if runtime_graph.value_info[i].name == input_info.name:
                        del runtime_graph.value_info[i]
                        break
                del runtime_graph.node[input_node_index]
                model_deps_info[
                    "DELETED_NODES_IN_BUILD"] = model_deps_info.get(
                        "DELETED_NODES_IN_BUILD",
                        "") + removed_transpose_name + " "

                logging.info(f"{removed_transpose_name} removed")

            elif input_node.op_type == "Transpose" and \
                    input_node.attribute[0].ints == [0, 3, 1, 2]:
                logging.info(
                    f"The model's input {input_info.name} connects to node "
                    f"{input_node.name}, it is Transpose NHWC2NCHW. "
                    f"No action needed")
            elif input_node.op_type == "Quantize" and \
                    quantize_layout == "NHWC":
                logging.info(
                    f"The model's input {input_info.name} connects to node "
                    f"{input_node.name}, it is Quantize, its layout is "
                    "already NHWC. No action needed")
            elif (input_node.op_type == "BPU"
                  or input_node.op_type == "HzBpuHBM"):
                logging.info(
                    f"The model's input {input_info.name} connects to node "
                    f"{input_node.name}, it is BPU OP, its layout is already"
                    "NHWC. No action needed")
            else:
                logging.info(
                    f"A NHWC2NCHW transpose node will be added for input "
                    f"{input_info.name} in bin model since except for "
                    "Quanitze/Dequantize and transpose, all other op's are "
                    "treated as nchw layout by default!")
                need_add_transpose_node_list.append((node_index, input_node))

    if need_add_transpose_node_list:
        # Except for Dequantize and transpose,
        # all other op's are nchw output by default
        # Add a transpose node to convert nhwc to nchw

        # Constructing the new node to be inserted
        transpose_node = runtime_pb2.NodeProto()
        transpose_node.op_type = "Transpose"
        transpose_node.input.append(input_info.name)
        transpose_node.name = "transpose_node_" + input_info.name + "2nchw"

        trans_out_name = transpose_node.name + "_output"
        transpose_node.output.append(trans_out_name)

        # Modify the first input name of target node
        # to be the name of new node output
        for _, input_node in need_add_transpose_node_list:
            input_node.input[0] = trans_out_name

        node_attribute = transpose_node.attribute.add()
        node_attribute.name = 'perm'
        node_attribute.type = runtime_pb2.AttributeProto.INTS
        node_attribute.ints.append(0)
        node_attribute.ints.append(3)
        node_attribute.ints.append(1)
        node_attribute.ints.append(2)
        # Insert to start position
        runtime_graph.node.insert(0, transpose_node)
        model_deps_info["ADD_NODES_IN_BUILD"] = model_deps_info.get(
            "ADD_NODES_IN_BUILD", "") + transpose_node.name + " "

        # Add input_info to graph value_info and
        # trans_node out information to graph input.
        value_info = runtime_graph.value_info.add()
        value_info.name = trans_out_name
        value_info.type.elem_type = input_info.type.elem_type
        for dim in input_info.type.dim:
            value_info.type.dim.append(dim)
        input_info.type.dim[1], input_info.type.dim[2], input_info.type.dim[3] = \
            input_info.type.dim[2], input_info.type.dim[3], input_info.type.dim[1] # noqa E501


def set_output_layout(output_layout, runtime_graph):
    '''set output layout(nchw or nhwc)'''
    if output_layout.upper() == "NHWC":
        set_output_layout_nhwc(runtime_graph)
    elif output_layout.upper() == "NCHW":
        set_output_layout_nchw(runtime_graph)
    else:
        raise ValueError(f'Invalid output layout: {output_layout}')


def set_output_layout_nhwc(runtime_graph):
    '''set output layout nhwc'''
    for output_info in runtime_graph.output:
        ndim = len(output_info.type.dim)
        if ndim < 4:
            continue
        output_node_index = -1
        for node_index in range(len(runtime_graph.node)):
            if output_info.name in runtime_graph.node[node_index].output:
                output_node_index = node_index
                break
        if output_node_index == -1:
            raise ValueError("Output info %s not belong to a node" %
                             (output_info.name))
        output_node = runtime_graph.node[output_node_index]
        node_type = output_node.op_type
        if node_type == "Dequantize" and output_node.attribute[0].s == b"NHWC":
            continue
        if node_type == "Transpose" and \
                output_node.attribute[0].ints == [0, 2, 3, 1]:
            continue
        if node_type == "Transpose" and \
                output_node.attribute[0].ints == [0, 3, 1, 2]:
            # 删除tranpose node
            output_info.name = output_node.input[0]
            output_info.type.dim[1], output_info.type.dim[2], output_info.type.dim[3] = \
                output_info.type.dim[2], output_info.type.dim[3], output_info.type.dim[1] # noqa E501

            # 删除value info中
            for i in range(len(runtime_graph.value_info)):
                if runtime_graph.value_info[i].name == output_info.name:
                    del runtime_graph.value_info[i]
                    break
            del runtime_graph.node[output_node_index]
        else:
            # 加一个tranpose node，将nchw转为nhwc
            transpose_node = runtime_graph.node.add()

            transpose_node.op_type = "Transpose"
            transpose_node.name = "transpose_node_" \
                + output_info.name + "2nhwc"
            transpose_node.input.append(output_info.name)
            trans_out_name = "transpose_" + output_info.name + "2nhwc"
            transpose_node.output.append(trans_out_name)

            node_attribute = transpose_node.attribute.add()
            node_attribute.name = 'perm'
            node_attribute.type = runtime_pb2.AttributeProto.INTS
            node_attribute.ints.append(0)
            node_attribute.ints.append(2)
            node_attribute.ints.append(3)
            node_attribute.ints.append(1)

            # 适配horizonrt对输出node的处理，horizonrt里默认输出node是nchw,
            # 根据输出node的data_format属性判断是不是nhwc。
            node_attribute = transpose_node.attribute.add()
            node_attribute.name = 'output_data_format'
            node_attribute.type = runtime_pb2.AttributeProto.STRING
            node_attribute.s = b'NHWC'

            # 在graph value_info中添加output_info
            # 在graph output 中添加trans_node out info
            value_info = runtime_graph.value_info.add()
            value_info.name = output_info.name
            value_info.type.elem_type = output_info.type.elem_type
            for dim in output_info.type.dim:
                value_info.type.dim.append(dim)

            output_info.name = trans_out_name
            output_info.type.dim[1], output_info.type.dim[2], output_info.type.dim[3] = \
                output_info.type.dim[2], output_info.type.dim[3], output_info.type.dim[1] # noqa E501


def set_output_layout_nchw(runtime_graph):
    '''set output layout nchw'''
    for output_info in runtime_graph.output:
        ndim = len(output_info.type.dim)
        if ndim < 4:
            continue
        output_node_index = -1
        for node_index in range(len(runtime_graph.node)):
            if output_info.name in runtime_graph.node[node_index].output:
                output_node_index = node_index
                break
        if output_node_index == -1:
            raise ValueError("Output info %s not belong to a node" %
                             (output_info.name))
        output_node = runtime_graph.node[output_node_index]
        node_type = output_node.op_type
        if node_type == "Transpose" and \
                output_node.attribute[0].ints == [0, 2, 3, 1]:
            # 删除tranpose node
            output_info.name = output_node.input[0]
            output_info.type.dim[1], output_info.type.dim[2], output_info.type.dim[3] = \
                output_info.type.dim[3], output_info.type.dim[1], output_info.type.dim[2] # noqa E501

            # 删除value info中
            for i in range(len(runtime_graph.value_info)):
                if runtime_graph.value_info[i].name == output_info.name:
                    del runtime_graph.value_info[i]
                    break
            del runtime_graph.node[output_node_index]
        elif node_type == "Dequantize" and \
                output_node.attribute[0].s == b"NHWC":
            # 加一个tranpose node，将nhwc转为nchw
            transpose_node = runtime_graph.node.add()

            transpose_node.op_type = "Transpose"
            transpose_node.name = "transpose_node_" + \
                output_info.name + "2nchw"
            transpose_node.input.append(output_info.name)
            trans_out_name = "transpose_" + output_info.name + "2nchw"
            transpose_node.output.append(trans_out_name)

            node_attribute = transpose_node.attribute.add()
            node_attribute.name = 'perm'
            node_attribute.type = runtime_pb2.AttributeProto.INTS
            node_attribute.ints.append(0)
            node_attribute.ints.append(3)
            node_attribute.ints.append(1)
            node_attribute.ints.append(2)

            # 在graph value_info中添加output_info
            # 在graph output 中添加trans_node out info
            value_info = runtime_graph.value_info.add()
            value_info.name = output_info.name
            value_info.type.elem_type = output_info.type.elem_type
            for dim in output_info.type.dim:
                value_info.type.dim.append(dim)

            output_info.name = trans_out_name
            output_info.type.dim[1], output_info.type.dim[2], output_info.type.dim[3] = \
                output_info.type.dim[3], output_info.type.dim[1], output_info.type.dim[2] # noqa E501
        else:
            # 除了Dequantize和transpose，其它op默认都是nchw的
            pass
