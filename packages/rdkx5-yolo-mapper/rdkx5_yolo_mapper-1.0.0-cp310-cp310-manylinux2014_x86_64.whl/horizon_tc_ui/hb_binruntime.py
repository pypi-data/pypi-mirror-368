# Copyright (c) 2022 Horizon Robotics.All Rights Reserved.
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
import subprocess
from typing import List

import yaml
from jinja2 import Template

from horizon_tc_ui import tool_path
from horizon_tc_ui.config.mapper_conf_parser import get_list_from_txt
from horizon_tc_ui.hbdtort import runtime_pb2
from horizon_tc_ui.utils.connect import Board
from horizon_tc_ui.utils.tool_utils import get_hw_index, update_input_shape


class HbBinRuntime:
    def __init__(self,
                 bin_model: str = None,
                 username: str = "root",
                 password: str = ""):
        if bin_model is None:
            raise ValueError("please provide either bin_model")

        self.bin_model = bin_model
        self.username = username
        self.password = password

        self.model_name = None
        self._output_names = None
        self._node_names = None
        self._node_and_output_names = None

        self.model_info = None
        self._march = None
        self._input_name_list = []
        self._input_type_rt_list = []
        self._input_layout_rt_list = []
        self._input_type_train_list = []
        self._input_layout_train_list = []
        self._input_shape_list = []
        self._input_batch_list = []

        self.check()

        self.load_model()
        self.set_yaml_info()

    def check(self):
        self.check_model_exist()

    def check_model_exist(self):
        if not os.path.isfile(self.bin_model):
            raise ValueError("bin_model does not exist: " + self.bin_model)

    def check_board_ip(self, board_ip):
        compile_ip = re.compile(r'^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.'
                                r'(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.'
                                r'(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.'
                                r'(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
        if not compile_ip.match(board_ip):
            raise ValueError("arm board ip invalid: " + board_ip)

    def check_board_ip_is_connect(self, board_ip):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        result = s.connect_ex((board_ip, 22))

        if result != 0:
            raise ValueError(
                f"{board_ip} connection failed, please try later.")

        logging.info(f"{board_ip} connection succeeded.")

    def check_host_hrt(self):
        """
        check host hrt tools version
        """
        if os.system("hrt_model_exec --version") == 0:
            local_hrt_model_exec_version = os.popen(
                "hrt_model_exec --version").read()
            logging.debug(
                f"host hrt version is {local_hrt_model_exec_version}")
        else:
            raise ValueError("DNN TOOL on host machine check failed, "
                             "please install it from Open Explorer package.")

    def load_model(self):
        self.model_reserial = runtime_pb2.ModelProto()
        runtime_model_file = open(self.bin_model, 'rb')
        self.model_reserial.ParseFromString(runtime_model_file.read())
        runtime_model_file.close()

    def set_yaml_info(self):
        model_info = self.get_model_info()
        self._march = model_info["MARCH"]

        self._input_name_list = get_list_from_txt(model_info["INPUT_NAMES"])
        self._input_type_rt_list = get_list_from_txt(
            model_info["INPUT_TYPE_RT"])
        self._input_layout_rt_list = get_list_from_txt(
            model_info["INPUT_LAYOUT_RT"])
        self._input_type_train_list = get_list_from_txt(
            model_info["INPUT_TYPE_TRAIN"])
        self._input_layout_train_list = get_list_from_txt(
            model_info["INPUT_LAYOUT_TRAIN"])
        self.input_shape = get_list_from_txt(model_info["INPUT_SHAPE"])
        self._input_batch_list = get_list_from_txt(model_info["INPUT_BATCH"])

        self.set_bin_shape()

    def set_bin_shape(self):
        if self._input_shape_list:
            return self._input_shape_list

        for index, input_name in enumerate(self._input_name_list):
            if self._input_type_rt_list[index] == "featuremap":
                self._input_shape_list.append([
                    i for i in
                    self.model_reserial.graphs[0].input[index].type.dim
                ])
            else:
                if self._input_type_rt_list[index] == "nv12":
                    self._input_layout_rt_list[index] = "NHWC"

                if self._input_layout_rt_list[
                        index] == self._input_layout_train_list[index]:
                    self._input_shape_list.append(
                        list(map(int, self.input_shape[index].split("x"))))
                else:
                    self._input_shape_list.append(
                        list(
                            map(
                                int,
                                update_input_shape(
                                    self._input_layout_rt_list[index],
                                    self.input_shape[index]).split("x"))))

    def get_model_name(self) -> str:
        self.model_name = self.bin_model.split('/')[-1].split('.bin')[0]
        return self.model_name

    def get_input_shapes(self) -> list:
        return self._input_shape_list

    def get_input_names(self) -> list:
        return self._input_name_list

    def get_output_names(self) -> list:
        if self._output_names is not None:
            return self._output_names
        self._output_names = [
            i.name for i in self.model_reserial.graphs[0].output
        ]
        return self._output_names

    def get_node_names(self) -> list:
        if self._node_names is not None:
            return self._node_names
        self._node_names = [i.name for i in self.model_reserial.graphs[0].node]
        return self._node_names

    def get_node_and_output_names(self) -> list:
        if self._node_and_output_names is not None:
            return self._node_and_output_names

        self._node_and_output_names = [
            (i.name, i.output) for i in self.model_reserial.graphs[0].node
        ]
        return self._node_and_output_names

    def get_model_info(self):
        if self.model_reserial.HasField('graph'):
            self.model_info = self.model_reserial.metadata_props
        else:
            if len(self.model_reserial.graphs) > 1 or len(
                    self.model_reserial.metadata_props_info) > 1:
                raise ValueError("pack model is not supported")
            self.model_info = self.model_reserial.metadata_props_info[
                0].model_info

        return self.model_info

    def get_march(self) -> str:
        return self._march

    def get_input_type_rts(self) -> list:
        return self._input_type_rt_list

    def get_input_layout_rts(self) -> list:
        return self._input_layout_rt_list

    def get_input_batchs(self) -> list:
        if not self._input_batch_list or all(not i
                                             for i in self._input_batch_list):
            _list = []
            for input_shape in self._input_shape_list:
                _list.append(input_shape[0])
            return _list

        _list = []
        for index, input_batch in enumerate(self._input_batch_list):
            if input_batch and int(input_batch) == 1:
                _list.append(self._input_shape_list[index][0])
            else:
                _list.append(int(input_batch))

        return _list

    def get_yaml_info_dict(self) -> dict:
        input_batch_list = self.get_input_batchs()
        _dict = {}
        for index, input_name in enumerate(self._input_name_list):
            _dict[input_name] = {
                "march": self._march,
                "input_type_rt": self._input_type_rt_list[index],
                "input_layout_rt": self._input_layout_rt_list[index],
                "input_type_train": self._input_type_train_list[index],
                "input_layout_train": self._input_layout_train_list[index],
                "input_shape": self._input_shape_list[index],
                "input_batch": input_batch_list[index],
            }
        return _dict

    def get_input_source(self) -> dict:
        model_info = self.get_model_info()
        input_source = model_info.get("input-source", r"{}")
        input_source = yaml.safe_load(input_source)
        return input_source

    def get_hw(self) -> List[List[int]]:
        hw_list = []
        input_shapes = self.get_input_shapes()
        for idx, layout in enumerate(self.get_input_layout_rts()):
            h_idx, w_idx = get_hw_index(layout)
            hw_list.append(
                [input_shapes[idx][h_idx], input_shapes[idx][w_idx]])
        return hw_list

    def generate_shell_file(self,
                            compare_digits: int,
                            work_path: str,
                            dump_all_nodes_results: bool = False) -> None:
        input_str = ""
        roi_infer = False
        roi_list = []
        script_info = {}
        input_sources = self.get_input_source()
        input_batch = 1 if not self._input_batch_list else int(
            self._input_batch_list[0])
        for idx, input_name in enumerate(self._input_name_list):
            if input_str:
                input_str += f",bin_input_{input_name}.bin"
            else:
                input_str = f"bin_input_{input_name}.bin"
            if input_sources[input_name] == "resizer":
                input_hws = self.get_hw()
                roi_infer = True
                roi_list.append(
                    f'0,0,{",".join(str(i - 1) for i in input_hws[idx])}')

        if roi_infer:
            if input_batch:
                input_str = ",".join([input_str] * input_batch)
                roi_list = roi_list * input_batch
            roi_info_str = '\n    --roi "{}" \\\n    '.format(  # noqa
                ";".join(roi_list))  # noqa
        else:
            roi_info_str = "\n    "

        script_info['model_file'] = self.bin_model.split('/')[-1]
        script_info['input_file'] = input_str
        script_info['dump_precision'] = str(compare_digits)
        script_info['dump_intermediate'] = str(
            3 if dump_all_nodes_results else 0)
        script_info['roi_info'] = roi_info_str
        script_info['roi_infer'] = str(roi_infer).lower()

        with open(f"{tool_path}/utils/dnn_infer.sh", "r") as f:
            shell_content = f.read()

        template = Template(source=shell_content)
        shell_content = template.render(**script_info)

        with open(f"{work_path}/infer.sh", "w") as shell_file:
            shell_file.write(shell_content)

    def init_environment(self, local_path: str, work_path: str) -> None:
        os.system(f"cp {self.bin_model} {work_path}/")
        os.system(f"cp {local_path}/infer.sh {work_path}/")
        for input_name in self._input_name_list:
            os.system(
                f"cp {local_path}/bin_input_{input_name}.bin {work_path}/")

    def run_with_board(self,
                       board_ip: str,
                       compare_digits: int,
                       local_path: str,
                       work_path: str,
                       board_path: str,
                       dump_all_nodes_results: bool = False) -> None:
        self.check_board_ip(board_ip)
        self.check_board_ip_is_connect(board_ip)

        with Board(host=board_ip,
                   username=self.username,
                   password=self.password) as b:
            _, stdout, _ = b.exec_command('source /etc/profile;echo "*";'
                                          'hrt_model_exec --version || exit 1')
            result = str(stdout.read(), encoding="utf-8").strip()
            hrt_version_board = result.split('*')[-1].strip()
            logging.debug(
                f" The version of board end hrt is {hrt_version_board} ")
            if not result or result.endswith("*"):
                raise ValueError(
                    "DNN tool on dev board check failed. "
                    "Please make sure the board ip is valid and "
                    "tool is installed from Open Explorer package")

            self.generate_shell_file(compare_digits, local_path,
                                     dump_all_nodes_results)
            self.init_environment(local_path, work_path)

            arm_file = f"/userdata/{board_path}"
            _, stdout, _ = b.exec_command(
                f"rm -rf {arm_file}; mkdir -p {arm_file}")

            logging.debug(str(stdout.read(), encoding="utf-8"))

            for file_name in os.listdir(work_path):
                b.upload(f"{work_path}/{file_name}", arm_file)

            # remote execution
            _, stdout, _stderr = b.exec_command(f"sh -l {arm_file}/infer.sh")
            stderr = str(_stderr.read(), encoding="utf-8")
            if stderr:
                logging.debug("Error log: %s", stderr)
            infer_log = str(stdout.read(), encoding="utf-8")
            logging.debug(infer_log)

            os.makedirs(f"{work_path}/output", exist_ok=True)

            b.download_dir(remote_path=f"{arm_file}/",
                           local_path=f"{work_path}/output",
                           regex=r"^model_infer_output_(.*?)\.txt$")
            if dump_all_nodes_results:
                b.download_dir(remote_path=f"{arm_file}/",
                               local_path=f"{work_path}/output",
                               regex=r"(.*?)-output-(.*?)\.txt$")

            if not os.listdir(f"{work_path}/output"):
                logging.info(infer_log)
                raise ValueError("Arm inference failed, "
                                 "please check the model and environment")

    def run_with_sim(self,
                     compare_digits: int,
                     local_path: str,
                     work_path: str,
                     dump_all_nodes_results: bool = False):
        self.check_host_hrt()
        self.generate_shell_file(compare_digits, local_path,
                                 dump_all_nodes_results)
        self.init_environment(local_path, work_path)

        host_infer_log = subprocess.getoutput(f"sh {work_path}/infer.sh")
        logging.debug(host_infer_log)
        os.makedirs(f"{work_path}/output", exist_ok=True)
        os.system(
            f'mv {work_path}/model_infer_output_*.txt {work_path}/output')

        if not os.listdir(f"{work_path}/output"):
            logging.error(host_infer_log)
