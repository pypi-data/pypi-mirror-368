# Copyright (c) 2022 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import os
import copy
import enum
import argparse
import logging
from graphviz import Digraph
from difflib import SequenceMatcher
from horizon_tc_ui.hbdtort import runtime_pb2


class DataFormatType(enum.Enum):
    UNDEFINED = 0
    FLOAT32 = 1
    UINT8 = 2
    INT8 = 3
    UINT16 = 4
    INT16 = 5
    INT32 = 6
    INT64 = 7
    STRING = 8
    FLOAT16 = 9
    DOUBLE = 10
    UINT32 = 11
    UINT64 = 12
    BFLOAT16 = 13
    BOOL = 14


class InputDataType(enum.Enum):
    UNDEFINED = 0
    INT8 = 1
    UINT8 = 2
    INT32 = 3
    UINT32 = 4
    FEATUREMAP = 5
    GRAY = 6
    NV12 = 7
    YUV444 = 8
    BGR = 9
    RGB = 10
    BGR_PLANAR = 11
    RGB_PLANAR = 12
    NV12_SEPARATE = 13
    INT64 = 14
    UINT64 = 15
    FLOAT64 = 16
    INT16 = 17
    UINT16 = 18
    FLOAT16 = 19
    INT4 = 20
    UINT4 = 21


class InputLayoutType():
    UNUSED = 0
    NHWC = 1
    NCHW = 2


input_layout_map = {1: "NHWC", 2: "NCHW"}


class DotNode:
    def __init__(self, name):
        self.name = name
        self.input_nodes = []
        self.output_nodes = []
        self.shape = []
        self.next_nodes = []
        self.type = ""
        self.shape_index = 0

    def __str__(self):
        return ("name: {} type: {} shape: {} input_nodes: {} output_nodes: {} "
                "next_nodes: {}".format(self.name, self.type, self.shape,
                                        self.input_nodes, self.output_nodes,
                                        self.next_nodes))


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def find_next_nodes(target_node: DotNode, dot_notes: list):
    for output_node in target_node.output_nodes:
        for node in dot_notes:
            if node != target_node and output_node in node.input_nodes:
                target_node.next_nodes.append(node.name)


'''
def find_output_node(input_node_name, dot_notes: list):
    for node in dot_notes:
        if input_node_name in node.input_nodes:
            return node
'''


def find_output_node_all(input_node_name, dot_notes: list,
                         dot_names_back: list):
    for node in dot_notes:
        if input_node_name in node.input_nodes:
            dot_names_back.append(node.name)


def filter_str(name):
    return name.replace("/", "").replace(":", "").replace(",", "")


def find_output_name(name, node_names):
    index = 0
    for output_name in node_names:
        if name in output_name:
            return node_names[index]
        index = index + 1
    return None


def find_node(name_list, node):
    ratio = 0
    index = 0
    count = 0
    for name in name_list:
        if node in name:
            return name_list[index]
        res = similarity(name, node)
        if ratio < res:
            ratio = res
            count = index
        index = index + 1
    return name_list[count]


def get_data_type(input_type_rt: str) -> str:
    """
    get the data type by input_type_rt
    :param input_type_rt: nv12/rgb/bgr/yuv444/gray/featuremap
    :return: data_type
    """
    if 'featuremap' in input_type_rt:
        if '_' in input_type_rt:
            suffix = input_type_rt.split('_')[1].lower()
            if 's' in suffix:
                return "INT" + suffix.split('s')[1]
            elif 'u' in suffix:
                return "UINT" + suffix.split('u')[1]
            elif 'f' in suffix:
                return "FLOAT" + suffix.split('f')[1]
            else:
                return "FLOAT32"
        else:
            return "FLOAT32"
    else:
        if '_128' in input_type_rt:
            return 'INT8'
        else:
            return 'UINT8'


