# Copyright (c) 2022 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

# flake8: noqa

import logging
import struct
import onnx.onnx_pb as onnx_pb2
from onnx.onnx_pb import ValueInfoProto
from onnx.onnx_pb import TensorProto
from struct import unpack

from horizon_tc_ui.config import mapper_consts
from horizon_tc_ui.config.mapper_conf_parser import get_list_from_txt
from horizon_tc_ui.hbdtort import layout_util
from horizon_tc_ui.hbdtort import runtime_pb2
from horizon_tc_ui.utils.model_utils import find_tensor
from horizon_tc_ui.utils.tool_utils import get_input_batch

HORIZONRT_BUILDER_VERSION_KEY = 'BUILDER_VERSION'

# logger = logging.getLogger('runtime_logger')
# logger.setLevel(logging.DEBUG)

attribute_type_dict = {
    0: "UNDEFINED",
    1: "FLOAT",
    2: "INT",
    3: "STRING",
    4: "TENSOR",
    5: "GRAPH",
    6: "FLOATS",
    7: "INTS",
    8: "STRINGS",
    9: "TENSORS",
    10: "GRAPHS",
    11: "SPARSE_TENSOR",
    12: "SPARSE_TENSORS",
}


def AttributeNumInfoCheck(op_type, attribute_num, num):
    if attribute_num != num:
        raise ValueError(
            "node {%s} is invalid, its attribute num should be {%d}, actually given {%d}"
            % (op_type, num, attribute_num))


def AttributeTypeInfoCheck(op_type, attribute_type, type):
    if attribute_type != type:
        raise ValueError(
            "node {%s} is invalid, its attribute type should be {%s}, actually given {%s}"
            % (op_type, attribute_type_dict[type],
               attribute_type_dict[attribute_type]))


def GetTensorShape(op_type, tensor):
    tensor_shape = []
    if isinstance(tensor, ValueInfoProto):
        tensor_shape = [e.dim_value for e in tensor.type.tensor_type.shape.dim]
    elif isinstance(tensor, TensorProto):
        tensor_shape = [e for e in tensor.dims]
    else:
        raise ValueError(
            "node {%s} is invalid, its proto type is not support" % (op_type))
    return tensor_shape


def GetTensorType(op_type, tensor):
    tensor_type = 0
    if isinstance(tensor, ValueInfoProto):
        tensor_type = tensor.type.tensor_type.elem_type
    elif isinstance(tensor, TensorProto):
        tensor_type = tensor.data_type
    else:
        raise ValueError(
            "node {%s} is invalid, its proto type is not support" % (op_type))
    return tensor_type


def convert_leaky_relu(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'LeakyRelu'
    attribute_num = len(onnx_node.attribute)
    if attribute_num > 1:
        raise ValueError(
            "node {%s} is invalid, its attribute length should be <= 1,"
            " actually given {%d}" % (onnx_node.op_type, attribute_num))
    if attribute_num == 1:
        AttributeTypeInfoCheck(onnx_node.op_type, onnx_node.attribute[0].type,
                               onnx_pb2.AttributeProto.FLOAT)
        runtime_node_attribute = runtime_node.attribute.add()
        runtime_node_attribute.name = 'alpha'
        runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
        runtime_node_attribute.f = onnx_node.attribute[0].f

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_hardsigmoid(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'HardSigmoid'
    for attribute in onnx_node.attribute:
        if attribute.name == 'alpha':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'alpha'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute.f = attribute.f
        elif attribute.name == 'beta':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'beta'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute.f = attribute.f

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_selu(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Selu'
    for attribute in onnx_node.attribute:
        if attribute.name == 'alpha':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'alpha'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute.f = attribute.f
        elif attribute.name == 'gamma':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'gamma'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute.f = attribute.f

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_thresholded_relu(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ThresholdedRelu'
    for attribute in onnx_node.attribute:
        if attribute.name == 'alpha':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'alpha'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute.f = attribute.f

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_lrn(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'LRN'
    for attribute in onnx_node.attribute:
        if attribute.name == 'alpha':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'alpha'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute.f = attribute.f
        elif attribute.name == 'beta':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'beta'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute.f = attribute.f
        elif attribute.name == 'bias':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'bias'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute.f = attribute.f
        elif attribute.name == 'size':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'size'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INT)
            runtime_node_attribute.i = attribute.i
        else:
            raise ValueError('Not support this attribute=%s' % attribute.name)

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type])
    shape = GetTensorShape(onnx_node.op_type, tensor)
    if len(shape) != 4:
        raise ValueError(
            "LRN currently only support 4-D tensor, give rank is =%d" %
            len(shape))


# 由于model_convert那边的SpaceToDepth和onnx官网的名字不同，需要实现两个op转换函数
def convert_onnx_space_to_depth(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'SpaceToDepth'
    for attribute in onnx_node.attribute:
        if attribute.name == 'blocksize':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'block_height'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attribute.i
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'block_width'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attribute.i
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INT)
        else:
            raise ValueError('Not support this attribute=%s' % attribute.name)


def convert_space_to_depth(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'SpaceToDepth'
    for attribute in onnx_node.attribute:
        if attribute.name == 'block_height':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'block_height'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INT)
            runtime_node_attribute.i = attribute.i
        elif attribute.name == 'block_width':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'block_width'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INT)
            runtime_node_attribute.i = attribute.i

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_depth_to_space(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'DepthToSpace'
    for attribute in onnx_node.attribute:
        if attribute.name == 'blocksize':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'block_size'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INT)
            runtime_node_attribute.i = attribute.i
        elif attribute.name == 'mode':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'mode'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.STRING
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.STRING)
            runtime_node_attribute.s = attribute.s
        else:
            raise ValueError('DepthToSpace not support this attribute=%s' %
                             attribute.name)

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_reshape(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = onnx_node.op_type


def convert_concat(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = onnx_node.op_type
    AttributeNumInfoCheck(onnx_node.op_type, len(onnx_node.attribute), 1)
    AttributeTypeInfoCheck(onnx_node.op_type, onnx_node.attribute[0].type,
                           onnx_pb2.AttributeProto.INT)
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'dimension'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = onnx_node.attribute[0].i
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)


def convert_batch_norm(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'BatchNormalization'
    for attribute in onnx_node.attribute:
        if attribute.name == 'epsilon':
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'epsilon'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            runtime_node_attribute.f = attribute.f

    ## input[i]
    for index in range(len(onnx_node.input)):
        _, tensor = find_tensor(onnx_graph, onnx_node.input[index])
        elem_type = GetTensorType(onnx_node.op_type, tensor)
        if op_data_type_dict[elem_type] != 'FLOAT':
            raise ValueError(onnx_node.op_type +
                             ' currently only support FLOAT '
                             'but gives %s' % op_data_type_dict[elem_type])


def convert_instance_norm(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'InstanceNormalization'
    for attribute in onnx_node.attribute:
        if attribute.name == 'epsilon':
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'epsilon'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            runtime_node_attribute.f = attribute.f

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_max_pool(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'MaxPool'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'indices'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    if len(onnx_node.output) == 2:
        runtime_node_attribute.i = 1
    else:
        runtime_node_attribute.i = 0
    for attribute in onnx_node.attribute:
        if attribute.name == 'ceil_mode':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'ceil_mode'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INT)
            if attribute.i:
                runtime_node_attribute.i = attribute.i
            else:
                runtime_node_attribute.i = 0
        elif attribute.name == 'kernel_shape':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'kernel_shape'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INTS)
            for i in range(len(attribute.ints)):
                runtime_node_attribute.ints.append(attribute.ints[i])
        elif attribute.name == 'pads':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'pads'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INTS)
            if (len(attribute.ints) != 4 and len(attribute.ints) != 6):
                raise ValueError("node {%s} is invalid, its attribute num "
                                 "should be 4 or 6, actually given {%d}" %
                                 (onnx_node.op_type, len(attribute.ints)))
            for val in attribute.ints:
                runtime_node_attribute.ints.append(val)
        elif attribute.name == 'strides':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'strides'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INTS)
            for i in range(len(attribute.ints)):
                runtime_node_attribute.ints.append(attribute.ints[i])
        elif attribute.name == 'dilations':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'dilate'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INTS)
            for val in attribute.ints:
                # 目前支持1*1的，后续会支持通用大小
                if val != 1:
                    raise ValueError("MaxPool dilation only support 1*1")
                runtime_node_attribute.ints.append(val)
        else:
            raise ValueError('Not support this attribute=%s' % attribute.name)


def convert_average_pool(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'AveragePool'
    for attribute in onnx_node.attribute:
        if attribute.name == 'count_include_pad':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'count_include_pad'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INT)
            runtime_node_attribute.i = attribute.i
        elif attribute.name == 'ceil_mode':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'ceil_mode'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INT)
            runtime_node_attribute.i = attribute.i
        elif attribute.name == 'kernel_shape':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'kernel_shape'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INTS)
            for i in range(len(attribute.ints)):
                runtime_node_attribute.ints.append(attribute.ints[i])
        elif attribute.name == 'auto_pad':
            runtime_node_attribute = runtime_node.attribute.add()
            if attribute.s not in [
                    b'NOTSET', b'SAME_UPPER', b'SAME_LOWER', b'VALID'
            ]:
                raise ValueError('AveragePool not support this auto_pad=%s' %
                                 attribute.s)
            runtime_node_attribute.name = 'auto_pad'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.STRING
            runtime_node_attribute.s = attribute.s
        elif attribute.name == 'pads':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'pads'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INTS)
            if (len(attribute.ints) != 4 and len(attribute.ints) != 6):
                raise ValueError("node {%s} is invalid, its attribute num "
                                 "should be 4 or 6, actually given {%d}" %
                                 (onnx_node.op_type, len(attribute.ints)))
            for val in attribute.ints:
                runtime_node_attribute.ints.append(val)
        elif attribute.name == 'strides':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'strides'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INTS)
            for i in range(len(attribute.ints)):
                runtime_node_attribute.ints.append(attribute.ints[i])
        else:
            raise ValueError('Not support this attribute=%s' % attribute.name)


def convert_conv(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Conv'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'bias_term'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    if len(onnx_node.input) == 2:
        runtime_node_attribute.i = 0
    else:
        runtime_node_attribute.i = 1

    for attribute in onnx_node.attribute:
        if attribute.name == 'dilations':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'dilate'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INTS)
            for i in range(len(attribute.ints)):
                runtime_node_attribute.ints.append(attribute.ints[i])
        elif attribute.name == 'group':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'num_group'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INT)
            runtime_node_attribute.i = attribute.i
        elif attribute.name == 'pads':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'pad'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INTS)
            if len(attribute.ints) == 6:
                if attribute.ints[0] != attribute.ints[3] or attribute.ints[
                        1] != attribute.ints[4] or attribute.ints[
                            2] != attribute.ints[5]:
                    raise ValueError(
                        "node {%s} is invalid, its pads attribute should be "
                        "satisfy pads[0] == pads[3] and pads[1] == pads[4] and "
                        "pads[2] == pads[5], "
                        "pads: {%d}, {%d}, {%d}, {%d} {%d}, {%d}" %
                        (onnx_node.op_type, attribute.ints[0],
                         attribute.ints[1], attribute.ints[2],
                         attribute.ints[3], attribute.ints[4],
                         attribute.ints[5]))
                runtime_node_attribute.ints.append(attribute.ints[0])
                runtime_node_attribute.ints.append(attribute.ints[1])
                runtime_node_attribute.ints.append(attribute.ints[2])
            elif len(attribute.ints) == 4:
                if attribute.ints[0] != attribute.ints[2] or attribute.ints[
                        1] != attribute.ints[3]:
                    raise ValueError(
                        "node {%s} is invalid, its pads attribute should be "
                        "satisfy pads[0] == pads[2] and pads[1] == pads[3], "
                        "pads: {%d}, {%d}, {%d}, {%d}" %
                        (onnx_node.op_type, attribute.ints[0],
                         attribute.ints[1], attribute.ints[2],
                         attribute.ints[3]))
                runtime_node_attribute.ints.append(attribute.ints[0])
                runtime_node_attribute.ints.append(attribute.ints[1])
            elif len(attribute.ints) == 2:
                if attribute.ints[0] != attribute.ints[1]:
                    raise ValueError(
                        "node {%s} is invalid, its pads attribute should be "
                        "satisfy pads[0] == pads[1], pads: {%d}, {%d}" %
                        (onnx_node.op_type, attribute.ints[0],
                         attribute.ints[1]))
                runtime_node_attribute.ints.append(attribute.ints[0])
            else:
                raise ValueError("node {%s} is invalid, its attribute num "
                                 "should be {2} or {4}, actually given {%d}" %
                                 (onnx_node.op_type, len(attribute.ints)))
        elif attribute.name == 'strides':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'stride'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INTS)
            for i in range(len(attribute.ints)):
                runtime_node_attribute.ints.append(attribute.ints[i])
        elif attribute.name == 'kernel_shape':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'kernel'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INTS)
            for i in range(len(attribute.ints)):
                runtime_node_attribute.ints.append(attribute.ints[i])
        else:
            raise ValueError('Not support this attribute=%s' % attribute.name)


