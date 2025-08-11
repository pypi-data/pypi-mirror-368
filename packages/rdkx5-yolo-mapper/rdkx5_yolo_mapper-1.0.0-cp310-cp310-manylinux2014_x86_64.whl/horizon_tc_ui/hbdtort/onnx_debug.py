# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import os

import horizon_nn.horizon_onnx.onnx_pb as onnx_pb2

model_reserial = onnx_pb2.ModelProto()

# onnx_file = open("./alexnet.onnx", 'rb')
onnx_file = open("./model_zoo/yolov3_x2a/hybrid_model_yolov3_x2a.onnx", 'rb')
#onnx_file = open("./mobilenetv1_hybrid.onnx", 'rb')
model_reserial.ParseFromString(onnx_file.read())
onnx_file.close()

#print model info
print('ir_version', model_reserial.ir_version)
print('model_version', model_reserial.model_version)
print('opset', model_reserial.opset_import)
# print('producer_name', model_reserial.producer_name)
# print('producer_version', model_reserial.producer_version)
# print('domain', model_reserial.domain)
# print('model_version', model_reserial.model_version)
# print('doc_string', model_reserial.doc_string)
# print('metadata', model_reserial.metadata_props)

#print graph info
graph = model_reserial.graph
print('graph name', graph.name)
# print('graph doc_string', graph.doc_string)

input_cnt = 0
for value_input in graph.input:
    print("value_input" + str(input_cnt) + 'name',
          value_input.name,
          'elem_type:',
          value_input.type.tensor_type.elem_type,
          end=' ')
    print('dim [', end='')
    for dim in value_input.type.tensor_type.shape.dim:
        print(dim.dim_value, end=' ')
    print(']')
    input_cnt += 1

output_cnt = 0
for value_out in graph.output:
    print("value_output" + str(output_cnt) + 'name',
          value_out.name,
          'elem_type:',
          value_out.type.tensor_type.elem_type,
          end=' ')
    print('dim [', end='')
    for dim in value_out.type.tensor_type.shape.dim:
        print(dim.dim_value, end=' ')
    print(']')
    output_cnt += 1

value_info_cnt = 0
print('value_info list size', len(graph.value_info))
for value_info in graph.value_info:
    print("value_info" + str(value_info_cnt) + 'name',
          value_info.name,
          'elem_type:',
          value_info.type.tensor_type.elem_type,
          end=' ')
    print('dim [', end='')
    for dim in value_info.type.tensor_type.shape.dim:
        print(dim.dim_value, end=' ')
    print(']')
    value_info_cnt += 1

assert not len(graph.quantization_annotation)
assert not len(graph.sparse_initializer)

print('initializer list size', len(graph.initializer))
initializer_cnt = 0
for initializer in graph.initializer:
    print('initializer' + str(initializer_cnt) + 'name',
          initializer.name,
          end=' dims:')
    for dim in initializer.dims:
        print(str(dim), end=' ')
    print('] data_type: ', str(initializer.data_type))
    assert initializer.segment.begin == 0 and initializer.segment.end == 0

    initializer_cnt += 1
'''print node info'''

node_cnt = 0
for node in graph.node:
    print('node' + str(node_cnt) + '_name',
          node.name,
          "node type:",
          node.op_type,
          end=' ')
    print('input: [', end=' ')
    for input in node.input:
        print(input, end=' ')
    print(']', end=' ')
    print('output: [', end=' ')
    for out in node.output:
        print(out, end=' ')
    print(']', end=' ')
    print('attribute: [')
    for attribute in node.attribute:
        print('{name: ',
              attribute.name,
              'type: ',
              attribute.type,
              '}',
              end=' ')
    print(']')

    node_cnt += 1
