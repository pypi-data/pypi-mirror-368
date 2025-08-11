# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import logging
import os
import sys
from os import path

import click
from hbdk import __version__ as hbdk_version
from horizon_nn.api import version as horizon_nn_version

from horizon_tc_ui.config.mapper_consts import march_list
from horizon_tc_ui.hb_mapper_checker import CheckerRunner
from horizon_tc_ui.hb_mapper_infer import InferRunner
from horizon_tc_ui.hb_mapper_makertbin import MakertbinRunner
from horizon_tc_ui.utils.tool_utils import init_root_logger, on_exception_exit
from horizon_tc_ui.utils.yaml_builder import YamlBuilder
from horizon_tc_ui.version import __version__


@click.group()
@click.version_option(version=__version__)
@click.help_option('--help', '-h')
@on_exception_exit
def main():
    """hb_mapper is an offline model transform tool
    provided by horizon."""


@main.command()
@click.help_option('--help', '-h')
@click.option('--proto', type=str, help='caffe prototxt file')
@click.option('--model',
              type=click.Path(exists=True),
              help='caffe/onnx model file')
@click.option('--model-type',
              type=click.Choice(['caffe', 'onnx']),
              required=True)
@click.option('--march',
              type=click.Choice(march_list),
              help="""
              BPU's micro architectures(J5:bayes, X5:bayes-e, XJ3:bernoulli2),
              default bayes
              """,
              default='bayes')
@click.option(
    '--input-shape',
    type=(str, str),
    default=[],
    multiple=True,
    help='input model_input_name followed by model_input_shape, '
    'model_input_shape should be seperated by "x", e.g. "input1 1x3x224x224"')
@click.option('--output',
              type=str,
              default='',
              help='parameter [output] is deprecated, '
              r'log info will be saved in hb_mapper_checker_{date_time}.log')
@on_exception_exit
def checker(proto, model, model_type, march, input_shape, output):
    """
    check whether the model meet the requirements.
    """
    log_level = logging.DEBUG
    init_root_logger("hb_mapper_checker", file_level=log_level)

    logging.info("Start hb_mapper....")
    logging.info("hbdk version %s" % hbdk_version)
    logging.info("horizon_nn version %s" % horizon_nn_version)
    logging.info("hb_mapper version %s" % __version__)
    if output:
        logging.warning('parameter [output] is deprecated')
    if not model:
        raise ValueError('onnx or caffe model is required')

    if model_type == 'caffe' and (proto is None or not path.isfile(proto)):
        raise ValueError('please specify caffe proto file!')

    CheckerRunner(proto, model, model_type, march,
                  input_shape).run(__version__)


@main.command()
@click.help_option('--help', '-h')
@click.option('-c',
              '--config',
              type=click.Path(exists=True),
              required=False,
              help='Model convert config file')
@click.option('--model-type', type=click.Choice(['caffe', 'onnx']))
@click.option('--fast-perf',
              'fast_perf',
              flag_value=True,
              default=False,
              help='Build with fast perf mode')
@click.option('--model',
              type=click.Path(exists=True),
              help='Caffe/ONNX model file')
@click.option('--proto',
              type=click.Path(exists=True),
              help='Caffe prototxt file')
@click.option('--march',
              type=click.Choice(march_list),
              default='bayes',
              help="""
              BPU's micro architectures(J5:bayes, X5:bayes-e, XJ3:bernoulli2),
              default bayes
              """)
@click.option('-i',
              '--input-shape',
              type=(str, str),
              default=[],
              multiple=True,
              help='Specify the model input shape, '
              'e.g. --input_shape input1 1x3x224x224')
@on_exception_exit
def makertbin(config: click.Path, fast_perf: bool, proto: click.Path,
              model: click.Path, model_type: str, march: str,
              input_shape: tuple) -> None:
    """
    transform caffe model to quantization model,
    generate runtime bin file
    """
    log_level = logging.DEBUG
    init_root_logger("hb_mapper_makertbin", file_level=log_level)

    logging.info("Start hb_mapper....")
    logging.info("hbdk version %s" % hbdk_version)
    logging.info("horizon_nn version %s" % horizon_nn_version)
    logging.info("hb_mapper version %s" % __version__)
    if fast_perf:
        # check input
        if not os.path.isfile(str(model)):
            raise ValueError(f'user input model is not a file: {model}')
        if config:
            logging.error('fast-perf mode is turned on, '
                          f'the incoming config file {config} cannot be used')
            logging.error('please consider turn off fast-perf '
                          'or cancel the incoming config file')
            exit(1)
        yaml_builder = YamlBuilder(mode="fast_perf",
                                   proto=proto,
                                   model=model,
                                   model_type=model_type,
                                   march=march,
                                   input_shape=input_shape)
        config = yaml_builder.build()

    MakertbinRunner(config, model_type).run(__version__)


@main.command()
@click.help_option('--help', '-h')
@click.option('-c',
              '--config',
              type=click.Path(exists=True),
              required=True,
              help='mapper config file')
@click.option('--model-file',
              type=click.Path(exists=True),
              required=True,
              help='float onnx moded file or quantified onnx model file')
@click.option('--model-type',
              type=click.Choice(['caffe', 'onnx']),
              required=False,
              default="caffe",
              help='original model type. Choose from caffe or onnx')
@click.option(
    '--image-file',
    type=(str, click.Path(exists=True)),
    required=True,
    multiple=True,
    help=r'input {model_input_name} and {image_file}, '
    'this image file will be use for inference. e.g. "input_name1 kite.jpg"')
@click.option('--input-layout',
              type=str,
              required=False,
              default="NCHW",
              help='layout of model input')
@click.option('--output-dir',
              type=str,
              required=True,
              help='the layer output will be generated to output dir')
@on_exception_exit
def infer(config, model_file, model_type, image_file, input_layout,
          output_dir):
    """
    inference and dump output feature as float vector.
    conv layer output will be dumped.
    """

    log_level = logging.DEBUG
    init_root_logger("hb_mapper_infer", file_level=log_level)

    logging.info("Start hb_mapper....")
    logging.info("hbdk version %s" % hbdk_version)
    logging.info("horizon_nn version %s" % horizon_nn_version)
    logging.info("hb_mapper version %s" % __version__)
    logging.info(f"model type set as {model_type}")
    if input_layout != "NCHW" and input_layout != "NHWC":
        raise ValueError('input_layout should be NCHW or NHWC !')

    InferRunner(config, model_file, model_type, image_file, input_layout,
                output_dir).run()


if __name__ == '__main__':
    print("[Cauchy Warning] This \'hb_mapper\' only support Ultralytics YOLO .export() models.")
    sys.exit(main())
