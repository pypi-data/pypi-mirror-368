# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

from horizon_tc_ui.hbdtort import runtime_pb2

model_reserial = runtime_pb2.ModelProto()

runtime_model_file = open("./runtime_model.bin", 'rb')
model_reserial.ParseFromString(runtime_model_file.read())
runtime_model_file.close()

#print model info
print('ir_version', model_reserial.ir_version)
print('model_version', model_reserial.compiler_version)

#print graph info
graph = model_reserial.graph
print('graph name', graph.name)

input_cnt = 0
for value_input in graph.input:
    print("value_input" + str(input_cnt) + 'name: ',
          value_input.name,
          'elem_type: ',
          value_input.type.elem_type,
          end=' ')
    print('dim: [', end='')
    for dim in value_input.type.dim:
        print(dim, end=' ')
    print(']')
    input_cnt += 1

output_cnt = 0
for value_out in graph.output:
    print("value_output" + str(output_cnt) + 'name',
          value_out.name,
          'elem_type:',
          value_out.type.elem_type,
          end=' ')
    print('dim: [', end='')
    for dim in value_out.type.dim:
        print(dim, end=' ')
    print(']')
    output_cnt += 1

value_info_cnt = 0
print('value_info list size', len(graph.value_info))
for value_info in graph.value_info:
    print("value_info" + str(value_info_cnt) + 'name',
          value_info.name,
          'elem_type:',
          value_info.type.elem_type,
          end=' ')
    print('dim: [', end='')
    for dim in value_info.type.dim:
        print(dim, end=' ')
    print(']')
    value_info_cnt += 1

print('initializer list size', len(graph.initializer))
initializer_cnt = 0
for initializer in graph.initializer:
    print('initializer' + str(initializer_cnt) + 'name',
          initializer.name,
          'elem_type:',
          initializer.shape_type.elem_type,
          end=' dims:')
    for dim in initializer.shape_type.dim:
        print(str(dim), end=' ')
    print(']')

    if initializer.name == 'conv1/bn1_mean':
        print(initializer.name, "[", end='')
        for val in initializer.float_data:
            print(val, ",", end='')
        print("]")
    if initializer.name == 'conv1/bn1_var':
        print(initializer.name, "[", end='')
        for val in initializer.float_data:
            print(val, ",", end='')
        print("]")
    if initializer.name == 'conv1/bn1_scale':
        print(initializer.name, "[", end='')
        for val in initializer.float_data:
            print(val, ",", end='')
        print("]")
    if initializer.name == 'conv1/bn1_bias':
        print(initializer.name, "[", end='')
        for val in initializer.float_data:
            print(val, ",", end='')
        print("]")

    initializer_cnt += 1
'''print node info'''

node_cnt = 0
for node in graph.node:
    print('node' + str(node_cnt) + '_name',
          node.name,
          "node type:",
          node.op_type,
          end=' ')
    if node.op_type == 'Stack_Neighbor':
        print('value: ', node.attribute[0].s)
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