def input_type_rt_shape_transpose(shape: list, march: str, input_type_rt: str,
                                  input_layout_rt: str) -> list:
    """
    calculate the shape of nv12 node input
    :param shape: shape
    :param march: bernoulli2, bayes or bayes-e
    :param input_type_rt: bgr/rgb/yuv444...
    :param input_layout_rt: NCHW / NHWC
    :return: shape list eg
    """
    data_type = get_data_type(input_type_rt)
    _shape = [
        int(i)
        for i in shape[0].split(f', {input_type_rt.upper()}')[0].split('x')
    ]
    # NHWC
    if input_type_rt == "featuremap":
        data_shape = 'x'.join(
            [str(i) for i in [_shape[index] for index in [0, 3, 1, 2]]])
    else:
        if input_layout_rt == "NHWC":
            data_shape = 'x'.join(
                [str(i) for i in [_shape[index] for index in [0, 2, 3, 1]]])
        else:
            data_shape = 'x'.join(
                [str(i) for i in [_shape[index] for index in [0, 3, 1, 2]]])
    return [
        f'{data_shape}, {input_type_rt.upper()}, ',
        f'{input_layout_rt}, {data_type}'
    ]


def nv12_shape_transpose(shape: list, march: str, input_type_rt: str) -> list:
    """
    calculate the shape of nv12 node input
    :param shape: yuv shape
    :param march: bernoulli2, bayes or bayes-e
    :return: nv12 shape list eg ['1x336x224, NV12']
    """
    yuv_shape = [int(i) for i in shape[0].split(', NV12')[0].split('x')]
    # NHWC
    nv12_shape = 'x'.join(str(x) for x in yuv_shape) + " / 2"
    return [f'{nv12_shape}, NV12, {get_data_type(input_type_rt)}']


def insert_nv12_conv_node(i, dot_node: DotNode, dot_nodes: list, march: str,
                          input_type_rt: str) -> list:
    """
    when data type is nv12 insert conversion node
    :param i: number
    :param dot_node: dot node
    :param dot_nodes: dot nodes
    :param march: bernoulli2, bayes or bayes-e
    :param input_type_rt: nv12
    :return: None
    """
    # Create a dot node and assignment
    insert_dot_node = DotNode(
        name="NV12TOYUV444" if i == 0 else f'NV12TOYUV444_{i}')
    insert_dot_node.type = "BPU"
    insert_dot_node.input_nodes.append(dot_node.name)
    dot_node_shape = copy.deepcopy(dot_node.shape)
    dot_node_shape[0] = dot_node_shape[0].replace("NV12", "YUV444")
    insert_dot_node.output_nodes = dot_node.output_nodes
    insert_dot_node.next_nodes = dot_node.next_nodes
    # Modify the input node of the original node
    # next_node.input_nodes = [insert_dot_node.name]
    # Insert new nv12 node
    dot_nodes.insert(1, insert_dot_node)
    # Modify the output node of the data input node
    dot_node.next_nodes = [insert_dot_node.name]
    # Modify the output shape of the data input node
    nv12_shape = nv12_shape_transpose(dot_node.shape, march, input_type_rt)
    dot_node.shape = nv12_shape
    insert_dot_node.shape = dot_node_shape
    return nv12_shape


def insert_layout_convert_node(i: int, dot_node: DotNode, dot_nodes: list,
                               march: str, node_name: str, input_type_rt: str,
                               input_layout_rt: str) -> list:
    """
        when data type is not nv12 and ( march and layout_rt do not match ）
        insert conversion node
        :param i: number
        :param dot_node: dot node
        :param dot_nodes: dot nodes list
        :param march: bernoulli2, bayes or bayes-e
        :param node_name: node name
        :param input_type_rt: bgr/rgb/yuv444...
        :return: None
        """
    # Create a dot node and assignment
    # name: h1
    # type shape: ['1x64x68x240, FLOAT, NHWC, UINT8']
    # input_nodes: []
    # output_nodes: []
    # next_nodes: ['h1_mul1_HzQuantize_TransposeInput0']
    insert_dot_node = DotNode(name=node_name if i == 0 else (node_name +
                                                             f'_{i}'))
    insert_dot_node.type = node_name.lower().replace('to', '2')
    insert_dot_node.input_nodes.append(dot_node.name)
    insert_dot_node.shape = dot_node.shape
    insert_dot_node.output_nodes = dot_node.output_nodes
    insert_dot_node.next_nodes = dot_node.next_nodes

    dot_nodes.insert(1, insert_dot_node)
    dot_node.next_nodes = [insert_dot_node.name]
    dot_node_shape = input_type_rt_shape_transpose(dot_node.shape, march,
                                                   input_type_rt,
                                                   input_layout_rt)
    dot_node.shape = dot_node_shape
    return dot_node_shape


