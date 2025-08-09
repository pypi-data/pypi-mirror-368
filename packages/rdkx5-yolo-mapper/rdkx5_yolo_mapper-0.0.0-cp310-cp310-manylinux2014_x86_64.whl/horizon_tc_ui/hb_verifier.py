# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.
import logging
import os

import click

from horizon_tc_ui.utils.tool_utils import init_root_logger, on_exception_exit
from horizon_tc_ui.verifier import (ParamsCheck, VerifierParams, bin_infer,
                                    compare, get_input_data_by_model,
                                    onnx_infer)
from horizon_tc_ui.version import __version__


def cmd_wrapper(input_params: VerifierParams) -> None:
    init_root_logger("hb_verifier")
    output_dir = os.path.join(os.getcwd(), "verifier_output")
    os.makedirs(output_dir, exist_ok=True)

    logging.info("HB_Verifier Starts...")
    logging.info(f"verifier tool version {__version__}")

    logging.info(f"model: {input_params.model}")
    logging.info(f"board_ip: {input_params.board_ip}")
    logging.info(f"input: {input_params.input}")
    logging.info(f"run_sim: {input_params.run_sim}")
    logging.info(
        f"dump_all_nodes_results: {input_params.dump_all_nodes_results}")
    logging.info(f"compare_digits: {input_params.compare_digits}")

    logging.info(" check params start ".center(50, "="))
    params = ParamsCheck(params=input_params)
    params.check_params()
    logging.info(" check params end ".center(50, "="))

    onnx_list = params.get_onnx_model()
    bin_list = params.get_bin_model()
    input_datas = params.get_input_data()

    logging.info(" get input data start ".center(50, "="))
    input_data_dict = get_input_data_by_model(output_dir, bin_list, onnx_list,
                                              input_datas)
    logging.info(" get input data end ".center(50, "="))

    onnx_output = onnx_infer(params.compare_digits, output_dir, onnx_list,
                             input_data_dict, params.dump_all_nodes_results)
    bin_output = bin_infer(params.board_ip, params.run_sim,
                           params.compare_digits, output_dir, bin_list,
                           params.dump_all_nodes_results, params.username,
                           params.password)

    output_path_list = onnx_output + bin_output

    compare(output_path_list, params.compare_digits)


@click.command()
@click.help_option('--help', '-h')
@click.version_option(version=__version__)
@click.option('-m',
              '--model',
              type=str,
              required=True,
              help='The types of parameters supported include bin models '
              'and onnx models, with multiple models separated by ",".')
@click.option('-b',
              '--board-ip',
              type=str,
              required=False,
              help='Arm board ip')
@click.option('-i', '--input', type=str, required=False, help='Input image')
@click.option('-s',
              '--run-sim',
              type=bool,
              default=False,
              help='Use libdnn for X86 environment to do bin model inference')
@click.option('-r',
              '--dump-all-nodes-results',
              type=bool,
              default=False,
              help='Save the output results of each operator and compare')
@click.option('-c',
              '--compare_digits',
              type=int,
              default=5,
              required=False,
              help='The numerical precision of the comparison inference result'
              )  # noqa
@click.option('-u',
              '--username',
              type=str,
              default='root',
              help='Board username')
@click.option('-p', '--password', type=str, default='', help='Board password')
@on_exception_exit
def cmd_main(model: str, board_ip: str, input: str, run_sim: bool,
             dump_all_nodes_results: bool, compare_digits: int, username: str,
             password: str) -> None:
    """Validate the results of a specified fixed-point model and *.bin runtime model
    """  # noqa
    params = VerifierParams()
    params.model = model
    params.board_ip = board_ip
    params.input = input
    params.run_sim = run_sim
    params.dump_all_nodes_results = dump_all_nodes_results
    params.compare_digits = compare_digits
    params.username = username
    params.password = password
    cmd_wrapper(params)
