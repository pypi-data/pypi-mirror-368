# Copyright (c) 2024 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import logging
import os
import re
import socket

from horizon_tc_ui.utils.connect import Board
from horizon_tc_ui.utils.model_utils import BinModelInfo, ModelInfo
from horizon_tc_ui.verifier import VerifierParams
from horizon_tc_ui.version import __version__


class ParamsCheck:
    def __init__(self, params: VerifierParams) -> None:
        self.model = params.model
        self.board_ip = params.board_ip
        self.username = params.username
        self.password = params.password
        self.input = params.input
        self.run_sim = params.run_sim
        self.dump_all_nodes_results = params.dump_all_nodes_results
        self.compare_digits = params.compare_digits

        self.hrt_version_board = ""
        self.hrt_version_local = ""

        self.bin_list = []
        self.onnx_list = []
        self.input_list = []
        self._input_name_list = []

        self._input_shape_dict = {}
        self.resizer = False

    def check_params(self) -> None:
        self.check_compare_digits()
        self.check_model()

        if self.board_ip:
            self.check_board_ip()
            self.check_board_ip_is_connect()
            self.check_board_hrt()

        if self.run_sim:
            self.check_host_hrt()

        if self.board_ip and self.run_sim:
            self.check_hrt_version()

        if self.bin_list:
            self.check_mapper_version_in_bin()

        self.check_bin_rely()
        self.check_run_sim_legitimate()

        self.check_input_names()
        self.check_input_num_by_name()
        self.check_input()
        if not self.bin_list and self.onnx_list:
            self.check_input_only_onnx()

    def check_compare_digits(self) -> None:
        if not re.match(r'^[1-9]\d*$', str(self.compare_digits)):
            raise ValueError("compare_digits must be a positive integer. "
                             f"You gave the value is {self.compare_digits}.")

    def check_model(self) -> None:
        for model in self.model.split(','):
            if not os.path.isfile(model):
                raise ValueError("model does not exist: " + model)

            if model.endswith('.onnx'):
                if model in self.onnx_list:
                    raise ValueError(
                        f"The {model} model already exists, please modify")

                self.onnx_list.append(model)
                continue

            if model.endswith('.bin'):
                if model in self.bin_list:
                    raise ValueError(
                        f"The {model} model already exists, please modify")
                ModelInfo(model).check_node_is_deleted_for_verifier()

                self.bin_list.append(model)
                continue

            raise ValueError(
                "Currently, only onnx and bin models are supported."
                " Other types of models are still under development")

    def check_board_ip(self) -> None:
        compile_ip = re.compile(r'^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.'
                                r'(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.'
                                r'(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.'
                                r'(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
        if not compile_ip.match(self.board_ip):
            raise ValueError("board ip invalid: " + self.board_ip)

    def check_board_ip_is_connect(self) -> None:
        logging.info(f'check {self.board_ip} is connect')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        result = s.connect_ex((self.board_ip, 22))

        if result != 0:
            raise ValueError(
                f"{self.board_ip} connection failed, please try later.")

        logging.info(f"{self.board_ip} connection succeeded.")

    def check_board_hrt(self) -> None:
        """
        check hrt tools version on board
        """
        with Board(host=self.board_ip,
                   username=self.username,
                   password=self.password) as board:
            _, stdout, _ = board.exec_command(
                'source /etc/profile;echo "*";'
                'hrt_model_exec --version || exit 1')
            result = str(stdout.read(), encoding="utf-8").strip()
            self.hrt_version_board = result.split('*')[-1].strip()
        if result and not result.endswith('*'):
            logging.info(f"board hrt version is {self.hrt_version_board}")
        else:
            raise ValueError("DNN tool on dev board check failed. "
                             "Please make sure the board ip is valid and "
                             "tool is installed from Open Explorer package")

    def check_host_hrt(self) -> None:
        """
        check hrt tools version on host
        """
        if os.system("hrt_model_exec --version") == 0:
            self.hrt_version_local = os.popen(
                "hrt_model_exec --version").read()
            logging.info(f"host hrt version is {self.hrt_version_local}")
        else:
            raise ValueError("DNN TOOL on host machine check failed, "
                             "please install it from Open Explorer package.")

    def check_hrt_version(self) -> None:
        if self.hrt_version_board != self.hrt_version_local:
            message = "Please note: " \
                      "the versions of DNN tool on host machine " \
                      "and arm board are inconsistent"
            logging.warning(message)

    def check_mapper_version_in_bin(self) -> None:
        for model in self.bin_list:
            bin_mapper_verison = BinModelInfo(model).get_model_build_version()
            if bin_mapper_verison != __version__:
                message = f"The bin model named {model} " \
                          "may affect the verification result " \
                          "if the version number of the mapper recorded " \
                          "in the bin model is not the same as " \
                          "the version number of the current mapper. " \
                          "If the verification result is not as expected, " \
                          "please recompile the bin model and try again."
                logging.warning(message)

    def check_bin_rely(self) -> None:
        if self.bin_list and not self.board_ip and not self.run_sim:
            raise ValueError(
                "The bin model exists. "
                "Please specify a valid arm board IP or run_sim set to true")

    def check_run_sim_legitimate(self) -> None:
        if self.run_sim and self.dump_all_nodes_results:
            raise ValueError("Considering the time consumption, "
                             "it is strongly not recommended to"
                             " use the dump function in sim")

    def check_input(self) -> None:
        """
        1. 拆分参数，担心输入多张图片
        2. 校验每张图片的格式是否合规
        Returns: input_list [ input_name ]

        """
        if self.input:
            if ":" in self.input:
                input_dict = {}
                for input in self.input.split(','):
                    input_name, image_name = input.split(':')
                    if not os.path.isfile(image_name):
                        raise ValueError("input_image does not exist: " +
                                         image_name)
                    input_dict[input_name] = image_name
                self.input_list.append(input_dict)
            else:
                for image_name in self.input.split(','):
                    if not os.path.isfile(image_name):
                        raise ValueError("input_image does not exist: " +
                                         image_name)
                    self.input_list.append(image_name)
        else:
            if not self.bin_list and self.onnx_list:
                logging.info("When only a single model is available, "
                             "only the inference function is provided.")
                raise ValueError(
                    "When there is only onnx model for inference, "
                    "you need to specify the image that has completed "
                    "pre-processing in order to infer properly.")

    def _check_input_name(self, raw_input_name: list,
                          input_name: list) -> None:
        if len(raw_input_name) != len(input_name):
            raise ValueError(
                f"The quantity of model input is {len(raw_input_name)} "
                f"and {len(input_name)} respectively, "
                f"which is inconsistent. Please check the model")

        if sorted(raw_input_name) != sorted(input_name):
            raise ValueError("Inconsistent model input, please check")

    def check_input_names(self) -> None:
        raw_input_name_list = []
        for model in (self.bin_list + self.onnx_list):
            input_name_list = ModelInfo(model).get_input_name()
            if not raw_input_name_list:
                raw_input_name_list = input_name_list
            self._check_input_name(raw_input_name_list, input_name_list)

        if self.bin_list:
            self._input_name_list = BinModelInfo(
                self.bin_list[0]).get_input_name()
        else:
            self._input_name_list = raw_input_name_list

    def check_input_num_by_name(self) -> None:
        if self.input and len(self.input.split(',')) != len(
                self._input_name_list):
            raise ValueError(
                f"The input quantity is {len(self.input.split(','))}, "
                f"and the model input quantity is "
                f"{len(self._input_name_list)}, "
                f"which is inconsistent. Please modify")

    def check_input_only_onnx(self) -> None:
        if not self.input:
            raise ValueError(
                "When only the onnx model is used for inference, "
                "you need to specify the binary input with the .bin suffix")

        for i in self.input.split(','):
            if i and not i.endswith(".bin"):
                raise ValueError(
                    "When only the onnx model is used for inference, "
                    "you need to specify the binary input with the .bin suffix"
                )

    def get_onnx_model(self) -> list:
        return self.onnx_list

    def get_bin_model(self) -> list:
        return self.bin_list

    def get_model(self) -> list:
        return self.get_onnx_model() + self.get_bin_model()

    def get_input_data(self) -> dict:
        input_dict = {}
        for index, input_name in enumerate(self._input_name_list):
            if not self.input_list:
                input_dict[input_name] = ""
                continue

            if isinstance(self.input_list[0], dict):
                input_dict[input_name] = self.input_list[0][input_name]
                continue

            input_dict[input_name] = self.input_list[index]

        return input_dict
