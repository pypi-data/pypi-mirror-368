# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import os
import logging

import click

import horizon_tc_ui.version as hb_mapper_version
from horizon_tc_ui.config import mapper_consts
from horizon_tc_ui.config.mapper_conf_parser import get_list_from_txt
from horizon_tc_ui.hbdtort import runtime_pb2
from horizon_tc_ui.utils import tool_utils
from horizon_tc_ui.utils.model_utils import InputDataType, DataType


@click.command(help='''
A Tool used to get the deps info and compile info
''')
@click.help_option('--help', '-h')
@click.version_option(version=hb_mapper_version.__version__)
@tool_utils.on_exception_exit
@click.option('-m',
              type=str,
              default="",
              help='Only output model compile info of desired model')
@click.argument('bin_file', type=str)
def cmd_main(bin_file, m):
    main(bin_file, m)


def main(bin_file, m):
    if not bin_file.endswith('.bin'):
        raise ValueError(f'model {bin_file} is not a bin model')
    desired_model = ''
    if m:
        desired_model = m if not m.endswith('.bin') else m[:-4]
    if not os.path.exists(bin_file):
        raise ValueError(f"{bin_file} does not exist !!!")

    tool_utils.init_root_logger("hb_model_info")
    logging.info("Start hb_model_info....")
    logging.info("hb_model_info version %s" % hb_mapper_version.__version__)
    show_model_info(bin_file, desired_model)
    with open(bin_file, 'rb') as model_file:
        bin_str = model_file.read()
        bin_model = runtime_pb2.ModelProto()
        bin_model.ParseFromString(bin_str)
    log_model_info(bin_file, bin_model)


