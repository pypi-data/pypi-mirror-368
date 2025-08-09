# Copyright (c) 2021 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import numpy as np


def cal_gen(file_shape, file_name="cali.bin", dtype=np.uint8):
    a = np.random.rand(*file_shape).astype(dtype)
    a.tofile(file_name)
