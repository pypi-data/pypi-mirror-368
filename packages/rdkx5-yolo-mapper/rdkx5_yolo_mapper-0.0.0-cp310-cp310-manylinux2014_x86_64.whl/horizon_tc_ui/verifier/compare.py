# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import tqdm
from typing import List, Tuple

from horizon_tc_ui.utils.file_compare import file_res_compare, CompareResult
from horizon_tc_ui.utils.tool_utils import (error_message, get_file_name,
                                            green_message)


def get_compare_path(output_path_list: list) -> List[Tuple[str, str]]:
    """

    Args:
        output_path_list: mode model_name , output_path

    Returns:
        list [(), ()]

    """
    compare_path_list = []
    list_len = len(output_path_list)
    i = 0
    while i < list_len:
        j = i + 1
        while j < list_len:
            compare_path_list.append(
                (output_path_list[i], output_path_list[j]))
            j += 1
        i += 1
    return compare_path_list


def get_file(infer_path: str) -> dict:
    file_dict = {}
    for file in os.listdir(infer_path):
        parsed_name = file.replace('_data_batch_0', '')
        file_dict[parsed_name] = f"{infer_path}/{file}"

    return file_dict


def get_compare_file(files1: dict, files2: dict) -> tuple:
    is_inversion = False
    compare_file_list = []

    if len(files1) > len(files2):
        files1, files2 = files2, files1
        is_inversion = True

    for file_name in list(files1.keys()):
        file_path = files2.get(file_name, None)
        if file_path:
            compare_file_list.append((files1[file_name], files2[file_name]))
            files1.pop(file_name)
            files2.pop(file_name)

    for file1_name in list(files1.keys()):
        node_and_output_1_list = file1_name.split('.')[0].split('-to-')
        if len(node_and_output_1_list) > 1:
            output_name_1 = node_and_output_1_list[1]
            for file2_name in list(files2.keys()):
                node_and_output_2_list = file2_name.split('.')[0].split('-to-')
                if len(node_and_output_2_list
                       ) > 1 and output_name_1 == node_and_output_2_list[1]:
                    compare_file_list.append(
                        (files1[file1_name], files2[file2_name]))

    return is_inversion, compare_file_list


def compare_file_by_pool(compare_file: list,
                         compare_digits: int = 5) -> Tuple[dict, dict]:
    file1_compare_result = {}
    file2_compare_result = {}
    pbar = tqdm.tqdm(desc="Compare progress",
                     leave=True,
                     total=len(compare_file),
                     ncols=80,
                     ascii=True,
                     position=0)
    with ThreadPoolExecutor(max_workers=4) as pool:
        _list = []
        _dict = {}
        for file1, file2 in compare_file:
            results = pool.submit(file_res_compare, file1, file2,
                                  compare_digits)
            _list.append(results)
            _dict[results] = (file1, file2)

        for t in as_completed(_list):
            file1, file2 = _dict[t]
            file1_name = get_file_name(file1)
            file2_name = get_file_name(file2)

            file1_compare_result[file1_name] = {
                "results": t.result(),
                "compare_file": file2_name
            }
            file2_compare_result[file2_name] = {
                "results": t.result(),
                "compare_file": file1_name
            }

            pbar.update()

    pbar.close()
    return file1_compare_result, file2_compare_result


def get_node_log(file1_name: str, file2_name: str) -> Tuple[str, str]:
    if "model_infer_output_" in file1_name:
        logging.info("==============="
                     " Original output comparison results =================")
        logging.info(f"Comparison results of original output is {file1_name}")
        raw_output_index = file1_name.split('_')[-1]
        return f"raw output {raw_output_index}", \
            f"raw output {raw_output_index}"
    if "torch-jit-export_subgraph_" in file1_name or \
            "torch-jit-export_subgraph_" in file2_name:
        logging.info("==============="
                     " BPU node output comparison results =================")
        logging.info(
            f"Comparison result of node name"
            f" {file1_name.split('-to-')[0]} VS {file2_name.split('-to-')[0]}."
        )
        return file1_name.split('-to-')[0], file2_name.split('-to-')[0]

    logging.info(
        "=============== CPU node output comparison results =================")
    logging.info(
        f"Comparison result of node name {file1_name.split('-to-')[0]}")
    return file1_name.split('-to-')[0], file1_name.split('-to-')[0]


