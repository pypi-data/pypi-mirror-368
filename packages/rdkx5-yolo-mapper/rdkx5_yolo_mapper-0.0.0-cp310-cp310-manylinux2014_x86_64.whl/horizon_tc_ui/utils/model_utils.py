# Copyright (c) 2022 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import json
import logging
from enum import Enum
from itertools import chain

import onnx
from horizon_nn.api import infer_shapes, check_model
from onnx import onnx_pb as onnx_proto
from onnx.onnx_pb import ModelProto

from horizon_tc_ui import HB_ONNXRuntime
from horizon_tc_ui.hb_binruntime import HbBinRuntime
from horizon_tc_ui.hbdtort import runtime_pb2


def add_model_output(onnx_model,
                     output_nodes=None,
                     output_tensors=None,
                     keep_original_output=True) -> ModelProto:
    """
    Modify the output nodes of the original model.

    Args:
        onnx_model: onnx model graph, in onnx.ModelProto type.
        output_nodes: target nodes that will be added to output. node's all outputs will be added.
        output_tensors: target tensors that will be added to output.
        keep_original_output: whether keep the original model's output
    Return:
        Return the onnx model in onnx.ModelProto format
    """  # noqa

    def _get_nodes(graph):
        """
      Get the nodes of the original model, and return in the format of a dict. Keys are the node names, values are the nodeprotos.

      Args:
          graph: onnx model graph, in onnx.ModelProto type.
      Return:
          Return the dict contains node info. Keys are the node names, values are the nodeprotos.
      """  # noqa
        nodes_dict = {}
        for node in graph.node:
            nodes_dict[node.name] = node
        return nodes_dict

    def _remove_original_output():
        for output in reversed(onnx_model.graph.output):
            logging.info(f"Remove original output {output.name}")
            onnx_model.graph.output.remove(output)
            onnx_model.graph.value_info.append(output)

    # check values from graph input and graph value_info
    def _add_output(output_valueinfo_list):
        onnx_model.graph.output.extend([
            onnx.helper.make_tensor_value_info(
                value.name, value.type.tensor_type.elem_type, [
                    None if d.ByteSize() == 0 else
                    d.dim_param if d.dim_param else d.dim_value
                    for d in value.type.tensor_type.shape.dim
                ]) for value in chain(onnx_model.graph.input,
                                      onnx_model.graph.value_info)
            if value.name in output_valueinfo_list
        ])

    if output_nodes is None:
        output_nodes = []
    if output_tensors is None:
        output_tensors = []

    onnx_model: ModelProto = infer_shapes(onnx_model).proto
    nodes_dict = _get_nodes(onnx_model.graph)
    model_node_names = nodes_dict.keys()
    output_tensor_list = set()

    for node_name in output_nodes:
        if node_name not in model_node_names:
            raise ValueError(f"Cannot found output {node_name} in graph nodes")
        for output_item in nodes_dict[node_name].output:
            output_tensor_list.add(output_item)
    for tensor_name in output_tensors:
        output_tensor_list.add(tensor_name)

    if not keep_original_output:
        _remove_original_output()

    _add_output(output_tensor_list)

    try:
        check_model(onnx_model)
        infer_shapes(onnx_model)
    except Exception as e:
        onnx.save(onnx_model, "model_output_inserted_invalid.onnx")
        logging.error("onnx model validation failed, invalid model "
                      "saved as model_output_inserted_invalid.onnx")
        raise e

    return onnx_model


def find_tensor(runtime_graph, tensor_name):
    for index, value_info_item in enumerate(runtime_graph.value_info):
        if value_info_item.name == tensor_name:
            return index, value_info_item
    for index, input_item in enumerate(runtime_graph.input):
        if input_item.name == tensor_name:
            return index, input_item
    for index, initializer_item in enumerate(runtime_graph.initializer):
        if initializer_item.name == tensor_name:
            return index, initializer_item
    for index, output_item in enumerate(runtime_graph.output):
        if output_item.name == tensor_name:
            return index, output_item
    raise ValueError(f"Can not find tensor {tensor_name}")


def find_value_info(runtime_graph, tensor_name):
    for index, value_info_item in enumerate(runtime_graph.value_info):
        if value_info_item.name == tensor_name:
            return index, value_info_item
    raise ValueError(f"Can not find value info {tensor_name}")


def find_input(runtime_graph, input_name):
    index = -1
    for input_info in runtime_graph.input:
        index += 1
        if input_info.name == input_name:
            return index, input_info
    return -1, None


def find_output(runtime_graph, output_name):
    index = -1
    for output_info in runtime_graph.output:
        index += 1
        if output_info.name == output_name:
            return index, output_info
    return -1, None


def delete_value_info(runtime_graph, tensor_name):
    try:
        value_index, value_info_item = find_value_info(runtime_graph,
                                                       tensor_name)
        del runtime_graph.value_info[value_index]
    except ValueError:
        value_index, value_info_item = find_output(runtime_graph, tensor_name)
        if value_index == -1:
            raise ValueError(f"Can not find value info {tensor_name}")
        else:
            del runtime_graph.output[value_index]
    return value_info_item


