#!/usr/bin/env python
# Copyright (c) 2021 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import os
import click
import logging

from horizon_tc_ui.hbdtort.runtime_pb2 import ModelProto
from horizon_tc_ui.utils import tool_utils
from horizon_tc_ui.version import __version__

tool_utils.init_root_logger("hb_extract_hbm")


@click.command(help='''
A Tool used to extract hbm file from a model whose name is like *.bin.
This is a advanced tool, please contact horizon engineer for more info.
''')
@click.help_option('--help', '-h')
@click.version_option(version=__version__)
@click.argument('bin_file', type=os.path.abspath)
def cmd_main(bin_file):
    main_imp(bin_file)


class HbExtractHbm:
    def __init__(self, model_path: str) -> None:
        self.model_file = open(model_path, 'rb')
        self.bin_str = self.model_file.read()
        self.input_model_name = os.path.basename(model_path).split('.')[0]

    def parse_bin_model(self):
        self.bin_model = ModelProto()
        self.bin_model.ParseFromString(self.bin_str)
        self.graphs = list()
        if self.bin_model.HasField('graph'):
            graph = self.bin_model.graph
            self.graphs.append(graph)
        else:
            if len(self.bin_model.graphs) > 0:
                for graph in self.bin_model.graphs:
                    self.graphs.append(graph)
            else:
                raise ValueError('Invalid bin model!')

    def get_hbm_bytes(self):
        assert len(self.graphs) > 0, 'Invalid bin model!'
        self.hbm_info = dict()
        for graph in self.graphs:
            graph_name = graph.name
            hbm_bytes = [
                i for i in graph.initializer if i.name == 'PACKED_HBM_MODEL'
            ]
            assert len(hbm_bytes) > 0, f'There is no bpu model in {graph_name}'
            hbm_bytes = hbm_bytes[0].string_data[0]
            self.hbm_info.update({graph_name: hbm_bytes})

    def save_hbm(self):
        os.system(f'rm -rf {self.input_model_name}_hbm')
        os.mkdir(f'{self.input_model_name}_hbm')
        for name, hbm_bytes in self.hbm_info.items():
            save_name = '{}.hbm'.format(name)
            with open(save_name, 'wb') as f:
                f.write(hbm_bytes)
            logging.info(f"write hbm file: {save_name}")

    def run(self):
        self.parse_bin_model()
        self.get_hbm_bytes()
        self.save_hbm()


def main_imp(bin_file):
    hbm = HbExtractHbm(bin_file)
    hbm.run()


if __name__ == '__main__':
    cmd_main()