def log_info(model_info, index, graphs):
    logging.info("\n")
    logging.info(f' {str(graphs[index].name)} '.center(50, '*'))
    logging.info("############# model deps info #############")
    logging.info(
        f'hb_mapper version   : {model_info["BUILDER_VERSION"].strip()}')
    logging.info(f'hbdk version        : {model_info["HBDK_VERSION"].strip()}')
    logging.info(
        f'hbdk runtime version: {model_info["HBDK_RUNTIME_VERSION"].strip()}')

    logging.info(
        f'horizon_nn version  : {model_info["HORIZON_NN_VERSION"].strip()}')

    logging.info("############# model_parameters info #############")
    if model_info["CAFFE_MODEL"]:
        logging.info(f'caffe_model         : {model_info["CAFFE_MODEL"]}')
    if model_info["PROTOTXT"]:
        logging.info(f'prototxt            : {model_info["PROTOTXT"]}')
    if model_info["ONNX_MODEL"]:
        logging.info(f'onnx_model          : {model_info["ONNX_MODEL"]}')
    logging.info(f'BPU march           : {model_info["MARCH"]}')
    logging.info(f'layer_out_dump      : {model_info["LAYER_OUT_DUMP"]}')
    logging.info(f'log_level           : {model_info["LOG_LEVEL"]}')  # TODO
    logging.info(f'working dir         : {model_info["WORKING_DIR"]}')  # TODO
    logging.info(
        f'output_model_file_prefix: {model_info["MODEL_PREFIX"]}')  # TODO

    if model_info["OUTPUT_LAYOUT"]:
        logging.info(f'output_layout       : {model_info["OUTPUT_LAYOUT"]}')
    if model_info["OUTPUT_NODES"]:
        logging.info(f'output_nodes        : {model_info["OUTPUT_NODES"]}')
    if model_info.get("REMOVE_NODE_TYPE", None):
        logging.info(f'remove node type    : {model_info["REMOVE_NODE_TYPE"]}')
    if model_info.get("REMOVE_NODE_NAME", None):
        logging.info(f'remove node name    : {model_info["REMOVE_NODE_NAME"]}')
    if model_info.get("SET_NODE_DATA_TYPE", None):
        logging.info(
            f'set node data type   : {model_info["SET_NODE_DATA_TYPE"]}')
    if model_info.get("DEBUG_MODE", None):
        logging.info(f'debug_mode   : {model_info["DEBUG_MODE"]}')
    if model_info.get("NODE_INFO", None):
        logging.info(f'node info           : {model_info["NODE_INFO"]}')
    logging.info("############# input_parameters info #############")
    input_names = get_list_from_txt(model_info["INPUT_NAMES"])
    input_types_rt = get_list_from_txt(model_info["INPUT_TYPE_RT"])
    input_space_and_range = get_list_from_txt(
        model_info["INPUT_SPACE_AND_RANGE"])
    input_types_train = get_list_from_txt(model_info["INPUT_TYPE_TRAIN"])
    input_layout_rt = get_list_from_txt(model_info["INPUT_LAYOUT_RT"])
    input_layout_train = get_list_from_txt(model_info["INPUT_LAYOUT_TRAIN"])
    norm_types = get_list_from_txt(model_info["NORM_TYPE"])
    mean_value = get_list_from_txt(model_info["MEAN_VALUE"])
    scale_value = get_list_from_txt(model_info["SCALE_VALUE"])
    input_shapes = get_list_from_txt(model_info["INPUT_SHAPE"])
    input_batches = get_list_from_txt(model_info["INPUT_BATCH"])
    cal_dir = get_list_from_txt(model_info["CALI_DIR"])
    cal_data_type = get_list_from_txt(model_info["CAL_DATA_TYPE"])
    cali_type = model_info["CALI_TYPE"]

    logging.info("------------------------------------------")
    for ind, name in enumerate(input_names):
        logging.info(f"---------input info : {name} ---------")
        logging.info(f'input_name          : {name}')
        logging.info(f'input_type_rt       : {input_types_rt[ind]}')
        if input_space_and_range and input_space_and_range[ind]:
            logging.info(f'input_space&range   : {input_space_and_range[ind]}')
        logging.info(f'input_layout_rt     : {input_layout_rt[ind]}')
        logging.info(f'input_type_train    : {input_types_train[ind]}')
        logging.info(f'input_layout_train  : {input_layout_train[ind]}')
        logging.info(f'norm_type           : {norm_types[ind]}')
        logging.info(f'input_shape         : {input_shapes[ind]}')
        if input_batches:
            logging.info(
                f'input_batch         : {tool_utils.get_input_batch(input_shapes[ind], input_batches[0])}'  # noqa
            )
        if mean_value and mean_value[ind]:
            logging.info(f'mean_value          : {mean_value[ind]}')
        if scale_value and scale_value[ind]:
            logging.info(f'scale_value         : {scale_value[ind]}')
        if cali_type in mapper_consts.autoq_caltype_list:
            logging.info(f'cal_data_dir        : {cal_dir[ind]}')
        if cal_data_type:
            logging.info(f'cal_data_type       : {cal_data_type[ind]}')
        logging.info(f"---------input info : {name} end -------")
    logging.info("------------------------------------------")
    logging.info("############# calibration_parameters info #############")
    logging.info(f'preprocess_on       : {model_info["PREPROCESS_ON"]}')
    logging.info(f'calibration_type    : {model_info["CALI_TYPE"]}')
    if model_info.get("MAX_PERCENTILE", None):
        logging.info(f'max_percentile      : {model_info["MAX_PERCENTILE"]}')
    if model_info.get("OPTIMIZATION", None):
        logging.info(f'optimization      : {model_info["OPTIMIZATION"]}')
    if model_info.get("PER_CHANNEL", None):
        logging.info(f'per_channel         : {model_info["PER_CHANNEL"]}')
    if model_info.get("RUN_ON_CPU", None):
        logging.info(f'run_on_cpu          : {model_info["RUN_ON_CPU"]}')
    if model_info.get("RUN_ON_BPU", None):
        logging.info(f'run_on_bpu          : {model_info["RUN_ON_BPU"]}')
    if model_info.get("16BIT_QUANTIZE", None):
        logging.info(f'16 bit quantize     : {model_info["16BIT_QUANTIZE"]}')

    if model_info.get("CUSTOM_OP_METHOD", None):
        logging.info("############# custom_op info #############")
        logging.info(f'custom_op_method    : {model_info["CUSTOM_OP_METHOD"]}')
        logging.info(f'custom_op_dir       : {model_info["CUSTOM_OP_DIR"]}')
        logging.info(
            f'custom_op_reg_files : {model_info["CUSTOM_OP_REGISTER_FILES"]}')

    logging.info("############# compiler_parameters info #############")
    if model_info.get("DEBUG", None):
        logging.info(f'debug               : {model_info["DEBUG"]}')
    if model_info.get("COMPILE_MODE", None):
        logging.info('compile_mode        : ' f'{model_info["COMPILE_MODE"]}')
    hbdk_param_str = model_info["hbdk_params"]
    for item in hbdk_param_str.split():
        logging.info(f'{str(item)}' + ' ' * (20 - len(str(item))) +
                     f': {model_info[item]}')
    logging.info("--------- input/output types -------------------")
    logging.info(
        f'model input types   : {[InputDataType(item) for item in graphs[index].input_type]}'  # noqa
    )
    logging.info(
        'model output types  : '
        f'{[DataType(item.type.elem_type) for item in graphs[index].output]}')
    deleted_nodes = model_info.get("DELETED_NODES", "")
    if deleted_nodes != "":
        logging.warning(
            "Please note that the model information shown now is the information when the model was compiled, this model has been modified."  # noqa
        )
        logging.info("--------- deleted nodes -------------------")
        with open("deleted_nodes_info.txt", "w") as eval_log_handle:
            for item in deleted_nodes.split():
                logging.info(f'deleted nodes: {item}')
                deleted_node_info = model_info["NODE_" + item].replace(
                    ',', '').replace(']', '').replace('[', '')
                eval_log_handle.write(f"{deleted_node_info}\n")
    runtime_info = model_info.get("RUNTIME_INFO", "")
    if runtime_info:
        logging.debug("--------- runtime_info -------------------")
        for item in runtime_info.split():
            logging.debug(f'runtime_info {item}: {model_info[item]}')


