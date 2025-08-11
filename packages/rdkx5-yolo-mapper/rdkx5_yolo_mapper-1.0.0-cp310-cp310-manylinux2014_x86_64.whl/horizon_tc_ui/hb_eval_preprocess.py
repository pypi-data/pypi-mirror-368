# Copyright (c) 2021 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import click
import logging

from horizon_tc_ui.eval_preprocess import EvalPreprocess, __VERSION__
from horizon_tc_ui.eval_preprocess.conf import MODEL_LIST
from horizon_tc_ui.utils.tool_utils import on_exception_exit, init_root_logger


@click.command()
@click.help_option('--help', '-h')
@click.version_option(version=__VERSION__)
@click.option('--model_name',
              '-m',
              type=click.Choice(MODEL_LIST),
              required=True,
              help='Input model name.')
@click.option('--image_dir',
              '-i',
              type=str,
              required=True,
              help='Input image dir.')
@click.option('--output_dir',
              '-o',
              type=str,
              default='affected',
              help='Output dir.')
@click.option('--val_txt', '-v', type=str, default=None, hidden=False)
@click.option('--cvt-mode',
              '-c',
              type=click.Choice(['rgb_calc', 'opencv']),
              default='rgb_calc',
              hidden=True)
@on_exception_exit
def cmd_main(image_dir, model_name, output_dir, val_txt, cvt_mode):
    """
    Example: hb_eval_preprocess -m mobilenetv1 -i ./files
    """
    init_root_logger("hb_eval_preprocess", logging.INFO)
    eval_preprocess = EvalPreprocess(image_dir=image_dir,
                                     model_name=model_name,
                                     output_dir=output_dir,
                                     cvt_mode=cvt_mode,
                                     val_txt_path=val_txt)
    eval_preprocess.run()
