# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.
import fileinput
import logging
import os
from typing import Iterable, List, Tuple

import numpy as np
import onnx
from onnx.onnx_pb import ValueInfoProto, TensorProto

from horizon_tc_ui import HB_ONNXRuntime
from horizon_tc_ui.hb_binruntime import HbBinRuntime
from horizon_tc_ui.utils.tool_utils import \
    format_time_and_thread_id as format_time
from horizon_tc_ui.utils.tool_utils import get_file_name


def get_output_path(mode: str, model_name: str, output_dir: str) -> str:
    model_name += format_time()
    output_path = os.path.join(output_dir, f"{mode}/{model_name}")

    os.system(f"rm -rf {output_path}/*")
    os.makedirs(output_path, exist_ok=True)
    return output_path


def load_onnx_model(onnx_model: str, dump_all_nodes_results: bool) -> tuple:
    add_node = {}
    if dump_all_nodes_results:
        model = onnx.load(onnx_model)
        output_list = [output.name for output in model.graph.output]
        for node in model.graph.node:
            for output in node.output:
                if output not in output_list:
                    add_node[output] = node.name
                    model.graph.output.extend([ValueInfoProto(name=output)])

        return HB_ONNXRuntime(onnx_model=model), add_node

    return HB_ONNXRuntime(model_file=onnx_model), add_node


def onnx_organize_output(probs: Iterable, output_path: str,
                         compare_digits: int, output_name_list: list,
                         increase_node_dict: dict) -> List[str]:
    logging.debug(
        "Save the reasoning results of quanti model. Quantity: len(probs)")
    os.makedirs(f"{output_path}/output", exist_ok=True)

    _file_name = []
    for index, prob in enumerate(probs):
        output_name = output_name_list[index]

        node_name = increase_node_dict.get(output_name, "")
        if node_name:
            node_name = node_name.replace("/", "_")
            output_name = output_name.replace("/", "_")
            file_name = node_name + "-to-" + output_name
        else:
            file_name = f"model_infer_output_{index}_{output_name}"
        _file_name.append(file_name)

        logging.debug(f"The output result of {file_name} is being saved")

        prob.astype(np.float32).tofile(output_path + f"/{file_name}.bin")
        infer_result = output_path + f"/output/{file_name}.txt"

        prob_flatten = np.ravel(prob)
        np.set_printoptions(suppress=True)
        np.savetxt(infer_result, prob_flatten, fmt=f'%.0{compare_digits}f')
        logging.debug(f"Successfully saved the output result of {file_name}")

    logging.debug("The reasoning result of quanti model is saved successfully")

    return _file_name


def onnx_infer(
        compare_digits: int, output_dir: str, onnx_list: list,
        input_data_dict: dict,
        dump_all_nodes_results: bool) -> List[Tuple[str, str, str, str]]:
    _list = []
    for onnx_model in onnx_list:
        logging.info(
            "================ Quanti infer log start ========================="
        )
        onnx_sess, add_node = load_onnx_model(onnx_model,
                                              dump_all_nodes_results)
        input_data = input_data_dict[onnx_model]

        output_name_list = onnx_sess.output_names
        if onnx_sess.input_types[0] == TensorProto.DataType.FLOAT:
            output = onnx_sess.run(output_name_list,
                                   input_data,
                                   input_offset=0)
        else:
            output = onnx_sess.run(output_name_list, input_data)

        quanti_output_path = get_output_path('quanti_model',
                                             get_file_name(onnx_model),
                                             output_dir)

        logging.debug(f"output_name: {output_name_list}")
        file_list = onnx_organize_output(output, quanti_output_path,
                                         compare_digits, output_name_list,
                                         add_node)

        if os.listdir(f"{quanti_output_path}/output"):
            _list.append(("Quanti.onnx", get_file_name(onnx_model),
                          f"{quanti_output_path}/", file_list))

        logging.info(
            "================= Quanti infer log end =========================="
        )
    return _list


def merge_resizer_batch_output(file_list: list, save_folder: str,
                               save_name: str) -> None:
    """Merge dnn resizer batch output files to one file

    Args:
        file_list (list): merge files
        save_folder (str): save folder
        save_name (str): merged file name
    """
    save_path = os.path.join(save_folder, save_name)
    file_list_abs = [os.path.join(save_folder, i) for i in file_list]
    with open(
            save_path,
            'w') as outfile, fileinput.input(files=file_list_abs) as file_iter:
        for line in file_iter:
            outfile.write(line)