def log_model_info(bin_file, bin_model):
    logging.debug("*******************************\n\n")
    logging.debug(f"storing info of model: {bin_file}")
    graph_list = []
    if bin_model.HasField('graph'):
        graph_list.append(bin_model.graph)
    else:
        for graph_item in bin_model.graphs:
            graph_list.append(graph_item)
    for runtime_graph in graph_list:
        logging.debug(
            f"======== graph info: {runtime_graph.name} start ========")
        logging.debug("--------input----------")
        for item in runtime_graph.input:
            logging.debug(item)
        logging.debug("--------output----------")
        for item in runtime_graph.output:
            logging.debug(item)
        logging.debug("--------node----------")
        for item in runtime_graph.node:
            logging.debug(item)
        logging.debug("--------value_info----------")
        for item in runtime_graph.value_info:
            logging.debug(item)
        logging.debug("--------initializer----------")
        for item in runtime_graph.initializer:
            logging.debug(f"name: {item.name}")
            logging.debug(f"type: {item.shape_type}")
        logging.debug("--------input_type----------")
        for item in runtime_graph.input_type:
            logging.debug(item)
        logging.debug("--------input_layout----------")
        for item in runtime_graph.input_layout:
            logging.debug(item)
        logging.debug(
            f"========= graph info: {runtime_graph.name} end ========")


def show_model_info(model_file, desired_model=""):
    model_reserial = runtime_pb2.ModelProto()
    runtime_model_file = open(model_file, 'rb')
    model_reserial.ParseFromString(runtime_model_file.read())
    runtime_model_file.close()
    if model_reserial.HasField('graph'):
        logging.debug("model_reserial has 1 graph")
        model_info = model_reserial.metadata_props
        log_info(model_info, 0, [model_reserial.graph])
    else:
        logging.debug("model_reserial has multiple graphs")
        model_info = model_reserial.metadata_props_info
        graphs = model_reserial.graphs
        logging.debug(f"graphs length: {len(graphs)}")
        # logging.debug(f"model_info : {model_info}")
        model_found = True
        if desired_model:
            model_found = False
        for index, info in enumerate(model_info):
            model_name = graphs[index].name
            if desired_model:
                if desired_model == model_name:
                    log_info(info.model_info, index, graphs)
                    model_found = True
            else:
                log_info(info.model_info, index, graphs)
        if not model_found:
            raise ValueError(
                f"model '{desired_model}' not found in this bin model")