def draw_graph_png(model_file, dst_path, save_name, is_old=False):
    if is_old:
        raise ValueError("old model is not supported anymore")
    dot_nodes = []
    initializer_nodes = []
    input_node_names = []
    output_node_names = []
    graph_nodes = {}
    input_nodes = []

    model_reserial = runtime_pb2.ModelProto()
    runtime_model_file = open(model_file, 'rb')
    model_reserial.ParseFromString(runtime_model_file.read())
    runtime_model_file.close()

    graph = model_reserial.graphs[0]
    model_march = model_reserial.metadata_props_info[0].model_info.get('MARCH')
    input_type_rt_list = model_reserial.metadata_props_info[0].model_info.get(
        'INPUT_TYPE_RT').split(';')
    input_layout_rt_list = model_reserial.metadata_props_info[
        0].model_info.get('INPUT_LAYOUT_RT').split(';')

    if "" in input_type_rt_list: input_type_rt_list.remove("")  # noqa
    if "" in input_layout_rt_list: input_layout_rt_list.remove("")  # noqa

    need_insert_node_dict = {}
    for index in range(len(input_type_rt_list)):
        input_rt = input_type_rt_list[index]
        input_layout = input_layout_rt_list[index]
        input_shape_layout = get_input_shape_layout(graph.input[index])
        if "NCHW" == input_layout and "feature" not in input_rt and input_shape_layout == "NHWC":  # noqa
            need_insert_node_dict[index] = {
                "layout_rt_node_name": "NCHWTONHWC",
                "need_insert_layout_convert_node": True,
            }
        elif model_march in [
                "bayes", "bayes-e"
        ] and input_layout == "NHWC" and "feature" not in input_rt and input_shape_layout == "NCHW":  # noqa
            need_insert_node_dict[index] = {
                "layout_rt_node_name": "NHWCTONCHW",
                "need_insert_layout_convert_node": True,
            }
        else:
            need_insert_node_dict[index] = {
                "layout_rt_node_name": "",
                "need_insert_layout_convert_node": False,
            }

    input_index = -1
    layout_rt_node_name = ""
    for value_input in graph.input:
        input_index += 1

        check_dim_of_shape(input_type_rt_list[input_index], input_index,
                           value_input)

        layout = input_layout_map[graph.input_layout[input_index]]
        need_insert_layout_convert_node = need_insert_node_dict[input_index][
            'need_insert_layout_convert_node']
        layout_rt_node_name = need_insert_node_dict[input_index][
            'layout_rt_node_name']
        if need_insert_layout_convert_node:
            input_layout, new_input_layout = layout_rt_node_name.split("TO")
            layout = layout.replace(input_layout, new_input_layout)

        if input_type_rt_list[input_index] == 'nv12':
            layout = layout.replace("NCHW", "NHWC")

        if input_type_rt_list[input_index] == "featuremap" and \
           need_insert_layout_convert_node:
            dim_str = str(value_input.type.dim[0]) + "x" + str(
                value_input.type.dim[2]) + "x" + str(
                    value_input.type.dim[3]) + "x" + str(
                        value_input.type.dim[1])
        else:
            dim_str = ""
            for i in range(len(value_input.type.dim)):
                if i == 0:
                    dim_str += str(value_input.type.dim[i])
                else:
                    dim_str += "x" + str(value_input.type.dim[i])
        # nv12
        if graph.input_type[input_index] == 7:
            dim_str = 'x'.join([str(i) for i in value_input.type.dim])

        input_data_type = InputDataType(graph.input_type[input_index]).name
        data_format_type = DataFormatType(
            graph.input[input_index].type.elem_type).name
        graph_nodes[filter_str(value_input.name)] = ", ".join(
            [dim_str, input_data_type, layout, data_format_type])
        input_node_names.append(filter_str(value_input.name))

    # get output layout for attribute
    node_names = []
    output_layout = ""
    for node in graph.node:
        node_names.append(node.name)
        if len(node.attribute) != 0:
            for att in node.attribute:
                if att.name == "output_data_format":
                    output_layout = str(node.attribute[len(node.attribute) -
                                                       1].s)

    # record the num of repeat names for output data(not the node)
    cnt = 0
    # record the repeat names(just for searching)
    repeat_name_list = []
    for value_out in graph.output:
        dim_str = ""
        # dim < 4, no layout type
        if len(value_out.type.dim) != 4:
            out_layout = ""
        else:
            out_layout = ", " + output_layout[2:len(output_layout) - 1]
        for dim in value_out.type.dim:
            dim_str = dim_str + str(dim) + "x"
        graph_nodes[filter_str(
            value_out.name
        )] = dim_str[0:len(dim_str) - 1] + ", " + DataFormatType(
            value_out.type.elem_type).name + out_layout
        # get output data names
        if value_out.name in node_names:
            # rename the repeated name
            repeat_name_list.append(value_out.name)
            cnt = cnt + 1
        else:
            output_node_names.append(filter_str(value_out.name))

    for value_info in graph.value_info:
        dim_str = ""
        for dim in value_info.type.dim:
            dim_str = dim_str + str(dim) + "x"
        graph_nodes[filter_str(
            value_info.name)] = dim_str[0:len(dim_str) - 1] + ", " + str(
                DataFormatType(value_info.type.elem_type)).split('.')[-1]

    for initializer in graph.initializer:
        initializer_nodes.append(initializer.name)

    for node in graph.node:
        dot_node = DotNode(filter_str(node.name))
        for input in node.input:
            if input not in initializer_nodes:
                dot_node.input_nodes.append(filter_str(input))
        for out in node.output:
            if out and out not in initializer_nodes:
                dot_node.output_nodes.append(filter_str(out))
        dot_node.type = node.op_type
        dot_nodes.append(dot_node)
    # input nodes
    for name in input_node_names:
        input_node = DotNode(name)
        # input_node.next_nodes.append(find_output_node(name, dot_nodes).name)
        find_output_node_all(name, dot_nodes, input_node.next_nodes)

        input_node.shape.append(graph_nodes[input_node.name])
        dot_nodes.insert(0, input_node)
        input_nodes.append(input_node)

    for name in output_node_names:
        out_node = DotNode(name)
        out_node.input_nodes.append(name)
        dot_nodes.append(out_node)
    # output nodes
    for dot_node in dot_nodes:
        find_next_nodes(dot_node, dot_nodes)
        out_cnt = 0
        for output_node in dot_node.output_nodes:
            dot_node.shape.append(graph_nodes[output_node])
            output_node_name = find_output_name(dot_node.name,
                                                output_node_names)
            dot_node.next_nodes.append(output_node_name)
            # modify repeated name node's output abd next node info
            if output_node in repeat_name_list:
                dot_node.output_nodes[out_cnt] = f" {output_node} "
                dot_node.next_nodes[out_cnt] = f" {output_node} "
                out_cnt = out_cnt + 1

    for i in range(len(input_nodes)):
        if input_type_rt_list[i] in ["nv12", "yuv420sp_bt601_video"]:
            dot_node_shape = insert_nv12_conv_node(i, input_nodes[i],
                                                   dot_nodes, model_march,
                                                   "nv12")
            logging.info(
                "When the bin model input type is nv12, "
                "the BPU will convert nv12 to yuv444 internally "
                "to do the operation. In the drawing process, "
                "we use a BPU node to replace this input type conversion "
                "process to ensure the correctness of the logical "
                "relationships expressed in the diagram, but in fact, "
                "this BPU node doesn't exist in the bin model.. "
                "We name this BPU node involved in the drawing "
                f"process NV12TOYUV444 with details {dot_node_shape}.")

        else:
            need_insert_layout_convert_node = need_insert_node_dict[i][
                'need_insert_layout_convert_node']
            if need_insert_layout_convert_node:
                layout_rt_node_name = need_insert_node_dict[i][
                    'layout_rt_node_name']
                dot_node_shape = insert_layout_convert_node(
                    i, input_nodes[i], dot_nodes, model_march,
                    layout_rt_node_name, input_type_rt_list[i],
                    input_layout_rt_list[i])
                logging.info(
                    "When the layout of the bin model input does not match "
                    "the layout of the BPU input, dnn will do the layout "
                    "transformation in preprocessing, during the drawing "
                    "process, we use a transpose node instead of this "
                    "pre-processing process to ensure the correctness of "
                    "the logical relationships expressed in the diagram, "
                    "but in fact, this transpose node doesn't exist in the "
                    "bin model. We name this transpose node involved in the "
                    f"drawing process {layout_rt_node_name} "
                    f"and give the details as {dot_node_shape}.")

    # draw graph png
    dot = Digraph(name="model", comment="the test", format="png")
    for d in dot_nodes:
        if d.type != "":
            label_name = "name: " + d.name + "\ntype: " + d.type
            if d.type == "BPU":
                dot.node(name=d.name,
                         label=label_name,
                         color='black',
                         shape="box",
                         style="filled",
                         fillcolor="cadetblue")
            else:
                dot.node(name=d.name,
                         label=label_name,
                         color='black',
                         shape="box",
                         style="filled",
                         fillcolor="lightgrey")
        else:
            dot.node(name=d.name, label=d.name, color='black')

    # put txt
    for d in dot_nodes:
        n_nodes = d.next_nodes
        for n in n_nodes:
            if len(d.shape) != 0 and n is not None:
                if d.shape_index < len(d.shape):
                    dot.edge(d.name,
                             n,
                             label=d.shape[d.shape_index],
                             color='red')
                else:
                    dot.edge(d.name,
                             n,
                             label=d.shape[len(d.shape) - 1],
                             color='red')
                d.shape_index = d.shape_index + 1

    if save_name is None:
        save_name = os.path.basename(model_file).split(".")[0]
    dot.render(filename=save_name, directory=dst_path, view=False)
    logging.info("draw graph png finished.")


def check_dim_of_shape(input_type_rt, input_index, input_info):
    ndim = len(input_info.type.dim)
    if input_type_rt not in \
            ["featuremap", "featuremap_s8", "featuremap_u8"] and ndim != 4:
        raise ValueError(
            f"input {input_index} : {input_type_rt} has {ndim} dimension, "
            "not 4 dimension")


def get_input_shape_layout(value_info):
    dims = value_info.type.dim
    if len(dims) != 4:
        return ""

    if dims[1] == 3 or dims[1] == 1:
        return "NCHW"
    if dims[3] == 3 or dims[3] == 1:
        return "NHWC"

    return ""


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path',
                        '-m',
                        type=str,
                        required=True,
                        help='model file path.')
    parser.add_argument('--dst_path',
                        '-d',
                        type=str,
                        required=False,
                        default="./",
                        help='result save path.')
    parser.add_argument('--save_name',
                        '-s',
                        type=str,
                        required=False,
                        default="model_graph",
                        help='result save name.')
    args = parser.parse_args()

    draw_graph_png(args.model_path, args.dst_path, args.save_name)
