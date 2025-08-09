# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import logging
import os
import subprocess

import click
import yaml

import horizon_tc_ui.version as hb_mapper_version
from horizon_tc_ui.hb_pack import unpack_model
from horizon_tc_ui.hbdtort.graph_tool import draw_graph_png
from horizon_tc_ui.hbdtort.report_gen import generate_html
from horizon_tc_ui.hbdtort.runtime_pb2 import ModelProto
from horizon_tc_ui.utils import tool_utils


@click.command(help='''
A Tool used to analyze horizon hybrid model's performance, 
which you can find with a filename like *.bin.

Example: hb_perf foo.bin
''')
@click.help_option('--help', '-h')
@click.version_option(version=hb_mapper_version.__version__)
@click.argument('bin_file', type=os.path.abspath)
@click.option(
    '-m',
    type=str,
    default="",
    help=
    'Only output perf info of desired model, please use ";" to seperate when inputting multiple models'
)
@click.option('--internal-detail/--no-internal-detail',
              type=bool,
              default=False,
              hidden=True)
@tool_utils.on_exception_exit
def cmd_main(bin_file, m, internal_detail):
    cmd_wrapper(bin_file, m, internal_detail)


def cmd_wrapper(bin_file, m, internal_detail):
    tool_utils.init_root_logger("hb_perf")

    if not bin_file.endswith('.bin'):
        raise ValueError(
            f'model {os.path.split(bin_file)[1]} is not a bin model')
    desired_models = ""
    if m != "":
        desired_models = {
            i if i.endswith('.bin') else i + '.bin': i
            for i in m.split(';')
        }
    output_dir = "hb_perf_result"
    os.system(f"mkdir -p {output_dir}")
    logging.info("Start hb_perf....")
    logging.info("hb_perf version %s" % hb_mapper_version.__version__)
    with open(bin_file, 'rb') as f:
        model_reserial = ModelProto()
        model_reserial.ParseFromString(f.read())
    if model_reserial.HasField('graph'):
        # old
        main_imp(bin_file, internal_detail, True)
    else:
        # new
        if len(model_reserial.graphs) > 1:
            # pack model
            model_list = unpack_model(bin_file, 'unpack_models')
            desired_model_list = []
            if desired_models:
                for model_path in model_list:
                    if desired_models.get(os.path.split(model_path)[1], None):
                        del desired_models[os.path.split(model_path)[1]]
                        desired_model_list.append(model_path)
                if len(desired_models.keys()) != 0:
                    logging.warning(
                        'Please check if model {} is a valid bin file'.format(
                            ','.join(desired_models.keys())))
                model_list = desired_model_list
            for model in model_list:
                main_imp(model, internal_detail, False)
        elif len(model_reserial.graphs) == 0:
            raise ValueError(
                f'Graphs of the model is empty, please check if model {bin_file} is a valid bin file.'
            )
        else:
            # singular model
            main_imp(bin_file, internal_detail, False)

    curr_dir = os.getcwd()
    unpack_models_file = os.path.join(curr_dir, 'unpack_models')
    if os.path.exists(unpack_models_file):
        os.system(f'rm -rf {unpack_models_file}')


def main_imp(bin_file, internal_detail, is_old):
    output_dir = "hb_perf_result"
    output_name = os.path.basename(bin_file).split('.')[0]
    logging.info(f' {output_name} perf '.center(50, '*'))
    os.system(f"rm -rf {output_dir}/{output_name}")
    os.system(f"mkdir {output_dir}/{output_name}")

    draw_graph_png(bin_file, f"./{output_dir}/{output_name}/", output_name,
                   is_old)

    hbm_bytes = _get_hbm_bytes(bin_file, is_old)
    logging.info("get bpu model succeeded.")

    # with tempfile.TemporaryDirectory() as d:
    d = f"./{output_dir}/{output_name}"
    hbm_file = os.path.join(d, 'temp.hbm')
    with open(hbm_file, 'wb') as f:
        f.write(hbm_bytes)
    infos = _get_perf_result(d, hbm_file, internal_detail)
    logging.info("get perf info succeeded.")
    info_dict = _format_result(infos)

    if info_dict != None:
        info_dict["model_name"] = os.path.basename(bin_file)
        output_file = f"./{output_dir}/{output_name}/{output_name}.html"
        generate_html(info_dict, output_file, internal_detail)


def _format_result(infos):
    assert len(infos) > 0, "perf数据错误。"
    with_layer = 'layer details' in infos[0]['summary'].keys()
    if not with_layer:
        logging.warning("bpu model don't have per-layer perf info.")
        logging.warning("if you need per-layer perf info please enable"
                        "[compiler_parameters.debug:True] when use makertbin.")
    # 有layer的信息
    info_dict = {}
    info_dict["subgraph_list"] = []
    for info in infos:
        tmp_dict = {}
        summary = info['summary']
        subgraph_name = summary['model name']
        tmp_dict["calc_load"] = tmp_dict.get("calc_load", 0) + summary.get(
            'BPU OPs per frame (effective)', 0)
        tmp_dict["DDR_cost"] = tmp_dict.get("DDR_cost", 0) + summary.get(
            'DDR megabytes per frame', 0)
        tmp_dict["latency"] = tmp_dict.get("latency", 0) + summary.get(
            'latency (ms)', 0)
        tmp_dict["loaded_byte"] = tmp_dict.get("loaded_byte", 0) + summary.get(
            'loaded bytes per frame', 0)
        tmp_dict["stored_byte"] = tmp_dict.get("stored_byte", 0) + summary.get(
            'stored bytes per frame', 0)
        tmp_dict["conv_working"] = tmp_dict.get(
            "conv_working", 0) + summary.get('BPU OPs per frame (working)', 0)
        tmp_dict["conv_original"] = tmp_dict.get(
            "conv_original", 0) + summary.get('BPU OPs per frame (effective)',
                                              0)

        info_dict["subgraph_list"].append({
            "name": subgraph_name,
            "perf": tmp_dict,
            "filename": subgraph_name + ".html"
        })
    return info_dict


def _get_hbm_bytes(bin_file, is_old):
    with open(bin_file, 'rb') as model_file:
        bin_str = model_file.read()
        bin_model = ModelProto()
        bin_model.ParseFromString(bin_str)
    if is_old:
        g = bin_model.graph
    else:
        g = bin_model.graphs[0]
    hbm_bytes = [i for i in g.initializer if i.name == 'PACKED_HBM_MODEL']
    assert len(hbm_bytes) > 0, '指定的模型中不存在bpu模型'

    hbm_bytes = hbm_bytes[0]
    hbm_bytes = hbm_bytes.string_data[0]
    return hbm_bytes


def _get_perf_result(dir_name, hbm_file, internal_detail):
    cmd_list = ['hbdk-perf', hbm_file, '-o', dir_name]
    if internal_detail:
        cmd_list.append('--internal-detail')
    res = subprocess.Popen(args=cmd_list,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    hbdk_out, hbdk_err = res.communicate()
    if hbdk_out:
        logging.info(hbdk_out.decode('utf-8'))
    if hbdk_err:
        logging.warning(hbdk_err.decode('utf-8'))
    if res.returncode != 0:
        raise Exception(
            f'failed to run {" ".join(cmd_list)} return code is {res.returncode}!!!'
        )
    ret_files = [
        os.path.join(dir_name, f) for f in os.listdir(dir_name)
        if f.endswith(".json")
    ]
    ret_files.sort()

    ret = []
    for fname in ret_files:
        with open(fname, 'r') as f:
            info = yaml.safe_load(f.read())
            ret.append(info)

    return ret


if __name__ == '__main__':
    cmd_main()
