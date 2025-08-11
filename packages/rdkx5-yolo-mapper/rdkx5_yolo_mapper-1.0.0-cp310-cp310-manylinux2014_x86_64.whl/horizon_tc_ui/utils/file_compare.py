# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.
import math
import logging
import numpy as np
from typing import Union
from horizon_tc_ui.config.config_info import ConfigBase


class CompareResult(ConfigBase):
    fully_match: bool = False
    total_line_num: int = 0
    mismatch_line_num: int = 0
    relative_mismatch_ratio: float = 0.0
    line_miss_num: int = 0
    line_diff_num: int = 0
    line_nan_num: int = 0
    max_abs_error: Union[float, str] = 0.0


def get_relative_mismatch_ratio(mismatch_ratio,
                                prob1: float = 0.0,
                                prob2: float = 0.0,
                                max_prob: float = 1.0) -> float:
    if prob1 and prob2:
        return max(mismatch_ratio,
                   abs(abs(prob1) - abs(prob2)) / max(abs(prob1), abs(prob2)))
    return max(mismatch_ratio, max_prob)


def get_max_abs_error(left: str, right: str) -> Union[str, float]:
    data1 = np.loadtxt(left)
    data2 = np.loadtxt(right)

    if data1.shape != data2.shape:
        logging.error("Shape mismatch: %s and %s", left, right)
        return 'N/A'

    absolute_errors = np.max(np.abs(data1 - data2))
    logging.debug("%s, %s, %f", left, right, absolute_errors)
    return absolute_errors


def get_mismatch(mismatch_line_num: int,
                 line_miss_num: int = 0,
                 line_diff_num: int = 0,
                 line_nan_num: int = 0) -> tuple:

    mismatch_line_num += 1
    if line_miss_num:
        line_miss_num += 1
        return False, mismatch_line_num, line_miss_num

    if line_diff_num:
        line_diff_num += 1
        return False, mismatch_line_num, line_diff_num

    line_nan_num += 1
    return False, mismatch_line_num, line_nan_num


def file_res_compare(file1: str,
                     file2: str,
                     compare_digits=5) -> CompareResult:
    fully_match = True
    relative_mismatch_ratio = 0.0

    mismatch_line_num = line_miss_num = line_diff_num = line_nan_num = \
        total_line_num = 0

    max_abs_error = get_max_abs_error(file1, file2)

    with open(file1, 'r') as f1_handle, open(file2, "r") as f2_handle:
        prob_diff = pow(0.1, compare_digits)
        f1_res = f1_handle.readline().strip()
        f2_res = f2_handle.readline().strip()

        while f1_res or f2_res:
            total_line_num += 1
            if not f1_res or not f2_res:
                fully_match, mismatch_line_num, line_miss_num = get_mismatch(
                    mismatch_line_num, line_miss_num=line_miss_num)
                relative_mismatch_ratio = get_relative_mismatch_ratio(
                    relative_mismatch_ratio)
                break

            f1_res = float(f1_res)
            f2_res = float(f2_res)

            if math.isnan(f1_res) or math.isnan(f2_res):
                fully_match, mismatch_line_num, line_nan_num = get_mismatch(
                    mismatch_line_num, line_nan_num=line_nan_num)
                relative_mismatch_ratio = get_relative_mismatch_ratio(
                    relative_mismatch_ratio)

            if abs(f1_res - f2_res) > prob_diff:
                fully_match, mismatch_line_num, line_diff_num = get_mismatch(
                    mismatch_line_num, line_diff_num=line_diff_num)
                relative_mismatch_ratio = get_relative_mismatch_ratio(
                    relative_mismatch_ratio, prob1=f1_res, prob2=f2_res)

            f1_res = f1_handle.readline().strip()
            f2_res = f2_handle.readline().strip()
    result = CompareResult()
    result.fully_match = fully_match
    result.total_line_num = total_line_num
    result.mismatch_line_num = mismatch_line_num
    result.relative_mismatch_ratio = relative_mismatch_ratio
    result.line_miss_num = line_miss_num
    result.line_diff_num = line_diff_num
    result.line_nan_num = line_nan_num
    result.max_abs_error = max_abs_error

    return result