def find_node(runtime_graph, node_name):
    for i in range(len(runtime_graph.node)):
        if runtime_graph.node[i].name == node_name:
            return i, runtime_graph.node[i]
    return None, None


def find_node_by_input(runtime_graph, input_name) -> list:
    node_list = []
    for node_info in runtime_graph.node:
        if input_name in node_info.input:
            node_list.append(node_info)
    return node_list


def find_node_by_output(runtime_graph, output_name) -> list:
    node_list = []
    for node_info in runtime_graph.node:
        if output_name in node_info.output:
            node_list.append(node_info)
    return node_list


def find_initializer_by_name(initializer, input_name):
    for info_item in initializer:
        if info_item.name == input_name:
            return info_item
    return None


def node_adjacent_input_or_output(graph, node):
    for node_input in node.input:
        for input_item in graph.input:
            if input_item.name == node_input:
                return True
    for node_output in node.output:
        for output_item in graph.output:
            if output_item.name == node_output:
                return True
    return False


# If the node to be deleted has an input/output
# relationship with other nodes, it cannot be deleted
def node_related_other_node_input_and_output(graph, node):
    input_related = False
    output_related = False
    for node_item in graph.node:
        # Loop through all nodes, and query whether the node input
        # matches the output of the node to be deleted
        for node_item_input in node_item.input:
            if node_item_input in node.output:
                output_related = True
                break
        # Loop through all nodes, and query whether the node output
        # matches the input of the node to be deleted
        for node_item_output in node_item.output:
            if node_item_output in node.input:
                input_related = True
                break
    return input_related and output_related


def remove_value_info(graph, value_name):
    for value_info_index in range(len(graph.value_info)):
        if graph.value_info[value_info_index].name == value_name:
            del graph.value_info[value_info_index]


def model_input_connects_to_multiple_nodes(graph, model_input):
    if not model_input:
        return False
    count = 0
    for node_item in graph.node:
        for input_item in node_item.input:
            if input_item == model_input.name:
                count += 1
    return count > 1


def replace_model_input(graph, old_name, new_name):
    logging.debug(f"replace model input name {old_name} with {new_name}")
    input_index, model_input = find_input(graph, old_name)
    graph.input[input_index].name = new_name


def check_layer(graph, node) -> str:
    """check if node is the first layer or last layer"""
    for _output in graph.output:
        if _output.name == node.output[0]:
            return 'output'

    for _input in graph.input:
        if _input.name == node.input[0]:
            return 'input'


def keep_output_or_input(graph, old_node: str) -> None:
    """keep model output or input name"""
    if check_layer(graph, old_node) == 'output':
        for input in old_node.input:
            replace_output(graph, input, old_node.output[0])
    elif check_layer(graph, old_node) == 'input':
        for output in old_node.output:
            replace_input(graph, output, old_node.input[0])
    else:
        logging.error(
            f'target node {old_node.name} is not first or last layer node')
        exit(1)


def replace_input(graph, old_name, new_name):
    logging.debug(f"replace input name {old_name} with {new_name}")
    node_list = find_node_by_input(graph, old_name)
    for node_item in node_list:
        for index, input_name in enumerate(node_item.input):
            if input_name == old_name:
                node_item.input[index] = new_name


def replace_output(graph, old_name, new_name):
    logging.debug(f"replace output name {old_name} with {new_name}")
    node_list = find_node_by_output(graph, old_name)
    for node_item in node_list:
        for index, output_name in enumerate(node_item.output):
            if output_name == old_name:
                node_item.output[index] = new_name


def list_to_str(origin_list):
    if not origin_list:
        return ""
    res_string = ""
    for item in origin_list:
        res_string += str(item)
        res_string += ";"
    return res_string


def construct_json_from_node(node: runtime_pb2, deleted_node: str) -> str:
    node_dict = {}
    if deleted_node:
        node_dict = json.loads(deleted_node)
    node_dict[node.name] = node.op_type

    return json.dumps(node_dict)


class InputDataType(Enum):
    UNDEFINED = 0
    S8 = 1
    U8 = 2
    S32 = 3
    U32 = 4
    F32 = 5
    Gray = 6
    NV12 = 7
    YUV444 = 8
    BGR = 9
    RGB = 10
    BGRP = 11
    RGBP = 12
    NV12_SEPARATE = 13
    S64 = 14
    U64 = 15
    F64 = 16
    S16 = 17
    U16 = 18
    F16 = 19
    S4 = 20
    U4 = 21


class DataType(Enum):
    UNDEFINED = 0
    FLOAT = 1
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


