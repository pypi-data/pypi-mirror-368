0  # Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import logging
import click
import sys
import os
from os.path import abspath, join, dirname

from horizon_tc_ui.utils.tool_utils import init_root_logger, get_default_log_file, on_exception_exit
from horizon_tc_ui.version import __version__


@click.group()
@click.help_option('--help', '-h')
@click.version_option(version=__version__)
@on_exception_exit
def main():
    init_root_logger("hb_custom_op")
    logging.info("Start hb_custom_op....")
    logging.info("hb_custom_op version %s" % __version__)


@main.command()
@on_exception_exit
def create():
    """
    create custom op template folder for generate library files.
    """
    init_root_logger("hb_custom_op_create")
    os.system(
        f"cp {abspath(dirname(__file__))}/custom_op_template/sample_custom.py ."
    )
    logging.info("python op template 'sample_custom.py' generated")
