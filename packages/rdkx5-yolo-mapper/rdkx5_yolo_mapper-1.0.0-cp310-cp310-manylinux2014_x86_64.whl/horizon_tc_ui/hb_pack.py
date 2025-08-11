# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import os
import ast
import click
import logging
from horizon_tc_ui.hbdtort import runtime_pb2
from horizon_tc_ui.utils.tool_utils import init_root_logger, on_exception_exit
import horizon_tc_ui.version as hb_mapper_version


def is_old(input_model: bytes) -> bool:
    model_package = runtime_pb2.ModelProto()
    model_package.ParseFromString(input_model)
    if model_package.HasField('graph'):
        return True
    else:
        return False


def parse_model(input_model: bytes) -> runtime_pb2.ModelProto():
    model_package = runtime_pb2.ModelProto()
    model_package.ParseFromString(input_model)
    return model_package


def pack_models(model_list, output_name):
    '''模型打包
    model_list为待打包模型列表
    output_name为输出模型名称
    '''
    model_names = []
    model_packages = runtime_pb2.ModelProto()
    for model_path in model_list:
        # 判断输入的文件是否以.bin结尾
        if not model_path.endswith('.bin'):
            raise ValueError(f'{model_path} is not a model file!!')
        model_names.append(os.path.basename(model_path).split(".")[0])

    set_model_names = set(model_names)
    if len(set_model_names) != len(model_names):
        raise ValueError("model name must be different !!!")
    logging.info('generate packed model')
    for index, model_path in enumerate(model_list):
        metadata_props = runtime_pb2.ModelInfo()
        with open(model_path, 'rb') as f:
            model_byte = f.read()
            model = parse_model(model_byte)
            if is_old(model_byte):
                graph = model.graph
                metadata_props.model_info.update(model.metadata_props)
            else:
                # 判断是否为已经pack过的模型
                if len(model.graphs) >= 2:
                    raise ValueError(
                        f'model: {model_list[index]} is a packed model, it can not be packed again!'
                    )
                graph = model.graphs[0]
                metadata_props = model.metadata_props_info[0]
        model_packages.metadata_props_info.append(metadata_props)
        model_packages.graphs.append(graph)
    save_file_name = output_name
    save_file = open(save_file_name, 'wb')
    save_file.write(model_packages.SerializeToString())
    logging.info(f'packed model：{save_file_name}')
    save_file.close()
    logging.info('pack models succeed!')


@click.command()
@click.help_option('--help', '-h')
@click.version_option(version=hb_mapper_version.__version__)
@click.argument('model', type=str, nargs=-1, required=True)
@click.option('-o',
              '--output_name',
              type=str,
              default='pack_model.bin',
              help='packed model name')
@on_exception_exit
def pack(model, output_name):
    '''
    Example：hb_pack a.bin b.bin c.bin -o out.bin
    '''
    init_root_logger("hb_pack")
    logging.info("hb_pack version %s" % hb_mapper_version.__version__)
    logging.info('Start pack models....')
    pack_models(model, output_name)


def unpack_model(model: bytes, output_dir: str) -> list:
    '''模型解包
    model为待解包模型
    output_dir为输出路径
    返回值为解包后模型列表
    '''
    unpack_models = []
    os.system(f'rm -rf {output_dir}')
    os.mkdir(output_dir)

    with open(model, 'rb') as model_byte:
        model_reserial = parse_model(model_byte.read())

    if model_reserial.HasField('graph'):
        raise ValueError(f'model {model} is not a packed model')
    for index, graph in enumerate(model_reserial.graphs):
        save_file_name = os.path.join(output_dir, graph.name) + '.bin'
        with open(save_file_name, 'wb') as f:
            save_model = runtime_pb2.ModelProto()
            save_model.graphs.append(graph)
            save_model.metadata_props_info.append(
                model_reserial.metadata_props_info[index])
            f.write(save_model.SerializeToString())
            logging.info(f'save model: {save_file_name}')
            unpack_models.append(save_file_name)
    return unpack_models


@click.command()
@click.help_option('--help', '-h')
@click.version_option(version=hb_mapper_version.__version__)
@click.argument(
    'model',
    type=str,
    nargs=1,
)
@click.option('-o',
              '--output_dir',
              type=str,
              default='unpack_models',
              help='unpacked models folder name')
@click.option('-r/-no-r', default=False, help='If need to unpack model.')
@on_exception_exit
def unpack(model, r, output_dir):
    '''
    Example：hb_unpack a.bin -o unpack_models
    '''
    init_root_logger("hb_unpack")
    logging.info("hb_unpack version %s" % hb_mapper_version.__version__)
    logging.info('Start unpack models....')
    unpack_model(model, output_dir)


if __name__ == '__main__':
    unpack()