def output_compare_results(file_list_1: list, file_list_2: list,
                           file1_result: dict, file2_result: dict,
                           is_inversion: bool) -> bool:
    fully_match = True
    output_inversion = False
    if len(file_list_1) > len(file_list_2):
        file_list_1, file_list_2 = file_list_2, file_list_1
        output_inversion = True

    for file_name_1 in file_list_1:
        result_dict = file1_result.get(file_name_1, None)
        if not result_dict:
            result_dict = file2_result.get(file_name_1, None)

        if result_dict:
            file_name_2 = result_dict["compare_file"]
            if is_inversion != output_inversion:
                file_name_1, file_name_2 = file_name_2, file_name_1

            node_name_1, node_name_2 = get_node_log(file_name_1, file_name_2)

            if not result_dict["results"]["fully_match"]:
                fully_match = False
            set_result_log(node_name_1, node_name_2, result_dict["results"])

    return fully_match


def set_result_log(node1: str, node2: str, results: CompareResult) -> None:
    mismatch_rate = round(results.mismatch_line_num / results.total_line_num,
                          3)
    if not results.fully_match:
        logging.info(f"mismatch result num: {results.mismatch_line_num}")
        logging.debug("****************************")
        logging.debug(f"mismatch.line_miss num: {results.line_miss_num}")
        logging.debug(f"mismatch.line_diff num: {results.line_diff_num}")
        logging.debug(f"mismatch.line_nan num: {results.line_nan_num}")
        logging.debug("****************************")
        logging.info(f"total result num: {results.total_line_num}")

        logging.info(f"mismatch rate: {mismatch_rate}")
        logging.info(
            f"relative mismatch ratio: {results.relative_mismatch_ratio}"
        )  # noqa
        logging.info(f"max abs error: {results.max_abs_error}")

    set_compare_log(results.fully_match, node1, node2)


def set_compare_log(fully_match, left_mode, right_mode) -> None:
    if fully_match:
        logging.info(
            green_message(
                f"{left_mode} and {right_mode} result Strict check PASSED"))
    else:
        logging.warning(
            error_message(
                f"{left_mode} and {right_mode} result Strict check FAILED"))


def compare(output_path_list: list, compare_digits: int) -> None:
    if len(output_path_list) <= 1:
        return None

    compare_path_list = get_compare_path(output_path_list)
    for infer_1, infer_2 in compare_path_list:
        mode_1, model_name_1, output_path_1, file_list_1 = infer_1
        mode_2, model_name_2, output_path_2, file_list_2 = infer_2
        logging.info(
            "***************************************************************")
        logging.info(f"compare source: {mode_1} VS {mode_2}")
        logging.info(f"compare model name: {model_name_1} VS {model_name_2}")

        file1_dict = get_file(f"{output_path_1}output")
        file2_dict = get_file(f"{output_path_2}output")
        is_inversion, compare_file_list = get_compare_file(
            file1_dict, file2_dict)

        logging.debug(file1_dict)
        logging.debug(file2_dict)
        logging.debug(is_inversion)
        logging.debug(compare_file_list)
        if len(compare_file_list) == 0:
            raise ValueError('There are no files to compare, '
                             'please check if the model output is correct')

        file1_result, file2_result = compare_file_by_pool(
            compare_file_list, compare_digits)
        fully_match = output_compare_results(file_list_1, file_list_2,
                                             file1_result, file2_result,
                                             is_inversion)
        set_compare_log(fully_match, mode_1, mode_2)

        logging.info(
            "***************************************************************")
    return None