tensor_datatype_to_input_datatype = {
    DataType.INT8: InputDataType.S8,
    DataType.UINT8: InputDataType.U8,
    DataType.UINT16: InputDataType.U16,
    DataType.INT16: InputDataType.S16,
    DataType.FLOAT16: InputDataType.F16,
    DataType.INT32: InputDataType.S32,
    DataType.UINT32: InputDataType.U32,
    DataType.FLOAT: InputDataType.F32,
    DataType.INT64: InputDataType.S64,
    DataType.UINT64: InputDataType.U64,
    DataType.DOUBLE: InputDataType.F64
}


class BinModelInfo:
    def __init__(self, model):
        self.model = model
        self._bin_sess = None

        self.set_model()

    def set_model(self):
        try:
            self._bin_sess = HbBinRuntime(bin_model=self.model)
        except Exception:
            raise ValueError(f"Exception in loading {self.model} model")

    def get_march(self) -> str:
        return self._bin_sess.get_march()

    def get_input_type_rt(self) -> list:
        return self._bin_sess.get_input_type_rts()

    def get_input_layout_rt(self) -> list:
        return self._bin_sess.get_input_layout_rts()

    def get_input_batch(self) -> list:
        return self._bin_sess.get_input_batchs()

    def get_input_name(self) -> list:
        return self._bin_sess.get_input_names()

    def get_model_build_version(self) -> str:
        model_info = self._bin_sess.get_model_info()
        return model_info.get("BUILDER_VERSION", "").strip()

    def get_input_shapes(self) -> list:
        return self._bin_sess.get_input_shapes()

    def get_type_of_node_to_deleted(self) -> list:
        deleted_node_type_list = []
        model_info = self._bin_sess.get_model_info()
        remove_node_type = model_info.get("REMOVE_NODE_TYPE", None)
        if remove_node_type and isinstance(remove_node_type, str):
            for i in remove_node_type.split(','):
                deleted_node_type_list.append(i.split("'")[1])

        deleted_json = model_info.get("DELETED_NODE_INFO", None)
        if deleted_json:
            deleted_node_type_list += list(
                dict(json.loads(deleted_json)).values())
        return list(set(deleted_node_type_list))


class OnnxModelInfo:
    def __init__(self, model):
        self.model = model
        self._onnx_sess = None

        self.set_model()

    def set_model(self):
        try:
            self._onnx_sess = HB_ONNXRuntime(model_file=self.model,
                                             input_batch=1)
        except Exception as e:
            raise ValueError(f"The analysis of model {self._onnx_sess} "
                             f"is not supported temporarily") from e

    def get_march(self) -> str:
        return ""

    def get_input_type_rt(self) -> list:
        # TODO：
        _list = []
        for input_type in self._onnx_sess.input_types:
            if input_type == onnx_proto.TensorProto.DataType.FLOAT:
                _list.append("featuremap")
            else:
                _list.append("")
        return _list

    def get_input_layout_rt(self) -> list:
        return []

    def get_input_batch(self) -> list:
        return []

    def get_input_name(self) -> list:
        return self._onnx_sess.input_names

    def get_input_shapes(self) -> list:
        return self._onnx_sess.input_shapes


class ModelInfo:
    def __init__(self, model):
        self.model = model
        self.model_object = None

        self.set_model_object()

    def set_model_object(self):
        if self.model.endswith(".bin"):
            self.model_object = BinModelInfo(self.model)
        elif self.model.endswith(".onnx"):
            self.model_object = OnnxModelInfo(self.model)
        else:
            raise ValueError(f"The analysis of model {self.model} "
                             f"is not supported temporarily")

    def get_input_name(self) -> list:
        return self.model_object.get_input_name()

    def check_node_is_deleted_for_verifier(self):
        deleted_node_list = self.model_object.get_type_of_node_to_deleted()
        unsupported_type_list = [
            "Quantize", "Cast", "Reshape", "Softmax", "Transpose"
        ]
        intersection_list = list(
            set(deleted_node_list) & set(unsupported_type_list))
        if intersection_list:
            raise ValueError(
                f"{self.model} model, the tool will not support inference for "
                f"this model if nodes of types {intersection_list} "
                "are removed.")

    def get_base_info_for_verifier(self) -> dict:
        march = self.model_object.get_march()
        input_name_list = self.model_object.get_input_name()
        input_type_rt_list = self.model_object.get_input_type_rt()
        input_layout_rt_list = self.model_object.get_input_layout_rt()

        input_batch_list = self.model_object.get_input_batch()

        _dict = {}
        for index, input_name in enumerate(input_name_list):
            _dict[input_name] = {
                "march":
                    march,
                "input_type_rt":
                    input_type_rt_list[index] if input_type_rt_list else "",
                "input_layout_rt":
                    input_layout_rt_list[index]
                    if input_layout_rt_list else "",
                "input_batch":
                    input_batch_list[index] if input_batch_list else "",
            }
        return _dict

    def get_input_shapes(self) -> dict:
        _dict = {}
        input_name_list = self.model_object.get_input_name()
        input_shape_list = self.model_object.get_input_shapes()

        for index, input_name in enumerate(input_name_list):
            _dict[input_name] = input_shape_list[index]

        return _dict