def get_file_name_by_bin(sess: HbBinRuntime, nodes: list,
                         save_folder: str) -> List[str]:
    raw_outputs = sess.get_output_names()
    input_sources = sess.get_input_source()
    input_batch = 1 if not sess._input_batch_list else int(
        sess._input_batch_list[0])  # noqa
    raw_output_list = []
    node_list = []

    for index in range(len(raw_outputs)):
        # model_infer_output_0
        # model_infer_output_0-data_batch-0_prob.txt

        if 'resizer' in input_sources.values():
            batch_output_files = []
            for batch in range(int(input_batch)):
                batch_output_file = f"model_infer_output_{index}_data_batch_{batch}_{raw_outputs[index]}.txt"  # noqa
                batch_output_files.append(batch_output_file)

            save_name = f"model_infer_output_{index}_{raw_outputs[index]}.txt"
            merged_output_file = merge_resizer_batch_output(
                file_list=batch_output_files,
                save_folder=save_folder,
                save_name=save_name)

            raw_output_list.append(merged_output_file)

        else:
            raw_output_list.append(
                f"model_infer_output_{index}_{raw_outputs[index]}")

    for node_name, output_list in nodes:
        for output_name in output_list:
            node_list.append(node_name + "-to-" + output_name)

    return raw_output_list + node_list


def get_board_path(board_path: str, model_name: str = '') -> str:
    model_name += format_time()
    if model_name:
        return f"{board_path}/{model_name}"
    return board_path


def update_file_name(file_path) -> None:
    for _, _, files in os.walk(file_path):
        for file_name in files:
            info_list = file_name.split('-output-')
            if len(info_list) == 1:
                pass
            elif len(info_list) == 2:
                output_name = info_list[1].split('-')[1]
                node_name_str = info_list[0]
                if "bpu" in node_name_str:
                    node_name = node_name_str.split('-bpu-')[1]
                else:
                    node_name = info_list[0].split('-')[3]
                os.system(f"mv {file_path}/{file_name}"
                          f" {file_path}/{node_name}-to-{output_name}.txt")
            else:
                output_name = 'output'
                node_name = info_list[0].split('-')[3]
                os.system(f"mv {file_path}/{file_name}"
                          f" {file_path}/{node_name}-to-{output_name}.txt")


def bin_infer(board_ip: str, run_sim: bool, compare_digits: int,
              output_dir: str, bin_list: list, dump_all_nodes_results: bool,
              username: str, password: str) -> List[Tuple[str, str, str, str]]:
    _list = []
    for bin in bin_list:
        bin_sess = HbBinRuntime(bin_model=bin,
                                username=username,
                                password=password)

        bin_name = get_file_name(bin)
        arm_output_path = get_output_path('arm_model', bin_name, output_dir)
        sim_output_path = get_output_path('sim_model', bin_name, output_dir)
        node_list = []
        if dump_all_nodes_results:
            node_list = bin_sess.get_node_and_output_names()

        if board_ip:
            logging.info("=================="
                         " Arm infer log start ==========================")
            bin_sess.run_with_board(board_ip, compare_digits, output_dir,
                                    arm_output_path,
                                    get_board_path("verifier_test", bin_name),
                                    dump_all_nodes_results)

            if os.listdir(f"{arm_output_path}/output"):
                file_list = get_file_name_by_bin(bin_sess, node_list,
                                                 f"{arm_output_path}/output")
                _list.append(
                    ("Arm", bin_name, f"{arm_output_path}/", file_list))

            if dump_all_nodes_results:
                update_file_name(arm_output_path + '/output')

            logging.info("=================="
                         " Arm infer log end ==========================")

        if run_sim:
            logging.info("=================="
                         " Sim infer log start ==========================")
            bin_sess.run_with_sim(compare_digits, output_dir, sim_output_path,
                                  dump_all_nodes_results)

            if os.listdir(f"{sim_output_path}/output"):
                file_list = get_file_name_by_bin(bin_sess, node_list,
                                                 f"{sim_output_path}/output")
                _list.append(
                    ("Sim", bin_name, f"{sim_output_path}/", file_list))
            logging.info("=================="
                         " Sim infer log end ==========================")
    return _list