def convert_transpose(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = "Transpose"
    AttributeNumInfoCheck(onnx_node.op_type, len(onnx_node.attribute), 1)
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'perm'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
    AttributeTypeInfoCheck(onnx_node.op_type, onnx_node.attribute[0].type,
                           onnx_pb2.AttributeProto.INTS)
    for i in range(len(onnx_node.attribute[0].ints)):
        runtime_node_attribute.ints.append(onnx_node.attribute[0].ints[i])

    # 适配horizonrt对输出node的处理，horizonrt里默认输出node是nchw,
    # 根据输出node的data_format属性判断是不是nhwc。
    if onnx_node.attribute[0].ints == [0, 2, 3, 1]:
        runtime_node_attribute = runtime_node.attribute.add()
        runtime_node_attribute.name = 'output_data_format'
        runtime_node_attribute.type = runtime_pb2.AttributeProto.STRING
        runtime_node_attribute.s = b'NHWC'
    elif onnx_node.attribute[0].ints == [0, 3, 1, 2]:
        runtime_node_attribute = runtime_node.attribute.add()
        runtime_node_attribute.name = 'input_data_format'
        runtime_node_attribute.type = runtime_pb2.AttributeProto.STRING
        runtime_node_attribute.s = b'NHWC'
    else:
        _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
        elem_type = GetTensorType(onnx_node.op_type, tensor)
        if op_data_type_dict[elem_type] != 'FLOAT' and \
           op_data_type_dict[elem_type] != 'INT8' and \
           op_data_type_dict[elem_type] != 'INT32':
            raise ValueError(onnx_node.op_type +
                             ' currently only support FLOAT '
                             ', INT8 and INT32 but gives %s' %
                             op_data_type_dict[elem_type])


def convert_softmax(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = "Softmax"
    attribute_num = len(onnx_node.attribute)
    if attribute_num > 1:
        raise ValueError(
            "node {%s} is invalid, its attribute num should be <= {%d}, actually given {%d}"
            % (onnx_node.op_type, 1, attribute_num))
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'axis'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    if attribute_num == 1:
        AttributeTypeInfoCheck(onnx_node.op_type, onnx_node.attribute[0].type,
                               onnx_pb2.AttributeProto.INT)
        runtime_node_attribute.i = onnx_node.attribute[0].i
    else:
        # opset 10
        runtime_node_attribute.i = 1


def convert_hz_softmax(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = "HzSoftmax"
    AttributeNumInfoCheck(onnx_node.op_type, len(onnx_node.attribute), 1)
    AttributeTypeInfoCheck(onnx_node.op_type, onnx_node.attribute[0].type,
                           onnx_pb2.AttributeProto.INT)
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'axis'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = onnx_node.attribute[0].i

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_hz_rsqrt(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = "HzRsqrt"
    for attribute in onnx_node.attribute:
        if attribute.name == 'epsilon':
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'epsilon'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            runtime_node_attribute.f = attribute.f
        elif attribute.name == 'is_sqrt_add_reciprocal':
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INT)
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'is_sqrt_add_reciprocal'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attribute.i
        else:
            raise ValueError('HzRsqrt not support this attribute=%s' %
                             attribute.name)

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_log_softmax(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = "LogSoftmax"
    for attribute in onnx_node.attribute:
        if attribute.name == 'axis':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axis'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INT)
            runtime_node_attribute.i = attribute.i
        else:
            raise ValueError('Not support this attribute=%s' % attribute.name)

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type])


def broadcast_constraint(onnx_node, runtime_node, onnx_graph):
    _, tensor0 = find_tensor(onnx_graph, onnx_node.input[0])
    shape0 = GetTensorShape(onnx_node.op_type, tensor0)

    _, tensor1 = find_tensor(onnx_graph, onnx_node.input[1])
    shape1 = GetTensorShape(onnx_node.op_type, tensor1)

    # scalar
    condition1 = len(shape0) == 0 or len(shape1) == 0

    # equal shape
    condition2 = shape0 == shape1

    # largest broadcast dim contrait
    condition3 = len(shape0) <= 8 and len(shape1) <= 8

    if (condition1 or condition2 or condition3) == False:
        logging.info('shape0: [%s]' % ('x'.join([str(e) for e in shape0])))
        logging.info('shape1: [%s]' % ('x'.join([str(e) for e in shape1])))
        logging.error("{%s} unsupported broadcast mode." % onnx_node.name)
        raise ValueError(
            "Please confirm that the shape is scalar or the two " +
            "shapes are consistent or the shape is less than 9")


def convert_resize(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = "Upsample"

    # if input_num > 2, use resize11, else resize10
    if len(onnx_node.input) > 2:
        runtime_node_attribute = runtime_node.attribute.add()
        runtime_node_attribute.name = 'resize11'
        runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
        runtime_node_attribute.i = 1

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_inputs'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    for attribute in onnx_node.attribute:
        if attribute.name == 'mode':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'mode'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            if attribute.s == b'nearest':
                runtime_node_attribute.i = 1
            elif attribute.s == b'linear':
                runtime_node_attribute.i = 2
            elif attribute.s == b'cubic':
                runtime_node_attribute.i = 3
            else:
                raise ValueError('Resize not support this mode=%s' %
                                 attribute.s)
        elif attribute.name == 'coordinate_transformation_mode':
            runtime_node_attribute = runtime_node.attribute.add()
            if attribute.s not in [
                    b'half_pixel', b'asymmetric', b"align_corners",
                    b'pytorch_half_pixel'
            ]:
                raise ValueError(
                    'Resize not support this coordinate_transformation_mode=%s'
                    % attribute.s)
            runtime_node_attribute.name = 'coordinate_transformation_mode'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.STRING
            runtime_node_attribute.s = attribute.s
        elif attribute.name == 'cubic_coeff_a':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'cubic_coeff_a'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            runtime_node_attribute.f = attribute.f
        elif attribute.name == 'nearest_mode':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'nearest_mode'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.STRING
            runtime_node_attribute.s = attribute.s
        elif attribute.name == 'exclude_outside':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'exclude_outside'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attribute.i
        else:
            raise ValueError('Resize not support this attribute=%s' %
                             attribute.name)

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    shape = GetTensorShape(onnx_node.op_type, tensor)
    if len(shape) != 4:
        raise ValueError('Not support this rank=%d' % len(shape))


def convert_hz_resize(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = "HzResize"
    for attribute in onnx_node.attribute:
        if attribute.name == 'mode':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'mode'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            # 目前只支持linear模式
            if attribute.s == b'linear':
                runtime_node_attribute.i = 1
            else:
                raise ValueError('Not support this mode=%s' %
                                 onnx_node.attribute[0].s)
        elif attribute.name == 'coordinate_transformation_mode':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'coordinate_transformation_mode'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.STRING
            runtime_node_attribute.s = attribute.s
        else:
            raise ValueError('Not support this attribute=%s' % attribute.name)


def convert_flatten(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Flatten'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'axis'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    if len(onnx_node.attribute) > 1:
        raise ValueError(
            "node {%s} is invalid, its attribute num should be <= {%d}, actually given {%d}"
            % (onnx_node.op_type, 1, len(onnx_node.attribute)))
    if len(onnx_node.attribute):
        AttributeTypeInfoCheck(onnx_node.op_type, onnx_node.attribute[0].type,
                               onnx_pb2.AttributeProto.INT)
        runtime_node_attribute.i = onnx_node.attribute[0].i


def convert_quantize(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Quantize'
    _, tensor_input = find_tensor(onnx_graph, onnx_node.input[0])
    shape_input = GetTensorShape(onnx_node.op_type, tensor_input)

    _, tensor_scale = find_tensor(onnx_graph, onnx_node.input[1])
    shape_scale = GetTensorShape(onnx_node.op_type, tensor_scale)

    per_axis = True if len(shape_scale) == 1 and shape_scale[0] > 1 else False

    for attr in onnx_node.attribute:
        if attr.name == 'data_format':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'input_data_format'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.STRING
            runtime_node_attribute.s = attr.s
        elif attr.name == 'bits':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'bits'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'axis':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axis'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
            if per_axis and (attr.i >= len(shape_input) or attr.i < 0):
                raise ValueError(
                    "axis should be [0, %d], actually given axis=%d" %
                    (len(shape_input) - 1, attr.i))
            if per_axis and (shape_input[attr.i] != shape_scale[0]):
                raise ValueError(
                    "per-axis quantize: scaleLen should be equal "
                    "input_shape[axis], actually given scaleLen = %d, "
                    "input_shape[axis] = input_shape[%d] = %d" %
                    (shape_scale[0], attr.i, shape_input[attr.i]))
        else:
            raise ValueError('Can not recognize attribute name %s' % attr.name)
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)


def convert_dequantize(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Dequantize'
    _, tensor_input = find_tensor(onnx_graph, onnx_node.input[0])
    shape_input = GetTensorShape(onnx_node.op_type, tensor_input)

    _, tensor_scale = find_tensor(onnx_graph, onnx_node.input[1])
    shape_scale = GetTensorShape(onnx_node.op_type, tensor_scale)

    per_axis = True if len(shape_scale) == 1 and shape_scale[0] > 1 else False

    for attr in onnx_node.attribute:
        if attr.name == 'data_format':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'data_format'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.STRING
            runtime_node_attribute.s = attr.s

            runtime_node_attribute1 = runtime_node.attribute.add()
            runtime_node_attribute1.name = 'output_data_format'
            runtime_node_attribute1.type = runtime_pb2.AttributeProto.STRING
            runtime_node_attribute1.s = attr.s
        elif attr.name == 'axis':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axis'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i

            if per_axis and (attr.i >= len(shape_input) or attr.i < 0):
                raise ValueError(
                    "axis should be [0, %d], actually given axis=%d" %
                    (len(shape_input) - 1, attr.i))
            if per_axis and (shape_input[attr.i] != shape_scale[0]):
                raise ValueError(
                    "per-axis dequantize: scaleLen should be equal "
                    "input_shape[axis], actually given scaleLen = %d, "
                    "input_shape[axis] = input_shape[%d] = %d" %
                    (shape_scale[0], attr.i, shape_input[attr.i]))

            runtime_node_attribute1 = runtime_node.attribute.add()
            runtime_node_attribute1.name = 'output_data_format'
            runtime_node_attribute1.type = runtime_pb2.AttributeProto.STRING
            runtime_node_attribute1.s = b'NHWC' if attr.i == 3 else b'NCHW'
        else:
            raise ValueError('Can not recognize attribute name %s' % attr.name)
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)


def convert_hzbpu(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'BPU'
    runtime_node.name = onnx_node.name


# 没有实际对应转换的算子
def convert_prod(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Eltwise'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 0

    # output
    _, tensor = find_tensor(onnx_graph, onnx_node.output[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    shape = GetTensorShape(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type])

    # input[i]
    for index in range(len(onnx_node.input)):
        _, tensor_index = find_tensor(onnx_graph, onnx_node.input[index])
        elem_type_index = GetTensorType(onnx_node.op_type, tensor_index)
        shape_index = GetTensorShape(onnx_node.op_type, tensor_index)
        if elem_type_index != elem_type or shape_index != shape:
            raise ValueError(onnx_node.op_type + " only support elewise calcu")


def convert_sum(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Eltwise'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 1

    # output
    _, tensor = find_tensor(onnx_graph, onnx_node.output[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    shape = GetTensorShape(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type])

    # input[i]
    for index in range(len(onnx_node.input)):
        _, tensor_index = find_tensor(onnx_graph, onnx_node.input[index])
        elem_type_index = GetTensorType(onnx_node.op_type, tensor_index)
        shape_index = GetTensorShape(onnx_node.op_type, tensor_index)
        if elem_type_index != elem_type or shape_index != shape:
            raise ValueError(onnx_node.op_type + " only support elewise calcu")


def convert_sin(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Eltwise'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 3


def convert_sinh(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Eltwise'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 4


def convert_cos(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Eltwise'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 5


def convert_cosh(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Eltwise'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 6


def convert_tan(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Eltwise'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 7


def convert_acos(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Eltwise'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 8


def convert_acosh(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Eltwise'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 9


def convert_asin(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Eltwise'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 10


def convert_asinh(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Eltwise'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 11


def convert_atan(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Eltwise'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 12


def convert_atanh(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Eltwise'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 13


def convert_sqrt(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Eltwise'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 14

    _, tensor = find_tensor(onnx_graph, onnx_node.output[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_reciprocal(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Eltwise'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 16

    _, tensor = find_tensor(onnx_graph, onnx_node.output[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT' and \
       op_data_type_dict[elem_type] != 'DOUBLE':
        raise ValueError(onnx_node.op_type +
                         ' currently only support FLOAT and DOUBLE '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_not(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Eltwise'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 17

    _, tensor = find_tensor(onnx_graph, onnx_node.output[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'BOOL':
        raise ValueError(onnx_node.op_type + ' currently only support BOOL '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_round(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Eltwise'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 18

    _, tensor = find_tensor(onnx_graph, onnx_node.output[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT' and \
       op_data_type_dict[elem_type] != 'DOUBLE':
        raise ValueError(onnx_node.op_type +
                         ' currently only support FLOAT and DOUBLE '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_elu(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Elu'
    if len(onnx_node.attribute):
        AttributeTypeInfoCheck(onnx_node.op_type, onnx_node.attribute[0].type,
                               onnx_pb2.AttributeProto.FLOAT)
        runtime_node_attribute = runtime_node.attribute.add()
        runtime_node_attribute.name = 'alpha_value'
        runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
        runtime_node_attribute.f = onnx_node.attribute[0].f

    _, tensor = find_tensor(onnx_graph, onnx_node.output[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_erf(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = onnx_node.op_type

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT' and \
       op_data_type_dict[elem_type] != 'DOUBLE':
        raise ValueError(onnx_node.op_type +
                         ' currently only support FLOAT and DOUBLE '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_ceil(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = onnx_node.op_type

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT' and op_data_type_dict[
            elem_type] != 'DOUBLE':
        raise ValueError(onnx_node.op_type +
                         ' currently only support FLOAT and DOUBLE '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_neg(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = onnx_node.op_type

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'INT8' and \
       op_data_type_dict[elem_type] != 'INT16' and \
       op_data_type_dict[elem_type] != 'INT32' and \
       op_data_type_dict[elem_type] != 'INT64' and \
       op_data_type_dict[elem_type] != 'FLOAT' and \
       op_data_type_dict[elem_type] != 'DOUBLE':
        raise ValueError(onnx_node.op_type +
                         ' currently only support INT8, INT16'
                         'INT32, INT64, FLOAT and DOUBLE but gives %s' %
                         op_data_type_dict[elem_type])


def convert_none_zero(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = onnx_node.op_type

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT' and \
       op_data_type_dict[elem_type] != 'INT8' and \
       op_data_type_dict[elem_type] != 'INT32':
        raise ValueError(onnx_node.op_type +
                         ' currently only support INT8, INT32'
                         ' and FLOAT but gives %s' %
                         op_data_type_dict[elem_type])

    shape = GetTensorShape(onnx_node.op_type, tensor)
    condition = len(shape) == 1 or len(shape) == 4
    if condition is False:
        raise ValueError(
            "currently only supported 1-D or 4-D. The shape dimension is" +
            + f"{len(shape)}")


def convert_prelu(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = onnx_node.op_type

    _, tensor0 = find_tensor(onnx_graph, onnx_node.input[0])
    shape0 = GetTensorShape(onnx_node.op_type, tensor0)

    _, tensor1 = find_tensor(onnx_graph, onnx_node.input[1])
    shape1 = GetTensorShape(onnx_node.op_type, tensor1)

    # shape相等
    condition1 = shape0 == shape1

    # shape1仅有一个元素
    condition2 = False
    if len(shape1) == 0 or (len(shape1) == 1 and shape1[0] == 1):
        condition2 = True
    else:
        prodsize = 1
        for i in shape1:
            prodsize *= i
        if prodsize == 1:
            condition2 = True

    # 4维度+NCHW排布+N维度值相同+C维度值相同
    condition3 = False
    if len(shape0) == 4 and len(shape1) == 4 and \
       shape0[0] == shape1[0] and shape0[1] == shape1[1]:
        # HxW, 1x1
        if shape1[2] == 1 and shape1[3] == 1:
            condition3 = True
        # HxW, Hx1
        elif shape0[2] == shape1[2]:
            condition3 = shape1[3] == 1
        # HxW, 1xW
        elif shape0[3] == shape1[3]:
            condition3 = shape1[2] == 1

    # shape0是4维度+shape1是3维度+
    condition4 = False
    if len(shape0) == 4 and len(shape1) == 3 and \
       shape0[1] == shape1[0] and shape1[1] == 1 and shape1[2] == 1:
        condition4 = True

    # TODO(ruxin.song): Code optimization and merging
    if (condition1 or condition2 or condition3 or condition4) is False:
        logging.info('shape0: [%s]' % ('x'.join([str(e) for e in shape0])))
        logging.info('shape1: [%s]' % ('x'.join([str(e) for e in shape1])))
        logging.error("{%s} unsupported broadcast mode." % onnx_node.name)
        raise ValueError(
            "Please confirm that the two shapes meet at least one of the" +
            " following conditions:\n" + "1. shape1 have only one element\n" +
            "2. shape0 is the same as shape1\n" +
            "3. The dimension of shape0 is 4, and the dimension of shape1" +
            " is 3. The second dimension of shape0 is equal to the first " +
            "dimension of shape1, and the second and third dimensions of " +
            "shape1 are 1\n" +
            "4. The dimensions of shape0 and shape1 are 4. " +
            "The values of dimensions N and C are the same and at least" +
            "one of the following conditions must be met:\n" +
            "4.1 The H and W dimensions of shape1 are 1\n" +
            "4.2 shape0 and shape1 have the same H dimension and the " +
            "W dimension of shape1 is 1\n" +
            "4.3 The W dimension of shape0 and shape1 is the same and the" +
            " H dimension of shape1 is 1")


def convert_range(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = onnx_node.op_type

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT' and \
       op_data_type_dict[elem_type] != 'INT16' and \
       op_data_type_dict[elem_type] != 'INT32' and \
       op_data_type_dict[elem_type] != 'INT64':
        raise ValueError(onnx_node.op_type +
                         ' currently only support INT16, INT32'
                         ', INT64 and FLOAT but gives %s' %
                         op_data_type_dict[elem_type])


def convert_node_float(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = onnx_node.op_type
    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_where(onnx_node, runtime_node, onnx_graph):
    # Condition
    runtime_node.op_type = onnx_node.op_type
    _, tensor_cond = find_tensor(onnx_graph, onnx_node.input[0])
    shape_cond = GetTensorShape(onnx_node.op_type, tensor_cond)
    elem_type_cond = GetTensorType(onnx_node.op_type, tensor_cond)
    if op_data_type_dict[elem_type_cond] != 'BOOL':
        raise ValueError(onnx_node.op_type + ' [cond] currently only support '
                         'BOOL but gives %s' %
                         op_data_type_dict[elem_type_cond])

    # X
    runtime_node.op_type = onnx_node.op_type
    _, tensor_x = find_tensor(onnx_graph, onnx_node.input[1])
    shape_x = GetTensorShape(onnx_node.op_type, tensor_x)
    elem_type_x = GetTensorType(onnx_node.op_type, tensor_x)
    if op_data_type_dict[elem_type_x] != 'FLOAT' and \
       op_data_type_dict[elem_type_x] != 'INT64':
        raise ValueError(onnx_node.op_type +
                         ' [x] currently only support FLOAT and '
                         'INT64 but gives %s' % op_data_type_dict[elem_type_x])

    # Y
    runtime_node.op_type = onnx_node.op_type
    _, tensor_y = find_tensor(onnx_graph, onnx_node.input[2])
    shape_y = GetTensorShape(onnx_node.op_type, tensor_y)
    elem_type_y = GetTensorType(onnx_node.op_type, tensor_y)
    if op_data_type_dict[elem_type_y] != 'FLOAT' and \
       op_data_type_dict[elem_type_y] != 'INT64':
        raise ValueError(onnx_node.op_type +
                         ' [y] currently only support FLOAT and '
                         'INT64 but gives %s' % op_data_type_dict[elem_type_y])

    # output
    runtime_node.op_type = onnx_node.op_type
    _, tensor_out = find_tensor(onnx_graph, onnx_node.output[0])
    shape_out = GetTensorShape(onnx_node.op_type, tensor_out)

    # shape constraint
    condition1 = False
    if shape_cond == shape_out and (shape_out == shape_x
                                    or shape_out == shape_y):
        if len(shape_x) == 0 or len(shape_y) == 0:
            condition1 = True
        if shape_x == shape_y:
            condition1 = True

    condition2 = False
    if len(shape_cond) == 4 and len(shape_out) == 4 and (
            shape_cond[0] == shape_out[0]):
        condition2 = True
        for i in range(1, len(shape_out)):
            if (shape_cond[i] != shape_out[i] and shape_cond[i] != 1):
                condition2 = False
                break

    if (condition1 or condition2) is False:
        logging.info('shape_cond: [%s]' %
                     ('x'.join([str(e) for e in shape_cond])))
        logging.info('shape_x: [%s]' % ('x'.join([str(e) for e in shape_x])))
        logging.info('shape_y: [%s]' % ('x'.join([str(e) for e in shape_y])))
        logging.info('shape_out: [%s]' % ('x'.join([str(e)
                                                    for e in shape_out])))
        logging.error("{%s} unsupported broadcast mode." % onnx_node.name)
        raise ValueError(
            "Please confirm that the two shapes meet at least one " +
            "of the following conditions:\n" +
            "1. shape_cond is equal to shape_out and shape_out is equal to " +
            "shape_x or shape_y. it has at " +
            "least one of the following conditions:\n" +
            "1.1 The length of shape_x or shape_y is 0\n" +
            "1.2 shape_x is the same as shape_y\n" +
            "2. The dimension of shape_cond and shape_out is 4, " +
            "the first dimension of the two shapes are equal, " +
            "the second dimension of the two shapes are equal " +
            "or the second dimension of shape_cond are 1 " +
            "and at least one of the following conditions is met:\n" +
            "2.1 The third and fourth dimensions of shape_cond are 1\n" +
            "2.2 The third and fourth dimensions of the two shapes are equal\n"
            + "2.3 The third dimension of shape_cond and shape_out is equal" +
            "and the fourth dimension of shape_cond is 1\n" +
            "2.4 The fourth dimension of shape_cond and shape_out is equal" +
            "and the third dimension of shape_cond is 1")


def convert_tile(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = onnx_node.op_type
    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT' and \
       op_data_type_dict[elem_type] != 'INT32' and \
       op_data_type_dict[elem_type] != 'INT64' and \
       op_data_type_dict[elem_type] != 'UINT32' and \
       op_data_type_dict[elem_type] != 'UINT64':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT, '
                         'INT32, INT64, UINT32 and UINT64 but gives %s' %
                         op_data_type_dict[elem_type])


def convert_node(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = onnx_node.op_type


def convert_cast(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = onnx_node.op_type

    support_type_list = [
        'DOUBLE', 'FLOAT', 'BOOL', 'INT64', 'UINT32', 'INT32', 'UINT16',
        'INT16', 'UINT8', 'INT8'
    ]

    # input 约束
    _, tensor_in = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type_in = GetTensorType(onnx_node.op_type, tensor_in)
    if op_data_type_dict[elem_type_in] not in support_type_list:
        raise ValueError(onnx_node.op_type +
                         ' from currently only support DOUBLE, '
                         'FLOAT, BOOL, INT64, UINT32, INT32, UINT16, INT16, '
                         'UINT8 and INT8 but gives %s' %
                         op_data_type_dict[elem_type_in])

    # output约束
    _, tensor_out = find_tensor(onnx_graph, onnx_node.output[0])
    elem_type_out = GetTensorType(onnx_node.op_type, tensor_out)
    if op_data_type_dict[elem_type_out] not in support_type_list:
        raise ValueError(onnx_node.op_type +
                         ' to currently only support DOUBLE, '
                         'FLOAT, BOOL, INT64, UINT32, INT32, UINT16, INT16, '
                         'UINT8 and INT8 but gives %s' %
                         op_data_type_dict[elem_type_out])


def convert_shape(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = onnx_node.op_type


def convert_clip(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Clip'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)

    if len(onnx_node.attribute) == 2:
        for attr in onnx_node.attribute:
            if attr.name == 'max':
                runtime_node_attribute = runtime_node.attribute.add()
                runtime_node_attribute.name = 'max'
                runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
                runtime_node_attribute.f = attr.f
            elif attr.name == 'min':
                runtime_node_attribute = runtime_node.attribute.add()
                runtime_node_attribute.name = 'min'
                runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
                runtime_node_attribute.f = attr.f
            else:
                raise ValueError('Clip not support this attribute=%s' %
                                 attr.name)
        if op_data_type_dict[elem_type] != 'FLOAT':
            raise ValueError(onnx_node.op_type +
                             ' currently only support FLOAT'
                             'but gives %s' % op_data_type_dict[elem_type])

    if op_data_type_dict[elem_type] != 'FLOAT' and \
       op_data_type_dict[elem_type] != 'DOUBLE':
        raise ValueError(onnx_node.op_type +
                         ' currently only support FLOAT and DOUBLE'
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_split(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Split'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_outputs'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.output)

    for attr in onnx_node.attribute:
        if attr.name == 'axis':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axis'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'split':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'split'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.INTS)
            for i in range(len(attr.ints)):
                runtime_node_attribute.ints.append(attr.ints[i])

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_reduce_sum(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Reduction'

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'reduction_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 1

    for attr in onnx_node.attribute:
        if attr.name == 'axes':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axes'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.INTS)
            for val in attr.ints:
                runtime_node_attribute.ints.append(val)


def convert_reduce_sum_square(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Reduction'

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'reduction_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 3

    for attr in onnx_node.attribute:
        if attr.name == 'axes':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axes'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.INTS)
            for val in attr.ints:
                runtime_node_attribute.ints.append(val)


def convert_reduce_mean(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Reduction'

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'reduction_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 4

    for attr in onnx_node.attribute:
        if attr.name == 'axes':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axes'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.INTS)
            for val in attr.ints:
                runtime_node_attribute.ints.append(val)


def convert_reduce_max(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Reduction'

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'reduction_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 5

    for attr in onnx_node.attribute:
        if attr.name == 'axes':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axes'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.INTS)
            for val in attr.ints:
                runtime_node_attribute.ints.append(val)


def convert_reduce_logsum(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Reduction'

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'reduction_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 6

    for attr in onnx_node.attribute:
        if attr.name == 'axes':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axes'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.INTS)
            for val in attr.ints:
                runtime_node_attribute.ints.append(val)


def convert_reduce_min(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Reduction'

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'reduction_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 7

    for attr in onnx_node.attribute:
        if attr.name == 'axes':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axes'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.INTS)
            for val in attr.ints:
                runtime_node_attribute.ints.append(val)


def convert_reduce_prod(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Reduction'

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'reduction_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 8

    for attr in onnx_node.attribute:
        if attr.name == 'axes':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axes'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.INTS)
            for val in attr.ints:
                runtime_node_attribute.ints.append(val)


def convert_gemm(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Gemm'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_inputs'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    for attr in onnx_node.attribute:
        if attr.name == 'alpha':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'alpha'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            runtime_node_attribute.f = attr.f
        elif attr.name == 'beta':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'beta'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            runtime_node_attribute.f = attr.f
        elif attr.name == 'transA':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'transA'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'transB':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'transB'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i

    for index in range(len(onnx_node.input)):
        _, tensor = find_tensor(onnx_graph, onnx_node.input[index])
        elem_type = GetTensorType(onnx_node.op_type, tensor)
        if op_data_type_dict[elem_type] != 'FLOAT':
            raise ValueError(onnx_node.op_type +
                             ' currently only support FLOAT '
                             'but gives %s' % op_data_type_dict[elem_type])


def convert_conv_transpose(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Deconvolution'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'bias_term'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    if len(onnx_node.input) == 2:
        runtime_node_attribute.i = 0
    else:
        runtime_node_attribute.i = 1

    for attribute in onnx_node.attribute:
        if attribute.name == 'dilations':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'dilate'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            if attribute.type != onnx_pb2.AttributeProto.INTS:
                raise ValueError(
                    onnx_node.op_type +
                    ' is invalid, its atrribute %s is not equal onnx_pb2.AttributeProto.INTS'
                    % attribute.name)
            for i in range(len(attribute.ints)):
                runtime_node_attribute.ints.append(attribute.ints[i])
        elif attribute.name == 'group':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'num_group'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            if attribute.type != onnx_pb2.AttributeProto.INT:
                raise ValueError(
                    onnx_node.op_type +
                    ' is invalid, its atrribute %s is not equal onnx_pb2.AttributeProto.INT'
                    % attribute.name)
            runtime_node_attribute.i = attribute.i
        elif attribute.name == 'pads':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'pad'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            if attribute.type != onnx_pb2.AttributeProto.INTS:
                raise ValueError(
                    onnx_node.op_type +
                    ' is invalid, its atrribute %s is not equal onnx_pb2.AttributeProto.INTS'
                    % attribute.name)
            if len(attribute.ints) != 4:
                raise ValueError(
                    onnx_node.op_type +
                    ' is invalid, its atrribute %s length should be 4, actually given %d'
                    % (attribute.name, len(attribute.ints)))
            if (attribute.ints[0] != attribute.ints[2]) or (
                    attribute.ints[1] != attribute.ints[3]):
                raise ValueError(
                    onnx_node.op_type +
                    ' is invalid, its atrribute %s only currently support p[0] == p[2] and p[1] == p[3]'
                    % attribute.name)
            runtime_node_attribute.ints.append(attribute.ints[0])
            runtime_node_attribute.ints.append(attribute.ints[1])
        elif attribute.name == 'strides':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'stride'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            if attribute.type != onnx_pb2.AttributeProto.INTS:
                raise ValueError(
                    onnx_node.op_type +
                    ' is invalid, its atrribute %s is not equal onnx_pb2.AttributeProto.INTS'
                    % attribute.name)
            for i in range(len(attribute.ints)):
                runtime_node_attribute.ints.append(attribute.ints[i])
        elif attribute.name == 'output_padding':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'output_padding'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            if attribute.type != onnx_pb2.AttributeProto.INTS:
                raise ValueError(
                    onnx_node.op_type +
                    ' is invalid, its atrribute %s is not equal onnx_pb2.AttributeProto.INTS'
                    % attribute.name)
            for i in range(len(attribute.ints)):
                runtime_node_attribute.ints.append(attribute.ints[i])


def convert_max_roi_pool(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'RoiPooling'

    for attr in onnx_node.attribute:
        if attr.name == 'pooled_shape':
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.INTS)
            AttributeNumInfoCheck(onnx_node.op_type, len(attr.ints), 2)

            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'pooled_h'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.ints[0]

            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'pooled_w'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.ints[1]
        elif attr.name == 'spatial_scale':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'spatial_scale'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute.f = attr.f


def convert_normalize(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Normalize'

    for attr in onnx_node.attribute:
        if attr.name == 'across_spatial':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'across_spatial'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'channel_shared':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'channel_shared'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'eps':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'eps'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            runtime_node_attribute.f = attr.f


def convert_ps_roi_pooling(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'PsroiPooling'

    for attr in onnx_node.attribute:
        if attr.name == 'group_size':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'group_size'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'output_dim':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'output_dim'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'spatial_scale':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'spatial_scale'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute.f = attr.f


def convert_bbox_decode(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'BboxDecode'

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_inputs'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    for attr in onnx_node.attribute:
        if attr.name == 'stds':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'stds'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOATS
            for i in range(len(attr.floats)):
                runtime_node_attribute.floats.append(attr.floats[i])
        elif attr.name == 'means':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'means'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOATS
            for i in range(len(attr.floats)):
                runtime_node_attribute.floats.append(attr.floats[i])
        elif attr.name == 'feat_stride':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'feat_stride'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'min_size':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'min_size'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute.f = attr.f
        elif attr.name == 'classes':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'classes'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'scales':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'scales'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOATS
            for i in range(len(attr.floats)):
                runtime_node_attribute.floats.append(attr.floats[i])
        elif attr.name == 'ratios':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'ratios'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOATS
            for i in range(len(attr.floats)):
                runtime_node_attribute.floats.append(attr.floats[i])


def convert_nms(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'NMS'

    for attr in onnx_node.attribute:
        if attr.name == 'pre_nms_topn':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'pre_nms_topn'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'post_nms_topn':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'post_nms_topn'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'force_suppressed':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'force_suppressed'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'nms_thresh':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'nms_thresh'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute.f = attr.f
        elif attr.name == 'score_thresh':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'score_thresh'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute.f = attr.f


def convert_mvn(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'MVN'

    for attr in onnx_node.attribute:
        if attr.name == 'normalize_variance':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'normalize_variance'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'across_channels':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'across_channels'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'eps':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'eps'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute.f = attr.f


def convert_argmax(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ArgMax'

    for attr in onnx_node.attribute:
        if attr.name == 'axis':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axis'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i


def convert_argmin(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ArgMin'

    for attr in onnx_node.attribute:
        if attr.name == 'axis':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axis'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i


def convert_topk(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'TopK'

    for attr in onnx_node.attribute:
        if attr.name == 'axis':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axis'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'largest':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'largest'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'sorted':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'sorted'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_axpy(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Axpy'


def convert_maxunpool(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'MaxUnpool'
    for attribute in onnx_node.attribute:
        if attribute.name == 'upsample_h':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'upsample_h'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INT)
            runtime_node_attribute.i = attribute.i
        elif attribute.name == 'upsample_w':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'upsample_w'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INT)
            runtime_node_attribute.i = attribute.i
        elif attribute.name == 'kernel_shape':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'kernel_shape'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INTS)
            for i in range(len(attribute.ints)):
                runtime_node_attribute.ints.append(attribute.ints[i])
        elif attribute.name == 'pads':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'pads'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INTS)
            for i in range(len(attribute.ints)):
                runtime_node_attribute.ints.append(attribute.ints[i])
        elif attribute.name == 'strides':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'strides'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INTS)
            for i in range(len(attribute.ints)):
                runtime_node_attribute.ints.append(attribute.ints[i])
        else:
            raise ValueError('Not support this attribute=%s' % attribute.name)

    if len(onnx_node.input) > 2:
        raise ValueError('Not support output_shape input')

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_crop(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Crop'

    for attr in onnx_node.attribute:
        if attr.name == 'axis':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axis'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'offsets':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'offsets'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.INTS)
            for i in range(len(attr.ints)):
                runtime_node_attribute.ints.append(attr.ints[i])


def convert_bbox2roi(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'BBoxtoRoi'


def convert_crelu(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'CRelu'
    for attr in onnx_node.attribute:
        if attr.name == 'bias_filler':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'bias_filler'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            runtime_node_attribute.f = attr.f


def convert_relux(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ReluX'
    for attr in onnx_node.attribute:
        if attr.name == 'clip_value':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'clip_value'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i


def convert_roi_decode(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'RoiDecode'

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_inputs'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    for attr in onnx_node.attribute:
        if attr.name == 'stds':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'stds'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOATS
            for i in range(len(attr.floats)):
                runtime_node_attribute.floats.append(attr.floats[i])
        elif attr.name == 'means':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'means'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOATS
            for i in range(len(attr.floats)):
                runtime_node_attribute.floats.append(attr.floats[i])
        elif attr.name == 'batch_size':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'batch_size'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.INT)
            runtime_node_attribute.i = attr.i


def convert_pad(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Pad'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_inputs'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)
    for attribute in onnx_node.attribute:
        if attribute.name == 'mode':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'mode'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.STRING
            runtime_node_attribute.s = attribute.s
        elif attribute.name == 'value':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'value'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute.f = attribute.f
        elif attribute.name == 'pads':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'pads'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INTS)
            for val in attribute.ints:
                if (val < 0):
                    raise ValueError("Pad lists not support negtive value." +
                                     f"actually given {val}")
                else:
                    runtime_node_attribute.ints.append(val)

            if len(attribute.ints) == 8:
                if attribute.ints[0] != 0 or attribute.ints[
                        1] != 0 or attribute.ints[4] != 0 or attribute.ints[
                            5] != 0:
                    raise ValueError(
                        'Pad: only support h and w dimension padding')
            elif len(attribute.ints) == 10:
                if attribute.ints[0] != 0 or attribute.ints[
                        1] != 0 or attribute.ints[5] != 0 or attribute.ints[
                            6] != 0:
                    raise ValueError(
                        'Pad: only support h w d dimension padding')
            else:
                raise ValueError(onnx_node.op_type +
                                 " currently only support 4-D and 5-D tensor" +
                                 f"actually given {len(attribute.ints)/2}")

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    shape = GetTensorShape(onnx_node.op_type, tensor)
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type])
    if (len(shape) != 4) and (len(shape) != 5):
        raise ValueError(onnx_node.op_type +
                         " currently only support 4-D and 5-D tensor" +
                         f"actually given {len(shape)}")

    # pad-11
    if len(onnx_node.input) >= 2:
        _, tensor1 = find_tensor(onnx_graph, onnx_node.input[1])
        shape1 = GetTensorShape(onnx_node.op_type, tensor1)
        for dim in shape1:
            if (dim < 0):
                raise ValueError("Pad not support negtive value." +
                                 f"actually given {dim}")


def convert_grid_sample(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'GridSample'

    for attr in onnx_node.attribute:
        if attr.name == 'data_format':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'data_format'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.STRING
            runtime_node_attribute.s = attr.s
        elif attr.name == 'sizes':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'sizes'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            for val in attr.ints:
                runtime_node_attribute.ints.append(val)
        else:
            raise ValueError('GridSample not support this attribute=%s' %
                             attr.name)


def convert_slice(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Slice'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)


def convert_add_broadcast(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ElementWiseBinaryBroadcast'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 0

    try:
        broadcast_constraint(onnx_node, runtime_node, onnx_graph)
    except ValueError as e:
        logging.error("convert_add_broadcast node failed")
        raise e


def convert_max_broadcast(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ElementWiseBinaryBroadcast'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 1

    try:
        broadcast_constraint(onnx_node, runtime_node, onnx_graph)
    except ValueError as e:
        logging.error("convert_max_broadcast node failed")
        raise e


def convert_mul_broadcast(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ElementWiseBinaryBroadcast'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 2

    try:
        broadcast_constraint(onnx_node, runtime_node, onnx_graph)
    except ValueError as e:
        logging.error("convert_mul_broadcast node failed")
        raise e


def convert_div_broadcast(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ElementWiseBinaryBroadcast'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 3

    try:
        broadcast_constraint(onnx_node, runtime_node, onnx_graph)
    except ValueError as e:
        logging.error("convert_div_broadcast node failed")
        raise e


def convert_sub_broadcast(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ElementWiseBinaryBroadcast'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 4

    try:
        broadcast_constraint(onnx_node, runtime_node, onnx_graph)
    except ValueError as e:
        logging.error("convert_sub_broadcast node failed")
        raise e


def convert_pow_broadcast(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ElementWiseBinaryBroadcast'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 5

    # 输入的type必须相等
    _, tensor0 = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type0 = GetTensorType(onnx_node.op_type, tensor0)

    _, tensor1 = find_tensor(onnx_graph, onnx_node.input[1])
    elem_type1 = GetTensorType(onnx_node.op_type, tensor1)

    if elem_type0 != elem_type1:
        raise ValueError(onnx_node.op_type + " X and Y must be equal type")

    try:
        broadcast_constraint(onnx_node, runtime_node, onnx_graph)
    except ValueError as e:
        logging.error("convert_pow_broadcast node failed")
        raise e


def convert_min_broadcast(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ElementWiseBinaryBroadcast'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_args'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 6

    try:
        broadcast_constraint(onnx_node, runtime_node, onnx_graph)
    except ValueError as e:
        logging.error("convert_min_broadcast node failed")
        raise e


def convert_equal_broadcast(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ElementWiseBinaryBroadcast'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 7

    try:
        broadcast_constraint(onnx_node, runtime_node, onnx_graph)
    except ValueError as e:
        logging.error("convert_equal_broadcast node failed")
        raise e


def convert_less_broadcast(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ElementWiseBinaryBroadcast'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 8

    try:
        broadcast_constraint(onnx_node, runtime_node, onnx_graph)
    except ValueError as e:
        logging.error("convert_less_broadcast node failed")
        raise e


def convert_lessorequal_broadcast(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ElementWiseBinaryBroadcast'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 9

    try:
        broadcast_constraint(onnx_node, runtime_node, onnx_graph)
    except ValueError as e:
        logging.error("convert_lessorequal_broadcast node failed")
        raise e


def convert_greater_broadcast(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ElementWiseBinaryBroadcast'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 10

    try:
        broadcast_constraint(onnx_node, runtime_node, onnx_graph)
    except ValueError as e:
        logging.error("convert_greater_broadcast node failed")
        raise e


def convert_greaterorequal_broadcast(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ElementWiseBinaryBroadcast'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 11

    try:
        broadcast_constraint(onnx_node, runtime_node, onnx_graph)
    except ValueError as e:
        logging.error("convert_greaterorequal_broadcast node failed")
        raise e


def convert_and_broadcast(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ElementWiseBinaryBroadcast'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 12

    try:
        broadcast_constraint(onnx_node, runtime_node, onnx_graph)
    except ValueError as e:
        logging.error("convert_and_broadcast node failed")
        raise e


def convert_or_broadcast(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ElementWiseBinaryBroadcast'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 13

    try:
        broadcast_constraint(onnx_node, runtime_node, onnx_graph)
    except ValueError as e:
        logging.error("convert_or_broadcast node failed")
        raise e


def convert_mod_broadcast(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ElementWiseBinaryBroadcast'
    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'eltwise_type'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = 14

    for attribute in onnx_node.attribute:
        if attribute.name == 'fmod':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'fmod'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attribute.i
        else:
            raise ValueError('Not support this attribute=%s' % attribute.name)

    try:
        broadcast_constraint(onnx_node, runtime_node, onnx_graph)
    except ValueError as e:
        logging.error("convert_or_broadcast node failed")
        raise e


def convert_cumsum(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'CumSum'

    for attr in onnx_node.attribute:
        if attr.name == 'exclusive':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'exclusive'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'reverse':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'reverse'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i

    ## [0]输入
    _, tensor0 = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type0 = GetTensorType(onnx_node.op_type, tensor0)
    if op_data_type_dict[elem_type0] not in [
            'UINT32', 'INT32', 'UINT64', 'INT64', 'FLOAT16', 'FLOAT', 'DOUBLE'
    ]:
        raise ValueError(
            onnx_node.op_type +
            ' currently only support UINT32 , INT32 , UINT64 , INT64 , FLOAT16 , FLOAT , DOUBLE '
            'but gives %s' % op_data_type_dict[elem_type0])

    ## [1]输入
    _, tensor1 = find_tensor(onnx_graph, onnx_node.input[1])
    elem_type1 = GetTensorType(onnx_node.op_type, tensor1)
    if op_data_type_dict[elem_type1] != 'INT32':
        raise ValueError(onnx_node.op_type + ' currently only support FLOAT '
                         'but gives %s' % op_data_type_dict[elem_type1])


def copy_tensor_to_runtime_node(onnx_node, runtime_node):
    for attr in onnx_node.attribute:
        if attr.name == 'value':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'value'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.TENSOR
            # get dims data
            for i in range(len(attr.t.dims)):
                runtime_node_attribute.t.shape_type.dim.append(attr.t.dims[i])
            runtime_node_attribute.t.shape_type.elem_type = attr.t.data_type
            # get data type
            elem_type = attr.t.data_type

            # Constant
            if runtime_node.op_type == 'Constant':
                if op_data_type_dict[elem_type] != 'FLOAT':
                    raise ValueError(onnx_node.op_type +
                                     ' currently only support FLOAT '
                                     'but gives %s' %
                                     op_data_type_dict[elem_type])
            # ConstantOfShape
            if runtime_node.op_type == 'ConstantOfShape':
                if op_data_type_dict[elem_type] != 'FLOAT' and \
                   op_data_type_dict[elem_type] != 'INT32' and \
                   op_data_type_dict[elem_type] != 'INT8':
                    raise ValueError(onnx_node.op_type +
                                     ' currently only support'
                                     'FLOAT, INT32 and INT8 but gives %s' %
                                     op_data_type_dict[elem_type])

            # judge is_raw_data
            raw_data_len = len(attr.t.raw_data)
            raw_data_buf = []
            if raw_data_len > 0:
                value = attr.t.raw_data
                # raw_data is not support string
                if elem_type == 1 or elem_type == 6:
                    for data_index in range(raw_data_len // 4):
                        raw_data_buf.append(value[data_index:data_index + 4])
                elif elem_type == 7 or elem_type == 11 or elem_type == 13:
                    for data_index in range(raw_data_len // 8):
                        raw_data_buf.append(value[data_index:data_index + 8])
                else:
                    raise ValueError(f"Not support type: {elem_type}")

                if elem_type == 1:
                    for i in range(len(raw_data_buf)):
                        runtime_node_attribute.t.float_data.append(
                            unpack("<f", raw_data_buf[i])[0])
                elif elem_type == 6:
                    for i in range(len(raw_data_buf)):
                        runtime_node_attribute.t.int32_data.append(
                            unpack("<i", raw_data_buf[i])[0])
                elif elem_type == 7:
                    for i in range(len(raw_data_buf)):
                        runtime_node_attribute.t.int64_data.append(
                            unpack("<q", raw_data_buf[i])[0])
                elif elem_type == 11:
                    for i in range(len(raw_data_buf)):
                        runtime_node_attribute.t.double_data.append(
                            unpack("<d", raw_data_buf[i])[0])
                elif elem_type == 13:
                    for i in range(len(raw_data_buf)):
                        runtime_node_attribute.t.uint64_data.append(
                            unpack("<Q", raw_data_buf[i])[0])
            else:
                if elem_type == 1:
                    logging.info(len(attr.t.float_data))
                    for index in range(len(attr.t.float_data)):
                        runtime_node_attribute.t.float_data.append(
                            attr.t.float_data[index])
                elif elem_type == 6:
                    for index in range(len(attr.t.int32_data)):
                        runtime_node_attribute.t.int32_data.append(
                            attr.t.int32_data[index])
                elif elem_type == 7:
                    for index in range(len(attr.t.int64_data)):
                        runtime_node_attribute.t.int64_data.append(
                            attr.t.int64_data[index])
                elif elem_type == 8:
                    for index in range(len(attr.t.string_data)):
                        runtime_node_attribute.t.string_data.append(
                            attr.t.string_data[index])
                elif elem_type == 11:
                    for index in range(len(attr.t.double_data)):
                        runtime_node_attribute.t.double_data.append(
                            attr.t.double_data[index])
                elif elem_type == 13:
                    for index in range(len(attr.t.uint64_data)):
                        runtime_node_attribute.t.uint64_data.append(
                            attr.t.uint64_data[index])
                else:
                    raise ValueError(f"Not support type: {elem_type}")


def convert_constant(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Constant'
    try:
        copy_tensor_to_runtime_node(onnx_node, runtime_node)
    except ValueError as e:
        logging.error("convert_constant node failed")
        raise e


def convert_const_of_shape(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ConstantOfShape'
    try:
        copy_tensor_to_runtime_node(onnx_node, runtime_node)
    except ValueError as e:
        logging.error("convert_const_of_shape node failed")
        raise e


def convert_gather(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Gather'

    for attr in onnx_node.attribute:
        if attr.name == 'axis':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axis'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT' and \
       op_data_type_dict[elem_type] != 'UINT32' and \
       op_data_type_dict[elem_type] != 'INT8' and \
       op_data_type_dict[elem_type] != 'INT32' and \
       op_data_type_dict[elem_type] != 'INT64' and \
       op_data_type_dict[elem_type] != 'UINT32' and \
       op_data_type_dict[elem_type] != 'UINT64':
        raise ValueError(onnx_node.op_type +
                         'input currently only support FLOAT, UINT32, '
                         'INT8, INT32, INT64, UINT32 and UINT64 but gives %s' %
                         op_data_type_dict[elem_type])


def convert_gather_nd(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'GatherND'

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT' and \
       op_data_type_dict[elem_type] != 'INT8' and \
       op_data_type_dict[elem_type] != 'INT32':
        raise ValueError(onnx_node.op_type +
                         ' currently only support FLOAT, INT8'
                         ' and INT32 but gives %s' %
                         op_data_type_dict[elem_type])


def convert_hz_channel_shuffle(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'HzChannelShuffle'

    for attr in onnx_node.attribute:
        runtime_node_attribute = runtime_node.attribute.add()
        runtime_node_attribute.name = 'group'
        runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
        runtime_node_attribute.i = attr.i


def convert_scatter_elements(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ScatterElements'

    for attr in onnx_node.attribute:
        if attr.name == 'axis':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axis'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i

    _, tensor0 = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type0 = GetTensorType(onnx_node.op_type, tensor0)
    if op_data_type_dict[elem_type0] != 'FLOAT' and \
       op_data_type_dict[elem_type0] != 'INT32' and \
       op_data_type_dict[elem_type0] != 'INT8':
        raise ValueError(onnx_node.op_type +
                         '[0] currently only support FLOAT,'
                         ' INT32 and INT8 but gives %s' %
                         op_data_type_dict[elem_type0])

    _, tensor2 = find_tensor(onnx_graph, onnx_node.input[2])
    elem_type2 = GetTensorType(onnx_node.op_type, tensor2)
    if op_data_type_dict[elem_type2] != 'FLOAT' and \
       op_data_type_dict[elem_type2] != 'INT32' and \
       op_data_type_dict[elem_type2] != 'INT8':
        raise ValueError(onnx_node.op_type +
                         '[2] currently only support FLOAT,'
                         ' INT32 and INT8 but gives %s' %
                         op_data_type_dict[elem_type2])

    _, tensor1 = find_tensor(onnx_graph, onnx_node.input[1])
    elem_type1 = GetTensorType(onnx_node.op_type, tensor1)
    if op_data_type_dict[elem_type1] != 'INT32':
        raise ValueError(onnx_node.op_type +
                         '[1] currently only support INT32,'
                         ' but gives %s' % op_data_type_dict[elem_type1])


def convert_scatter_nd(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = onnx_node.op_type

    _, tensor0 = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type0 = GetTensorType(onnx_node.op_type, tensor0)
    if op_data_type_dict[elem_type0] != 'FLOAT' and \
       op_data_type_dict[elem_type0] != 'INT32' and \
       op_data_type_dict[elem_type0] != 'INT8':
        raise ValueError(onnx_node.op_type +
                         '[0] currently only support FLOAT,'
                         ' INT32 and INT8 but gives %s' %
                         op_data_type_dict[elem_type0])

    _, tensor2 = find_tensor(onnx_graph, onnx_node.input[2])
    elem_type2 = GetTensorType(onnx_node.op_type, tensor2)
    if op_data_type_dict[elem_type2] != 'FLOAT' and \
       op_data_type_dict[elem_type2] != 'INT32' and \
       op_data_type_dict[elem_type2] != 'INT8':
        raise ValueError(onnx_node.op_type +
                         '[2] currently only support FLOAT,'
                         ' INT32 and INT8 but gives %s' %
                         op_data_type_dict[elem_type2])


def convert_rnn(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'RNN'
    runtime_node_attribute_i = runtime_node.attribute.add()
    runtime_node_attribute_i.name = 'input_num_args'
    runtime_node_attribute_i.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute_i.i = len(onnx_node.input)

    runtime_node_attribute_o = runtime_node.attribute.add()
    runtime_node_attribute_o.name = 'output_num_args'
    runtime_node_attribute_o.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute_o.i = len(onnx_node.output)

    for attribute in onnx_node.attribute:
        if attribute.name == 'activation_alpha':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'activation_alpha'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOATS
            for val in attribute.floats:
                runtime_node_attribute.floats.append(val)
        elif attribute.name == 'activation_beta':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'activation_beta'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOATS
            for val in attribute.floats:
                runtime_node_attribute.floats.append(val)
        elif attribute.name == 'activations':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'activations'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.STRINGS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.STRINGS)
            for val in attribute.strings:
                runtime_node_attribute.strings.append(val)
        elif attribute.name == 'clip':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'clip'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute.f = attribute.f
        elif attribute.name == 'direction':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'direction'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.STRING
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.STRING)
            runtime_node_attribute.s = attribute.s
            if attribute.s != b'forward':
                raise ValueError('RNN not support this direction=%s' %
                                 attribute.s)
        elif attribute.name == 'hidden_size':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'hidden_size'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INT)
            runtime_node_attribute.i = attribute.i

    for index in range(len(onnx_node.input)):
        if onnx_node.input[index] != '':
            _, tensor = find_tensor(onnx_graph, onnx_node.input[index])
            elem_type = GetTensorType(onnx_node.op_type, tensor)
            if op_data_type_dict[elem_type] != 'FLOAT':
                raise ValueError(onnx_node.op_type +
                                 ' currently only support FLOAT '
                                 'but gives %s' % op_data_type_dict[elem_type])
        else:
            runtime_node_attribute_i.i -= 1

    if runtime_node_attribute_i.i > 3:
        raise ValueError("RNN unsupport input num=%d" %
                         runtime_node_attribute_i.i)

    for index in range(len(onnx_node.output)):
        if onnx_node.output[index] != '':
            _, tensor = find_tensor(onnx_graph, onnx_node.output[index])
            elem_type = GetTensorType(onnx_node.op_type, tensor)
            if op_data_type_dict[elem_type] != 'FLOAT':
                raise ValueError(onnx_node.op_type +
                                 ' currently only support FLOAT '
                                 'but gives %s' % op_data_type_dict[elem_type])
            shape = GetTensorShape(onnx_node.op_type, tensor)
            if len(shape) != 3:
                raise ValueError(onnx_node.op_type +
                                 ' currently only support rank = 3,'
                                 'but gives rank = %s' % len(shape))
        else:
            runtime_node_attribute_o.i -= 1


def convert_lstm(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Lstm'
    runtime_node_attribute_i = runtime_node.attribute.add()
    runtime_node_attribute_i.name = 'input_num_args'
    runtime_node_attribute_i.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute_i.i = len(onnx_node.input)

    runtime_node_attribute_o = runtime_node.attribute.add()
    runtime_node_attribute_o.name = 'output_num_args'
    runtime_node_attribute_o.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute_o.i = len(onnx_node.output)

    for attribute in onnx_node.attribute:
        if attribute.name == 'activation_alpha':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'activation_alpha'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOATS
            for val in attribute.floats:
                runtime_node_attribute.floats.append(val)
        elif attribute.name == 'activation_beta':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'activation_beta'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOATS
            for val in attribute.floats:
                runtime_node_attribute.floats.append(val)
        elif attribute.name == 'activations':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'activations'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.STRINGS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.STRINGS)
            for val in attribute.strings:
                runtime_node_attribute.strings.append(val)
        elif attribute.name == 'clip':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'clip'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute.f = attribute.f
        elif attribute.name == 'direction':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'direction'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.STRING
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.STRING)
            runtime_node_attribute.s = attribute.s
            if attribute.s != b'forward':
                raise ValueError('LSTM not support this direction=%s' %
                                 attribute.s)
        elif attribute.name == 'hidden_size':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'hidden_size'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INT)
            runtime_node_attribute.i = attribute.i
        elif attribute.name == 'input_forget':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'input_forget'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INT)
            runtime_node_attribute.i = attribute.i

    # input
    for index in range(len(onnx_node.input)):
        if onnx_node.input[index] != '':
            _, tensor = find_tensor(onnx_graph, onnx_node.input[index])
            elem_type = GetTensorType(onnx_node.op_type, tensor)
            if op_data_type_dict[elem_type] != 'FLOAT':
                raise ValueError(onnx_node.op_type +
                                 ' currently only support FLOAT '
                                 'but gives %s' % op_data_type_dict[elem_type])
        else:
            runtime_node_attribute_i.i -= 1

    input_case1 = runtime_node_attribute_i.i == 3
    input_case2 = runtime_node_attribute_i.i == 4 and onnx_node.input[3] != ''
    input_case3 = runtime_node_attribute_i.i == 8
    if not (input_case1 or input_case2 or input_case3):
        raise ValueError("LSTM unsupport input num=%d" %
                         runtime_node_attribute_i.i)

    # output
    for index in range(len(onnx_node.output)):
        if onnx_node.output[index] != '':
            _, tensor = find_tensor(onnx_graph, onnx_node.output[index])
            elem_type = GetTensorType(onnx_node.op_type, tensor)
            if op_data_type_dict[elem_type] != 'FLOAT':
                raise ValueError(onnx_node.op_type +
                                 ' currently only support FLOAT '
                                 'but gives %s' % op_data_type_dict[elem_type])
        else:
            runtime_node_attribute_o.i -= 1


def convert_gru(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'Gru'
    runtime_node_attribute_i = runtime_node.attribute.add()
    runtime_node_attribute_i.name = 'input_num_args'
    runtime_node_attribute_i.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute_i.i = len(onnx_node.input)

    runtime_node_attribute_o = runtime_node.attribute.add()
    runtime_node_attribute_o.name = 'output_num_args'
    runtime_node_attribute_o.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute_o.i = len(onnx_node.output)

    for attribute in onnx_node.attribute:
        if attribute.name == 'activation_alpha':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'activation_alpha'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOATS
            for val in attribute.floats:
                runtime_node_attribute.floats.append(val)
        elif attribute.name == 'activation_beta':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'activation_beta'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOATS
            for val in attribute.floats:
                runtime_node_attribute.floats.append(val)
        elif attribute.name == 'activations':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'activations'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.STRINGS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.STRINGS)
            for val in attribute.strings:
                runtime_node_attribute.strings.append(val)
        elif attribute.name == 'clip':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'clip'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.FLOAT)
            runtime_node_attribute.f = attribute.f
        elif attribute.name == 'direction':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'direction'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.STRING
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.STRING)
            runtime_node_attribute.s = attribute.s
            if attribute.s != b'forward':
                raise ValueError('GRU not support this direction=%s' %
                                 attribute.s)
        elif attribute.name == 'hidden_size':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'hidden_size'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INT)
            runtime_node_attribute.i = attribute.i
        elif attribute.name == 'linear_before_reset':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'linear_before_reset'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INT)
            runtime_node_attribute.i = attribute.i

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'optional_input_flag'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
    optional_input_flag = [0, 0, 0]
    for index in range(len(onnx_node.input)):
        if index > 2:
            if onnx_node.input[index] == '':
                optional_input_flag[index - 3] = 0
            else:
                optional_input_flag[index - 3] = 1
    for val in optional_input_flag:
        runtime_node_attribute.ints.append(val)

    # input[i]
    for index in range(len(onnx_node.input)):
        if onnx_node.input[index] == '':
            runtime_node_attribute_i.i -= 1
        else:
            _, tensor = find_tensor(onnx_graph, onnx_node.input[index])
            elem_type = GetTensorType(onnx_node.op_type, tensor)
            if op_data_type_dict[elem_type] != 'FLOAT':
                raise ValueError(onnx_node.op_type +
                                 ' currently only support FLOAT '
                                 'but gives %s' % op_data_type_dict[elem_type])

    # output[i]
    for index in range(len(onnx_node.output)):
        if onnx_node.output[index] == '':
            runtime_node_attribute_o.i -= 1
        else:
            _, tensor = find_tensor(onnx_graph, onnx_node.output[index])
            elem_type = GetTensorType(onnx_node.op_type, tensor)
            if op_data_type_dict[elem_type] != 'FLOAT':
                raise ValueError(onnx_node.op_type +
                                 ' currently only support FLOAT '
                                 'but gives %s' % op_data_type_dict[elem_type])


# 与其他reduce算子保持一致，未添加onnx的keepdims属性
def convert_reducelogsumexp(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ReduceLogSumExp'
    for attr in onnx_node.attribute:
        if attr.name == 'axes':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axes'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.INTS)
            for val in attr.ints:
                runtime_node_attribute.ints.append(val)

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT' and \
       op_data_type_dict[elem_type] != 'DOUBLE':
        raise ValueError(onnx_node.op_type +
                         ' currently only support FLOAT and DOUBLE '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_eyelike(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'EyeLike'
    for attr in onnx_node.attribute:
        if attr.name == 'k':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'k'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.INT)
            runtime_node_attribute.i = attr.i
        elif attr.name == 'dtype':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'dtype'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.INT)
            runtime_node_attribute.i = attr.i


# 与其他reduce算子保持一致，未添加onnx的keepdims属性
def convert_reducel1(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ReduceL1'
    for attr in onnx_node.attribute:
        if attr.name == 'axes':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axes'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.INTS)
            for val in attr.ints:
                runtime_node_attribute.ints.append(val)


# 与其他reduce算子保持一致，未添加onnx的keepdims属性
def convert_reducel2(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ReduceL2'
    for attr in onnx_node.attribute:
        if attr.name == 'axes':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axes'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attr.type,
                                   onnx_pb2.AttributeProto.INTS)
            for val in attr.ints:
                runtime_node_attribute.ints.append(val)


# onnx 不存在scaledtanh op
def convert_scaledtanh(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ScaledTanh'
    for attribute in onnx_node.attribute:
        if attribute.name == 'alpha':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'alpha'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            runtime_node_attribute.f = attribute.f
        elif attribute.name == 'beta':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'beta'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            runtime_node_attribute.f = attribute.f
        else:
            raise ValueError('ScaledTanh not support this attribute=%s' %
                             attribute.name)


def convert_reverse_sequence(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'ReverseSequence'
    for attribute in onnx_node.attribute:
        if attribute.name == 'batch_axis':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'batch_axis'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attribute.i
        if attribute.name == 'time_axis':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'time_axis'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attribute.i


def convert_lp_normalization(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'LpNormalization'
    for attribute in onnx_node.attribute:
        if attribute.name == 'p':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'p'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attribute.i
        if attribute.name == 'axis':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axis'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attribute.i

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT' and \
       op_data_type_dict[elem_type] != 'DOUBLE':
        raise ValueError(onnx_node.op_type +
                         ' currently only support FLOAT and DOUBLE'
                         'but gives %s' % op_data_type_dict[elem_type])


# nchw和nhwc属性
def convert_lp_pool(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'LpPool'
    for attribute in onnx_node.attribute:
        if attribute.name == 'kernel_shape':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'kernel_shape'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INTS)
            for val in attribute.ints:
                runtime_node_attribute.ints.append(val)
        if attribute.name == 'strides':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'strides'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INTS)
            for val in attribute.ints:
                runtime_node_attribute.ints.append(val)
        if attribute.name == 'pads':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'pads'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INTS)
            for val in attribute.ints:
                runtime_node_attribute.ints.append(val)
        if attribute.name == 'p':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'p'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attribute.i

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT' and \
       op_data_type_dict[elem_type] != 'DOUBLE':
        raise ValueError(onnx_node.op_type +
                         ' currently only support FLOAT and DOUBLE'
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_randomuniform(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'RandomUniform'
    for attribute in onnx_node.attribute:
        if attribute.name == 'high':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'high'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            runtime_node_attribute.f = attribute.f
        if attribute.name == 'low':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'low'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            runtime_node_attribute.f = attribute.f
        if attribute.name == 'shape':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'shape'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
            AttributeTypeInfoCheck(onnx_node.op_type, attribute.type,
                                   onnx_pb2.AttributeProto.INTS)
            for val in attribute.ints:
                runtime_node_attribute.ints.append(val)
        if attribute.name == 'seed':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'seed'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            runtime_node_attribute.f = attribute.f
        if attribute.name == 'dtype':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'dtype'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attribute.i


def convert_randomuniform_like(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'RandomUniformLike'
    for attribute in onnx_node.attribute:
        if attribute.name == 'high':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'high'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            runtime_node_attribute.f = attribute.f
        if attribute.name == 'low':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'low'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            runtime_node_attribute.f = attribute.f
        if attribute.name == 'seed':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'seed'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            runtime_node_attribute.f = attribute.f
        if attribute.name == 'dtype':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'dtype'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attribute.i

    _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
    elem_type = GetTensorType(onnx_node.op_type, tensor)
    if op_data_type_dict[elem_type] != 'FLOAT' and \
       op_data_type_dict[elem_type] != 'DOUBLE':
        raise ValueError(onnx_node.op_type +
                         ' currently only support FLOAT and DOUBLE '
                         'but gives %s' % op_data_type_dict[elem_type])


def convert_gather_elements(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'GatherElements'
    for attr in onnx_node.attribute:
        if attr.name == 'axis':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axis'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i


def convert_global_lp_pool(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'GlobalLpPool'
    for attr in onnx_node.attribute:
        if attr.name == 'p':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'p'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i


def convert_onehot(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'OneHot'
    for attr in onnx_node.attribute:
        if attr.name == 'axis':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axis'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i


def convert_roialign(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'RoiAlign'
    for attr in onnx_node.attribute:
        if attr.name == 'mode':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'mode'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.STRING
            runtime_node_attribute.s = attr.s
        elif attr.name == 'output_height':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'output_height'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'output_width':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'output_width'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'sampling_ratio':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'sampling_ratio'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i
        elif attr.name == 'spatial_scale':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'spatial_scale'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
            runtime_node_attribute.f = attr.f


def convert_dequantize_linear(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'DequantizeLinear'

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_inputs'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    for attr in onnx_node.attribute:
        if attr.name == 'axis':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axis'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i


def convert_quantize_linear(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'QuantizeLinear'

    runtime_node_attribute = runtime_node.attribute.add()
    runtime_node_attribute.name = 'num_inputs'
    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
    runtime_node_attribute.i = len(onnx_node.input)

    for attr in onnx_node.attribute:
        if attr.name == 'axis':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axis'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i


def convert_dequantize_filter(onnx_node, runtime_node, onnx_graph):
    runtime_node.op_type = 'DequantizeFilter'
    logging.info("HorizonRT do not support HzDequantizeFilter, "
                 "please add DequantizeFilter in remove_node_type in your"
                 " config file or directly remove it using hb_model_modifier!")


runtime_node2onnx_node = {
    "Relu": convert_node_float,
    "LeakyRelu": convert_leaky_relu,
    "HzSpaceToDepth": convert_space_to_depth,
    "SpaceToDepth": convert_onnx_space_to_depth,
    "DepthToSpace": convert_depth_to_space,
    "Reshape": convert_reshape,
    "Concat": convert_concat,
    "BatchNormalization": convert_batch_norm,
    "InstanceNormalization": convert_instance_norm,
    "MaxPool": convert_max_pool,
    "Conv": convert_conv,
    "Transpose": convert_transpose,
    "Softmax": convert_softmax,
    "HzSoftmax": convert_hz_softmax,
    "LogSoftmax": convert_log_softmax,
    "GlobalAveragePool": convert_node,
    "GlobalMaxPool": convert_node,
    "Add": convert_add_broadcast,
    "Max": convert_max_broadcast,
    "Mul": convert_mul_broadcast,
    "Div": convert_div_broadcast,
    "Sub": convert_sub_broadcast,
    "Pow": convert_pow_broadcast,
    "Min": convert_min_broadcast,
    "Equal": convert_equal_broadcast,
    "Less": convert_less_broadcast,
    "LessOrEqual": convert_lessorequal_broadcast,
    "Greater": convert_greater_broadcast,
    "GreaterOrEqual": convert_greaterorequal_broadcast,
    "And": convert_and_broadcast,
    "Or": convert_or_broadcast,
    "Mod": convert_mod_broadcast,
    "Resize": convert_resize,
    "HzResize11": convert_hz_resize,
    "AveragePool": convert_average_pool,
    "Flatten": convert_flatten,
    "HzQuantize": convert_quantize,
    "HzDequantize": convert_dequantize,
    "HzBpuHBM": convert_hzbpu,
    "LRN": convert_lrn,
    "Dropout": convert_node,
    "Sigmoid": convert_node_float,
    "Exp": convert_node_float,
    "Tanh": convert_node_float,
    "Log": convert_node_float,
    "Elu": convert_elu,
    "Abs": convert_node_float,
    "PRelu": convert_prelu,
    "Clip": convert_clip,
    "Split": convert_split,
    "Sign": convert_node_float,
    "ReduceSum": convert_reduce_sum,
    "ReduceSumSquare": convert_reduce_sum_square,
    "ReduceMean": convert_reduce_mean,
    "ReduceMax": convert_reduce_max,
    "ReduceLogSum": convert_reduce_logsum,
    "ReduceMin": convert_reduce_min,
    "ReduceProd": convert_reduce_prod,
    "Gemm": convert_gemm,
    "ConvTranspose": convert_conv_transpose,
    "MaxRoiPool": convert_max_roi_pool,
    "HzNormalize": convert_normalize,
    "HzPSRoiPooling": convert_ps_roi_pooling,
    "HzBBoxDecode": convert_bbox_decode,
    "HzBBoxtoRoi": convert_bbox2roi,
    "HzNonMaxSuppression": convert_nms,
    "HzMeanVarianceNormalization": convert_mvn,
    "HzAxpy": convert_axpy,
    "Cast": convert_cast,
    "ArgMax": convert_argmax,
    "ArgMin": convert_argmin,
    "TopK": convert_topk,
    "HzMaxUnpool": convert_maxunpool,
    "HzCrop": convert_crop,
    "HzCRelu": convert_crelu,
    "HzReluX": convert_relux,
    "HzRoiDecode": convert_roi_decode,
    "Identity": convert_node,
    "Squeeze": convert_node,
    "Unsqueeze": convert_node,
    "Pad": convert_pad,
    "HzGridSample": convert_grid_sample,
    "Slice": convert_slice,
    "Floor": convert_node_float,
    "Ceil": convert_ceil,
    "MatMul": convert_node_float,
    "Softplus": convert_node_float,
    "Where": convert_where,
    "HardSigmoid": convert_hardsigmoid,
    "HardSwish": convert_node,
    "Selu": convert_selu,
    "ThresholdedRelu": convert_thresholded_relu,
    "Softsign": convert_node_float,
    "CumSum": convert_cumsum,
    "Shape": convert_shape,
    "Constant": convert_constant,
    "ConstantOfShape": convert_const_of_shape,
    "Range": convert_range,
    "Tile": convert_tile,
    "Gather": convert_gather,
    "GatherND": convert_gather_nd,
    "ScatterND": convert_scatter_nd,
    "HzChannelShuffle": convert_hz_channel_shuffle,
    "Sum": convert_sum,
    "Sin": convert_sin,
    "Sinh": convert_sinh,
    "Cos": convert_cos,
    "Cosh": convert_cosh,
    "Tan": convert_tan,
    "Acos": convert_acos,
    "Acosh": convert_acosh,
    "Asin": convert_asin,
    "Asinh": convert_asinh,
    "Atan": convert_atan,
    "Atanh": convert_atanh,
    "Sqrt": convert_sqrt,
    "Reciprocal": convert_reciprocal,
    "Not": convert_not,
    "Round": convert_round,
    "Expand": convert_node,
    "RNN": convert_rnn,
    "ScatterElements": convert_scatter_elements,
    "LSTM": convert_lstm,
    "GRU": convert_gru,
    "Neg": convert_neg,
    "ReduceLogSumExp": convert_reducelogsumexp,
    "EyeLike": convert_eyelike,
    "Erf": convert_erf,
    "ReduceL1": convert_reducel1,
    "ReduceL2": convert_reducel2,
    "ScaledTanh": convert_scaledtanh,
    "ReverseSequence": convert_reverse_sequence,
    "LpNormalization": convert_lp_normalization,
    "LpPool": convert_lp_pool,
    "RandomUniform": convert_randomuniform,
    "RandomUniformLike": convert_randomuniform_like,
    "GatherElements": convert_gather_elements,
    "GlobalLpPool": convert_global_lp_pool,
    "OneHot": convert_onehot,
    "RoiAlign": convert_roialign,
    "Tanh": convert_node_float,
    "QuantizeLinear": convert_quantize_linear,
    "DequantizeLinear": convert_dequantize_linear,
    "HzRsqrt": convert_hz_rsqrt,
    "HzDequantizeFilter": convert_dequantize_filter,
}

four_dim_node_set = {
    "GlobalAveragePool", "GlobalMaxPool", "DepthToSpace", "SpaceToDepth",
    "GlobalLpPool", "LpPool"
}


def make_dequantizefilter_node(onnx_graph, onnx_node, runtime_graph,
                               runtime_node, initializer_names_set,
                               dequantizefilter_initializers,
                               dequantizefilter_initializers_name):
    # add input
    runtime_node.input.append(onnx_node.input[0])
    runtime_node.input.append(onnx_node.input[1])

    # get input channels attr
    input_channels = []
    for attr in onnx_node.attribute:
        if attr.name == 'input_channels':
            for val in attr.ints:
                input_channels.append(val)
        elif attr.name == 'axis':
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'axis'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = attr.i

    # add axis attr
    if len(runtime_node.attribute) == 0:
        runtime_node_attribute = runtime_node.attribute.add()
        runtime_node_attribute.name = 'axis'
        runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
        runtime_node_attribute.i = 3

    # get scale input
    initializer_list = []
    for onnx_node_input in onnx_node.input:
        if onnx_node_input != onnx_node.input[0]:
            for onnx_initializer in onnx_graph.initializer:
                if onnx_initializer.name == onnx_node_input:
                    initializer_list.append(onnx_initializer)
                    dequantizefilter_initializers.append(onnx_initializer)
                    dequantizefilter_initializers_name.append(
                        onnx_initializer.name)

    # check scale num
    if len(initializer_list) != len(input_channels):
        raise ValueError("DequantizeFilter scale num mismatch")

    # add scale name
    runtime_initializer = runtime_graph.initializer.add()
    runtime_initializer.name = initializer_list[0].name
    initializer_names_set.add(initializer_list[0].name)

    # add scale shape
    dim_value = 4
    for dim in input_channels:
        dim_value += dim
    runtime_initializer.shape_type.dim.append(dim_value)

    # add scale dtype
    runtime_initializer.shape_type.elem_type = \
        onnx_tensor_type2runtime_tensor_type[initializer_list[0].data_type]

    # add scale data with 1.0
    runtime_initializer.float_data.append(1.0)
    runtime_initializer.float_data.append(1.0)
    runtime_initializer.float_data.append(1.0)
    runtime_initializer.float_data.append(1.0)

    # modify multi scales to one scale
    for i in range(len(initializer_list)):
        assert initializer_list[i].segment.begin == 0 and initializer_list[
            i].segment.end == 0
        assert len(initializer_list[i].external_data) == 0
        assert initializer_list[
            i].data_location == onnx_pb2.TensorProto.DEFAULT

        # only support scale
        if initializer_list[i].data_type != onnx_pb2.TensorProto.FLOAT:
            raise ValueError("DequantizeFilter only support scale Initializer")

        if len(initializer_list[i].float_data) == 1:
            if len(initializer_list[i].float_data) != 0:
                for channel in range(input_channels[i]):
                    runtime_initializer.float_data.append(
                        initializer_list[i].float_data[0])
            else:
                raise ValueError("DequantizeFilter scale data error")

        else:
            if len(initializer_list[i].float_data) != input_channels[i]:
                raise ValueError(
                    "DequantizeFilter per channel dequantize, channels error.")


def make_nodes(onnx_graph, runtime_graph, initializer_names_set,
               dequantizefilter_initializers,
               dequantizefilter_initializers_name):

    invalid_operators = []
    error_operators = []

    for onnx_node in onnx_graph.node:
        runtime_node = runtime_graph.node.add()

        # check pooling 4 dim input
        if onnx_node.op_type in four_dim_node_set:
            _, tensor = find_tensor(onnx_graph, onnx_node.input[0])
            shape = GetTensorShape(onnx_node.op_type, tensor)
            if (len(shape) != 4):
                raise ValueError(onnx_node.op_type +
                                 " only support 4 dim input")

        if onnx_node.op_type == 'HzBpuHBM':
            # onnx model bpu node has a useless input PACKED_HBM_MODEL, so ignore it.
            if len(onnx_node.input) <= 1:
                raise ValueError(
                    "node {%s} is invalid, its input num should be > {%d}, actually given {%d}"
                    % (onnx_node.op_type, 1, len(onnx_node.input)))
            for i in range(len(onnx_node.input) - 1):
                runtime_node.input.append(onnx_node.input[i])
        elif onnx_node.op_type == 'HzDequantizeFilter':
            make_dequantizefilter_node(onnx_graph, onnx_node, runtime_graph,
                                       runtime_node, initializer_names_set,
                                       dequantizefilter_initializers,
                                       dequantizefilter_initializers_name)
        else:
            for onnx_node_input in onnx_node.input:
                runtime_node.input.append(onnx_node_input)

        for onnx_node_output in onnx_node.output:
            runtime_node.output.append(onnx_node_output)
        runtime_node.name = onnx_node.name

        if onnx_node.op_type == 'PyOp':
            runtime_node.op_type = 'Custom'
            runtime_node_attribute = runtime_node.attribute.add()
            runtime_node_attribute.name = 'num_args'
            runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
            runtime_node_attribute.i = len(onnx_node.input)
            for attribute in onnx_node.attribute:
                runtime_node_attribute = runtime_node.attribute.add()
                if attribute.name == 'class_name':
                    runtime_node_attribute.name = 'custom_op_name'
                    runtime_node_attribute.type = runtime_pb2.AttributeProto.STRING
                    runtime_node_attribute.s = attribute.s + b"_HR_API"
                    continue
                runtime_node_attribute.name = attribute.name
                if attribute.type == onnx_pb2.AttributeProto.INT:
                    runtime_node_attribute.type = runtime_pb2.AttributeProto.INT
                    runtime_node_attribute.i = attribute.i
                elif attribute.type == onnx_pb2.AttributeProto.INTS:
                    runtime_node_attribute.type = runtime_pb2.AttributeProto.INTS
                    for val in attribute.ints:
                        runtime_node_attribute.ints.append(val)
                elif attribute.type == onnx_pb2.AttributeProto.FLOAT:
                    runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOAT
                    runtime_node_attribute.f = attribute.f
                elif attribute.type == onnx_pb2.AttributeProto.FLOATS:
                    runtime_node_attribute.type = runtime_pb2.AttributeProto.FLOATS
                    for val in attribute.floats:
                        runtime_node_attribute.floats.append(val)
                elif attribute.type == onnx_pb2.AttributeProto.STRING:
                    runtime_node_attribute.type = runtime_pb2.AttributeProto.STRING
                    runtime_node_attribute.s = attribute.s
                elif attribute.type == onnx_pb2.AttributeProto.STRINGS:
                    runtime_node_attribute.type = runtime_pb2.AttributeProto.STRINGS
                    for val in attribute.strings:
                        runtime_node_attribute.strings.append(val)
                elif attribute.type == onnx_pb2.AttributeProto.TENSOR:
                    runtime_node_attribute.type = runtime_pb2.AttributeProto.TENSOR
                    runtime_node_attribute.t = attribute.t
                elif attribute.type == onnx_pb2.AttributeProto.TENSORS:
                    runtime_node_attribute.type = runtime_pb2.AttributeProto.TENSORS
                    for val in attribute.tensors:
                        runtime_node_attribute.tensors.append(val)
                else:
                    raise ValueError(
                        'Custom op not support this attribute type=%s' %
                        attribute.type)
        elif onnx_node.op_type in runtime_node2onnx_node.keys():
            try:
                runtime_node2onnx_node[onnx_node.op_type](onnx_node,
                                                          runtime_node,
                                                          onnx_graph)
            except Exception as e:
                error_operators.append((onnx_node.name, onnx_node.op_type, e))
        else:
            invalid_operators.append(onnx_node.op_type)
    if invalid_operators:
        raise ValueError('HorizonRT not support these cpu operators: ' +
                         " ".join(set(invalid_operators)))

    if error_operators:
        for node_name, node_type, message in error_operators:
            logging.error(f"The node name is {node_name} "
                          f"and the node type is {node_type}. "
                          "Constraints exist")
            logging.error(f'error info: {message}')

        raise ValueError("The CPU operator constraint is abnormal")


onnx_tensor_type2runtime_tensor_type = {
    onnx_pb2.TensorProto.FLOAT: runtime_pb2.TensorTypeProto.FLOAT,
    onnx_pb2.TensorProto.UINT8: runtime_pb2.TensorTypeProto.UINT8,
    onnx_pb2.TensorProto.INT8: runtime_pb2.TensorTypeProto.INT8,
    onnx_pb2.TensorProto.UINT16: runtime_pb2.TensorTypeProto.UINT16,
    onnx_pb2.TensorProto.INT16: runtime_pb2.TensorTypeProto.INT16,
    onnx_pb2.TensorProto.INT32: runtime_pb2.TensorTypeProto.INT32,
    onnx_pb2.TensorProto.INT64: runtime_pb2.TensorTypeProto.INT64,
    onnx_pb2.TensorProto.STRING: runtime_pb2.TensorTypeProto.STRING,
    onnx_pb2.TensorProto.FLOAT16: runtime_pb2.TensorTypeProto.FLOAT16,
    onnx_pb2.TensorProto.DOUBLE: runtime_pb2.TensorTypeProto.DOUBLE,
    onnx_pb2.TensorProto.UINT32: runtime_pb2.TensorTypeProto.UINT32,
    onnx_pb2.TensorProto.UINT64: runtime_pb2.TensorTypeProto.UINT64,
    onnx_pb2.TensorProto.BOOL: runtime_pb2.TensorTypeProto.BOOL
}


def make_initializers(onnx_graph, runtime_graph, initializer_names_set,
                      dequantizefilter_initializers):
    for onnx_initializer in onnx_graph.initializer:
        if onnx_initializer not in dequantizefilter_initializers:
            runtime_initializer = runtime_graph.initializer.add()
            initializer_names_set.add(onnx_initializer.name)
            runtime_initializer.name = onnx_initializer.name

            assert onnx_initializer.segment.begin == 0 and \
                onnx_initializer.segment.end == 0
            assert len(onnx_initializer.external_data) == 0
            assert onnx_initializer.data_location == \
                onnx_pb2.TensorProto.DEFAULT

            for dim in onnx_initializer.dims:
                runtime_initializer.shape_type.dim.append(dim)

            data_type = onnx_initializer.data_type
            runtime_initializer.shape_type.elem_type = \
                onnx_tensor_type2runtime_tensor_type[data_type]
            if onnx_initializer.data_type == onnx_pb2.TensorProto.FLOAT:
                if len(onnx_initializer.float_data) != 0:
                    for val in onnx_initializer.float_data:
                        runtime_initializer.float_data.append(val)
                else:
                    assert len(onnx_initializer.raw_data) % 4 == 0
                    data_iter = struct.iter_unpack('f' * 1,
                                                   onnx_initializer.raw_data)
                    for val in data_iter:
                        runtime_initializer.float_data.append(val[0])
            elif onnx_initializer.data_type == onnx_pb2.TensorProto.INT32:
                if len(onnx_initializer.int32_data) != 0:
                    for val in onnx_initializer.int32_data:
                        runtime_initializer.int32_data.append(val)
                else:
                    assert len(onnx_initializer.raw_data) % 4 == 0
                    data_iter = struct.iter_unpack('i' * 1,
                                                   onnx_initializer.raw_data)
                    for val in data_iter:
                        runtime_initializer.int32_data.append(val[0])
            elif onnx_initializer.data_type == onnx_pb2.TensorProto.INT16:
                if len(onnx_initializer.int32_data) != 0:
                    for val in onnx_initializer.int32_data:
                        runtime_initializer.int32_data.append(val)
                else:
                    assert len(onnx_initializer.raw_data) % 2 == 0
                    data_iter = struct.iter_unpack('h' * 1,
                                                   onnx_initializer.raw_data)
                    for val in data_iter:
                        runtime_initializer.int32_data.append(val[0])
            elif onnx_initializer.data_type == onnx_pb2.TensorProto.INT8:
                if len(onnx_initializer.int32_data) != 0:
                    for val in onnx_initializer.int32_data:
                        runtime_initializer.int32_data.append(val)
                else:
                    data_iter = struct.iter_unpack('b' * 1,
                                                   onnx_initializer.raw_data)
                    for val in data_iter:
                        runtime_initializer.int32_data.append(val[0])
            elif onnx_initializer.data_type == onnx_pb2.TensorProto.UINT16:
                if len(onnx_initializer.int32_data) != 0:
                    for val in onnx_initializer.int32_data:
                        runtime_initializer.int32_data.append(val)
                else:
                    assert len(onnx_initializer.raw_data) % 2 == 0
                    data_iter = struct.iter_unpack('H' * 1,
                                                   onnx_initializer.raw_data)
                    for val in data_iter:
                        runtime_initializer.int32_data.append(val[0])
            elif onnx_initializer.data_type == onnx_pb2.TensorProto.UINT8:
                if len(onnx_initializer.int32_data) != 0:
                    for val in onnx_initializer.int32_data:
                        runtime_initializer.int32_data.append(val)
                else:
                    data_iter = struct.iter_unpack('B' * 1,
                                                   onnx_initializer.raw_data)
                    for val in data_iter:
                        runtime_initializer.int32_data.append(val[0])
            elif onnx_initializer.data_type == onnx_pb2.TensorProto.FLOAT16:
                if len(onnx_initializer.int32_data) != 0:
                    for val in onnx_initializer.int32_data:
                        runtime_initializer.int32_data.append(val)
                else:
                    assert len(onnx_initializer.raw_data) % 2 == 0
                    data_iter = struct.iter_unpack('e' * 1,
                                                   onnx_initializer.raw_data)
                    for val in data_iter:
                        runtime_initializer.int32_data.append(val[0])
            elif onnx_initializer.data_type == onnx_pb2.TensorProto.BOOL:
                if len(onnx_initializer.int32_data) != 0:
                    for val in onnx_initializer.int32_data:
                        runtime_initializer.int32_data.append(val)
                else:
                    data_iter = struct.iter_unpack('?' * 1,
                                                   onnx_initializer.raw_data)
                    for val in data_iter:
                        runtime_initializer.int32_data.append(val[0])
            elif onnx_initializer.data_type == onnx_pb2.TensorProto.STRING:
                assert len(onnx_initializer.raw_data) == 0
                for val in onnx_initializer.string_data:
                    runtime_initializer.string_data.append(val)
            elif onnx_initializer.data_type == onnx_pb2.TensorProto.INT64:
                if len(onnx_initializer.int64_data) != 0:
                    for val in onnx_initializer.int64_data:
                        runtime_initializer.int64_data.append(val)
                else:
                    assert len(onnx_initializer.raw_data) % 8 == 0
                    data_iter = struct.iter_unpack('q' * 1,
                                                   onnx_initializer.raw_data)
                    for val in data_iter:
                        runtime_initializer.int64_data.append(val[0])
            elif onnx_initializer.data_type == onnx_pb2.TensorProto.UINT64:
                if len(onnx_initializer.uint64_data) != 0:
                    for val in onnx_initializer.uint64_data:
                        runtime_initializer.uint64_data.append(val)
                else:
                    assert len(onnx_initializer.raw_data) % 8 == 0
                    data_iter = struct.iter_unpack('Q' * 1,
                                                   onnx_initializer.raw_data)
                    for val in data_iter:
                        runtime_initializer.uint64_data.append(val[0])
            elif onnx_initializer.data_type == onnx_pb2.TensorProto.UINT32:
                if len(onnx_initializer.uint64_data) != 0:
                    for val in onnx_initializer.uint64_data:
                        runtime_initializer.uint64_data.append(val)
                else:
                    assert len(onnx_initializer.raw_data) % 4 == 0
                    data_iter = struct.iter_unpack('I' * 1,
                                                   onnx_initializer.raw_data)
                    for val in data_iter:
                        runtime_initializer.uint64_data.append(val[0])
            elif onnx_initializer.data_type == onnx_pb2.TensorProto.DOUBLE:
                if len(onnx_initializer.double_data) != 0:
                    for val in onnx_initializer.double_data:
                        runtime_initializer.double_data.append(val)
                else:
                    assert len(onnx_initializer.raw_data) % 8 == 0
                    data_iter = struct.iter_unpack('d' * 1,
                                                   onnx_initializer.raw_data)
                    for val in data_iter:
                        runtime_initializer.double_data.append(val[0])
            else:
                raise ValueError(
                    "runtime don't support this tensor data type=%d" %
                    (onnx_initializer.data_type))


no_support_op = {14: 'COMPLEX64', 15: 'COMPLEX128', 16: 'BFLOAT16'}
op_data_type_dict_runtime = {
    0: "UNDEFINED",
    1: "FLOAT",
    2: "UINT8",
    3: "INT8",
    4: "UINT16",
    5: "INT16",
    6: "INT32",
    7: "INT64",
    8: "STRING",
    9: "FLOAT16",
    10: "DOUBLE",
    11: "UINT32",
    12: "UINT64",
    13: "BFLOAT16",
    14: "BOOL",
}

op_data_type_dict = {
    0: "UNDEFINED",
    1: "FLOAT",
    2: "UINT8",
    3: "INT8",
    4: "UINT16",
    5: "INT16",
    6: "INT32",
    7: "INT64",
    8: "STRING",
    9: "BOOL",
    10: "FLOAT16",
    11: "DOUBLE",
    12: "UINT32",
    13: "UINT64",
    14: "COMPLEX64",
    15: "COMPLEX128",
    16: "BFLOAT16",
}


def make_value_infos(onnx_graph,
                     runtime_graph,
                     info_type,
                     initializer_names_set=set(),
                     dequantizefilter_initializers_name=[]):
    value_infos = None
    if info_type == 'Input':
        value_infos = onnx_graph.input
    elif info_type == 'Output':
        value_infos = onnx_graph.output
    elif info_type == 'ValueInfo':
        value_infos = onnx_graph.value_info
    else:
        raise ValueError("Not support this type=%s" % (info_type))

    runtime_value_info = None
    for value_info in value_infos:
        if info_type == 'Input':
            if (value_info.name in initializer_names_set) or (
                    value_info.name in dequantizefilter_initializers_name):
                continue
            runtime_value_info = runtime_graph.input.add()
        elif info_type == 'Output':
            runtime_value_info = runtime_graph.output.add()
        elif info_type == 'ValueInfo':
            runtime_value_info = runtime_graph.value_info.add()
        else:
            raise ValueError("Not support this type=%s" % (info_type))
        runtime_value_info.name = value_info.name
        assert value_info.type.WhichOneof('value') == 'tensor_type'
        if value_info.type.tensor_type.elem_type in onnx_tensor_type2runtime_tensor_type.keys(
        ):
            runtime_value_info.type.elem_type = onnx_tensor_type2runtime_tensor_type[
                value_info.type.tensor_type.elem_type]
        else:
            raise ValueError(
                "Type: " +
                no_support_op[value_info.type.tensor_type.elem_type] +
                " is not support!")
        for dim in value_info.type.tensor_type.shape.dim:
            runtime_value_info.type.dim.append(dim.dim_value)


input_type_mapping = {
    "gray": runtime_pb2.Gray,
    "nv12": runtime_pb2.NV12,
    "yuv444": runtime_pb2.YUV444,
    "yuv444_128": runtime_pb2.YUV444,
    "yuv420sp_bt601_video": runtime_pb2.NV12,
    "bgr": runtime_pb2.BGR,
    "rgb": runtime_pb2.RGB,
    "bgrp": runtime_pb2.BGRP,
    "rgbp": runtime_pb2.RGBP,
    runtime_pb2.TensorTypeProto.INT8: runtime_pb2.S8,
    runtime_pb2.TensorTypeProto.UINT8: runtime_pb2.U8,
    runtime_pb2.TensorTypeProto.UINT16: runtime_pb2.U16,
    runtime_pb2.TensorTypeProto.INT16: runtime_pb2.S16,
    runtime_pb2.TensorTypeProto.FLOAT16: runtime_pb2.F16,
    runtime_pb2.TensorTypeProto.INT32: runtime_pb2.S32,
    runtime_pb2.TensorTypeProto.UINT32: runtime_pb2.U32,
    runtime_pb2.TensorTypeProto.FLOAT: runtime_pb2.F32,
    runtime_pb2.TensorTypeProto.INT64: runtime_pb2.S64,
    runtime_pb2.TensorTypeProto.UINT64: runtime_pb2.U64,
    runtime_pb2.TensorTypeProto.DOUBLE: runtime_pb2.F64,
}

input_type_set = {
    "featuremap", "gray", "nv12", "yuv444", "yuv444_128", "bgr", "rgb", "bgrp",
    "rgbp", "yuv420sp_bt601_video"
}

input_layout_mapping = {"NHWC": runtime_pb2.NHWC, "NCHW": runtime_pb2.NCHW}


def make_input_type(runtime_graph, input_type, input_layout_rt):
    input_len = len(runtime_graph.input)
    # assert input_len == 1
    if len(input_type) != input_len:
        raise ValueError(f"mode input num : {input_len} does not match " +
                         f"input type num {len(input_type)}")
    for i in range(input_len):
        rt_type = input_type[runtime_graph.input[i].name]
        # if input_layout_rt[i] == "NCHW" and rt_type in ["rgb", "bgr"]:
        #     rt_type = rt_type + 'p'
        if rt_type in ["nv12", "yuv420sp_bt601_video"]:
            runtime_graph.input_layout.append(runtime_pb2.NCHW)
        else:
            runtime_graph.input_layout.append(
                input_layout_mapping[input_layout_rt[i]])
        if rt_type in input_type_set:
            if rt_type.startswith('featuremap'):
                input = runtime_graph.input[i]
                runtime_graph.input_type.append(
                    input_type_mapping[input.type.elem_type])
            else:
                runtime_graph.input_type.append(input_type_mapping[rt_type])
        else:
            raise ValueError("Not support this input type=%s" % (rt_type))


def list_to_str(origin_list):
    if not origin_list:
        return ""
    res_string = ""
    for item in origin_list:
        res_string += str(item)
        res_string += ";"
    return res_string


def compile_deps_info_to_model(runtime_model, model_deps_info):
    logging.debug(f"model_deps_info: {model_deps_info}")
    if not model_deps_info:
        model_info = runtime_pb2.ModelInfo()
        model_info.model_info[
            HORIZONRT_BUILDER_VERSION_KEY] = model_deps_info.get(
                "hb_mapper_version", "9.9.9")
        runtime_model.metadata_props_info.append(model_info)
        return

    model_info = runtime_pb2.ModelInfo()
    if len(model_deps_info) != 1:
        # model deps info
        model_info.model_info[
            HORIZONRT_BUILDER_VERSION_KEY] = model_deps_info.get(
                "hb_mapper_version", "9.9.9")
        model_info.model_info["HBDK_VERSION"] = model_deps_info.get(
            "hbdk_version", "9.9.9")
        model_info.model_info["HBDK_RUNTIME_VERSION"] = model_deps_info.get(
            "hbdk_runtime_version", "9.9.9")
        model_info.model_info["HORIZON_NN_VERSION"] = model_deps_info.get(
            "horizon_nn_version", "9.9.9")

        # model_parameters info
        model_info.model_info["CAFFE_MODEL"] = model_deps_info.get(
            "caffe_model", "")
        model_info.model_info["PROTOTXT"] = model_deps_info.get("prototxt", "")
        model_info.model_info["ONNX_MODEL"] = model_deps_info.get(
            "onnx_model", "")
        model_info.model_info["MARCH"] = model_deps_info.get("march", "")
        model_info.model_info["LAYER_OUT_DUMP"] = str(
            model_deps_info.get("layer_out_dump", "N/A"))
        model_info.model_info["LOG_LEVEL"] = str(
            model_deps_info.get("log_level", "N/A"))
        model_info.model_info["WORKING_DIR"] = str(
            model_deps_info.get("working_dir", "N/A"))
        model_info.model_info["MODEL_PREFIX"] = str(
            model_deps_info.get("model_prefix", "N/A"))
        model_info.model_info["OUTPUT_NODES"] = str(
            model_deps_info.get("output_nodes", ""))
        model_info.model_info["REMOVE_NODE_TYPE"] = str(
            model_deps_info.get("remove_node_type", ""))
        model_info.model_info["REMOVE_NODE_NAME"] = str(
            model_deps_info.get("remove_node_name", ""))
        model_info.model_info["SET_NODE_DATA_TYPE"] = str(
            model_deps_info.get("set_node_data_type", ""))
        model_info.model_info["DEBUG_MODE"] = str(
            model_deps_info.get("debug_mode", ""))
        model_info.model_info["NODE_INFO"] = str(
            model_deps_info.get("node_info", ""))

        # input_parameters info
        model_info.model_info["INPUT_NAMES"] = list_to_str(
            model_deps_info.get("input_names", []))
        model_info.model_info["INPUT_TYPE_RT"] = list_to_str(
            model_deps_info.get("input_type_rt", []))
        model_info.model_info["INPUT_SPACE_AND_RANGE"] = list_to_str(
            model_deps_info.get("input_space_and_range", []))
        model_info.model_info["INPUT_TYPE_TRAIN"] = list_to_str(
            model_deps_info.get("input_type_train", []))

        model_info.model_info["INPUT_LAYOUT_TRAIN"] = list_to_str(
            model_deps_info.get("input_layout_train", []))
        model_info.model_info["INPUT_LAYOUT_RT"] = list_to_str(
            model_deps_info.get("input_layout_rt", []))

        model_info.model_info["NORM_TYPE"] = list_to_str(
            model_deps_info.get("norm_type", []))
        model_info.model_info["MEAN_VALUE"] = list_to_str(
            model_deps_info.get("mean_value", []))
        model_info.model_info["SCALE_VALUE"] = list_to_str(
            model_deps_info.get("scale_value", []))
        model_info.model_info["INPUT_SHAPE"] = list_to_str(
            model_deps_info.get("input_shape", []))
        model_info.model_info["INPUT_BATCH"] = list_to_str(
            model_deps_info.get("input_batch", []))
        if model_deps_info.get("custom_op_method", None) != None:
            model_info.model_info["CUSTOM_OP_METHOD"] = str(
                model_deps_info.get("custom_op_method", ""))
            model_info.model_info["CUSTOM_OP_DIR"] = str(
                model_deps_info.get("custom_op_dir", ""))
            model_info.model_info["CUSTOM_OP_REGISTER_FILES"] = list_to_str(
                model_deps_info.get("op_register_files", []))
        model_info.model_info["PREPROCESS_ON"] = str(
            model_deps_info.get("preprocess_on", "N/A"))
        if model_deps_info.get("optimization"):
            model_info.model_info["optimization".upper()] = list_to_str(
                model_deps_info.get("optimization"))
        model_info.model_info["CALI_TYPE"] = model_deps_info.get(
            "calibration_type", "N/A")
        model_info.model_info["CALI_DIR"] = list_to_str(
            model_deps_info.get("cal_dir", "N/A"))
        model_info.model_info["CAL_DATA_TYPE"] = list_to_str(
            model_deps_info.get("cal_data_type", []))
        model_info.model_info["PER_CHANNEL"] = str(
            model_deps_info.get("per_channel", ""))
        model_info.model_info["MAX_PERCENTILE"] = str(
            model_deps_info.get("max_percentile", ""))
        model_info.model_info["RUN_ON_CPU"] = list_to_str(
            model_deps_info.get("run_on_cpu", []))
        model_info.model_info["RUN_ON_BPU"] = list_to_str(
            model_deps_info.get("run_on_bpu", []))
        model_info.model_info["16BIT_QUANTIZE"] = str(
            model_deps_info.get("enable_int16", ""))
        model_info.model_info["DELETED_NODES_IN_BUILD"] = str(
            model_deps_info.get("DELETED_NODES_IN_BUILD", ""))
        model_info.model_info["ADD_NODES_IN_BUILD"] = str(
            model_deps_info.get("ADD_NODES_IN_BUILD", ""))

        hbdk_param_str = ""
        for item in model_deps_info.get("hbdk_params", {}):
            model_info.model_info[str(item)] = str(
                model_deps_info["hbdk_params"][item])
            hbdk_param_str += str(item) + " "
        model_info.model_info["hbdk_params"] = hbdk_param_str
        model_info.model_info["DEBUG"] = str(model_deps_info.get("debug"))
        model_info.model_info["COMPILE_MODE"] = model_deps_info.get(
            "compile_mode", "")
        show_model_info(model_info.model_info, len(model_deps_info))
        runtime_model.metadata_props_info.append(model_info)


def show_model_info(model_info, map_len):
    if map_len != 1:
        logging.info("############# model deps info #############")
        logging.info(
            f'hb_mapper version   : {model_info[HORIZONRT_BUILDER_VERSION_KEY].strip()}'
        )
        logging.info(
            f'hbdk version        : {model_info["HBDK_VERSION"].strip()}')
        logging.info(
            f'hbdk runtime version: {model_info["HBDK_RUNTIME_VERSION"].strip()}'
        )
        logging.info(
            f'horizon_nn version  : {model_info["HORIZON_NN_VERSION"].strip()}'
        )

        logging.info("############# model_parameters info #############")
        if model_info.get("CAFFE_MODEL", None):
            logging.info(f'caffe_model         : {model_info["CAFFE_MODEL"]}')
        if model_info.get("PROTOTXT", None):
            logging.info(f'prototxt            : {model_info["PROTOTXT"]}')
        if model_info.get("ONNX_MODEL", None):
            logging.info(f'onnx_model          : {model_info["ONNX_MODEL"]}')
        logging.info(f'BPU march           : {model_info["MARCH"]}')
        logging.info(f'layer_out_dump      : {model_info["LAYER_OUT_DUMP"]}')
        logging.info(f'log_level           : {model_info["LOG_LEVEL"]}')
        logging.info(f'working dir         : {model_info["WORKING_DIR"]}')
        logging.info(f'output_model_file_prefix: {model_info["MODEL_PREFIX"]}')

        if model_info.get("OUTPUT_LAYOUT", None):
            logging.info(
                f'output_layout       : {model_info["OUTPUT_LAYOUT"]}')
        if model_info.get("OUTPUT_NODES", None):
            logging.info(f'output_nodes        : {model_info["OUTPUT_NODES"]}')
        if model_info.get("REMOVE_NODE_TYPE", None):
            logging.info(
                f'remove node type    : {model_info["REMOVE_NODE_TYPE"]}')
        if model_info.get("REMOVE_NODE_NAME", None):
            logging.info(
                f'remove node name    : {model_info["REMOVE_NODE_NAME"]}')
        if model_info.get("SET_NODE_DATA_TYPE", None):
            logging.info(
                f'set node data type  : {model_info["SET_NODE_DATA_TYPE"]}')
        if model_info.get("DEBUG_MODE", None):
            logging.info(f'debug_mode  : {model_info["DEBUG_MODE"]}')
        if model_info.get("NODE_INFO", None):
            logging.info(f'node info  : {model_info["NODE_INFO"]}')

        logging.info("############# input_parameters info #############")
        input_names = get_list_from_txt(model_info["INPUT_NAMES"])
        input_types_rt = get_list_from_txt(model_info["INPUT_TYPE_RT"])
        input_space_and_range = get_list_from_txt(
            model_info["INPUT_SPACE_AND_RANGE"])
        input_types_train = get_list_from_txt(model_info["INPUT_TYPE_TRAIN"])
        input_layout_rt = get_list_from_txt(model_info["INPUT_LAYOUT_RT"])
        input_layout_train = get_list_from_txt(
            model_info["INPUT_LAYOUT_TRAIN"])
        norm_types = get_list_from_txt(model_info["NORM_TYPE"])
        mean_value = get_list_from_txt(model_info["MEAN_VALUE"])
        scale_value = get_list_from_txt(model_info["SCALE_VALUE"])
        input_shapes = get_list_from_txt(model_info["INPUT_SHAPE"])
        input_batches = get_list_from_txt(model_info["INPUT_BATCH"])
        cal_dir = get_list_from_txt(model_info["CALI_DIR"])
        cal_data_type = get_list_from_txt(model_info["CAL_DATA_TYPE"])
        cali_type = model_info["CALI_TYPE"]

        logging.info("------------------------------------------")
        for ind, name in enumerate(input_names):
            logging.info(f"---------input info : {name} ---------")
            logging.info(f'input_name          : {name}')
            logging.info(f'input_type_rt       : {input_types_rt[ind]}')
            if input_space_and_range and input_space_and_range[ind]:
                logging.info(
                    f'input_space&range   : {input_space_and_range[ind]}')
            logging.info(f'input_layout_rt     : {input_layout_rt[ind]}')
            logging.info(f'input_type_train    : {input_types_train[ind]}')
            logging.info(f'input_layout_train  : {input_layout_train[ind]}')
            logging.info(f'norm_type           : {norm_types[ind]}')
            logging.info(f'input_shape         : {input_shapes[ind]}')
            if input_batches:
                logging.info(
                    f'input_batch         : {get_input_batch(input_shapes[ind], input_batches[0])}'
                )
            if mean_value and mean_value[ind]:
                logging.info(f'mean_value          : {mean_value[ind]}')
            if scale_value and scale_value[ind]:
                logging.info(f'scale_value         : {scale_value[ind]}')
            if cali_type in mapper_consts.autoq_caltype_list:
                logging.info(f'cal_data_dir        : {cal_dir[ind]}')
            if cal_data_type:
                logging.info(f'cal_data_type       : {cal_data_type[ind]}')
            logging.info(f"---------input info : {name} end -------")
        logging.info("------------------------------------------")

        logging.info("############# calibration_parameters info #############")
        logging.info(f'preprocess_on       : {model_info["PREPROCESS_ON"]}')
        logging.info(f'calibration_type:   : {model_info["CALI_TYPE"]}')
        if model_info.get("optimization".upper()):
            logging.info(
                f'optimization        : {model_info["optimization".upper()]}')
        if model_info.get("MAX_PERCENTILE", None):
            logging.info(
                f'max_percentile      : {model_info["MAX_PERCENTILE"]}')
        if model_info.get("PER_CHANNEL", None):
            logging.info(f'per_channel         : {model_info["PER_CHANNEL"]}')
        if model_info.get("RUN_ON_CPU", None):
            logging.info(f'run_on_cpu          : {model_info["RUN_ON_CPU"]}')
        if model_info.get("RUN_ON_BPU", None):
            logging.info(f'run_on_bpu          : {model_info["RUN_ON_BPU"]}')
        if model_info.get("16BIT_QUANTIZE", None):
            logging.info(
                f'16 bit quantize     : {model_info["16BIT_QUANTIZE"]}')

        if model_info.get("CUSTOM_OP_METHOD", None):
            logging.info("############# custom_op info #############")
            logging.info(
                f'custom_op_method    : {model_info["CUSTOM_OP_METHOD"]}')
            logging.info(
                f'custom_op_dir       : {model_info["CUSTOM_OP_DIR"]}')
            logging.info(
                f'custom_op_reg_files : {model_info["CUSTOM_OP_REGISTER_FILES"]}'
            )

        logging.info("############# compiler_parameters info #############")
        if model_info.get("DEBUG", None):
            logging.info(f'debug               : {model_info["DEBUG"]}')
        if model_info.get("COMPILE_MODE", None):
            logging.info(f'compile_mode        : {model_info["COMPILE_MODE"]}')
        hbdk_param_str = model_info["hbdk_params"]
        for item in hbdk_param_str.split():
            logging.info(f'{str(item)}' + ' ' * (20 - len(str(item))) +
                         f': {model_info[item]}')

    else:
        logging.info("model deps info empty")


def build_runtime_model_wrapper(onnx_model,
                                rt_bin_file,
                                input_type,
                                input_layout_rt,
                                model_deps_info,
                                output_layout=None):
    # construct runtime model
    onnx_graph = onnx_model.graph

    logging.info(f'ONNX model output num : {len(onnx_graph.output)}')

    runtime_model = runtime_pb2.ModelProto()
    runtime_model.ir_version = 1
    runtime_model.compiler_version = 1
    new_graph = runtime_pb2.GraphProto()

    runtime_model.graphs.append(new_graph)
    runtime_graph = runtime_model.graphs[0]

    runtime_graph.name = onnx_graph.name

    # make nodes
    initializer_names_set = set()
    dequantizefilter_initializers = []
    dequantizefilter_initializers_name = []
    make_nodes(onnx_graph, runtime_graph, initializer_names_set,
               dequantizefilter_initializers,
               dequantizefilter_initializers_name)

    # make initializers
    make_initializers(onnx_graph, runtime_graph, initializer_names_set,
                      dequantizefilter_initializers)

    # make graph inputs
    make_value_infos(onnx_graph, runtime_graph, 'Input', initializer_names_set,
                     dequantizefilter_initializers_name)

    # make graph outputs
    make_value_infos(onnx_graph, runtime_graph, 'Output')

    # make graph value_infos
    make_value_infos(onnx_graph, runtime_graph, 'ValueInfo')

    make_input_type(runtime_graph, input_type, input_layout_rt)

    # 除了dequantize和transpose，其余cpu node如果作为图的输出node，则默认为NCHW格式
    if output_layout:
        layout_util.set_output_layout(output_layout, runtime_graph)

    if model_deps_info.get("input_type_rt", None):
        layout_util.set_featuremap_layout(model_deps_info, input_layout_rt,
                                          runtime_graph)

    compile_deps_info_to_model(runtime_model, model_deps_info)
    # Serilize
    save_file = open(rt_bin_file, 'wb')
    save_file.write(runtime_model.SerializeToString())
    save_file.close()
    return rt_bin_file
