# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

from horizon_nn.custom.op_registration import (op_implement_register,
                                               op_shape_infer_register)


@op_implement_register("CustomIdentity")
class CustomIdentity(object):
    def __init__(self, kernel_size, threshold):
        self._kernel_size = kernel_size
        self._default_threshold = threshold

    def compute(self, X):
        return X


@op_shape_infer_register("CustomIdentity")
def infer_shape(inputs_shape):
    outputs_shape = inputs_shape
    return outputs_shape
