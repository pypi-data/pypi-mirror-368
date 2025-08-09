# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import logging
import os
import re
import sys
from os import path
from typing import List, Tuple, Union

import click
import numpy as np

from horizon_tc_ui.utils import tool_utils
from horizon_tc_ui.version import __version__


def clear_dir(directory: str) -> None:
    bak_dir = os.path.join(directory, "bak")
    os.makedirs(bak_dir, exist_ok=True)
    if not path.isdir(directory):
        return
    files = os.listdir(directory)
    pattern = r'graph_output-output-\d+-(.*?)-frame_\d+'
    for item in files:
        output_name = ""

        match = re.search(pattern, item)
        if match:
            output_name = match.group(1)
            if output_name.endswith("_calibrated"):
                output_name = output_name.split("_calibrated")[0]
        elif re.search(r'(layer-.*?)-.*?-(frame_\d+)\.', item):
            os.system(f"mv {directory}/{item} {bak_dir}/")
            logging.debug(f"mv {directory}/{item} {bak_dir}/")
        else:
            if item.endswith("_calibrated.bin"):
                output_name = item.split("_calibrated.bin")[0]

        if output_name:
            os.system(f"mv {directory}/{item} {directory}/{output_name}.bin")


def _validate_input_args(left: str, right: str) -> None:
    # Check if both left and right exists.
    if not path.exists(left) or not path.exists(right):
        logging.error("wrong input argments left(%s), right(%s).", left, right)
        sys.exit(-1)

    # Both left and right must be folder or file.
    if (path.isfile(left) and not path.isfile(right)) \
            or (path.isdir(left) and not path.isdir(right)):
        logging.error("left(%s) and right(%s) should all be files/folders.")
        sys.exit(-1)

    clear_dir(left)
    clear_dir(right)


def _get_matched_files(left: str, right: str) -> List[Tuple[str, str]]:
    """Get matched files by input file name

    Args:
        left (str): left output path
        right (str): right output path

    Returns:
        list: matched files list
    """
    files_left = {
        f
        for f in os.listdir(left) if os.path.isfile(os.path.join(left, f))
    }
    files_right = {
        f
        for f in os.listdir(right) if os.path.isfile(os.path.join(right, f))
    }

    identical_files = files_left.intersection(files_right)
    different_files = files_left.symmetric_difference(files_right)
    logging.debug("left and right path different files %s", different_files)

    identical_files_pairs = [(os.path.join(left, f), os.path.join(right, f))
                             for f in identical_files]  # noqa

    return identical_files_pairs


def compare(lfile: str, rfile: str) -> Union[None, dict]:
    lvec = np.fromfile(lfile, np.float32)
    rvec = np.fromfile(rfile, np.float32)

    if len(lvec) != len(rvec):
        logging.warning("lvec length(%d) not matches rvec length(%d)",
                        len(lvec), len(rvec))
        return None

    if np.linalg.norm(lvec) * np.linalg.norm(rvec) == 0:
        logging.warning("Skip zero vector %s and %s", lfile, rfile)
        return None
    cosin_dis = np.dot(lvec,
                       rvec) / (np.linalg.norm(lvec) * np.linalg.norm(rvec))
    euc_dis = np.linalg.norm(lvec - rvec)
    mae = np.abs(lvec - rvec).max()
    mse = np.average(np.power(lvec - rvec, 2))

    return {
        'Cosin Similarity': cosin_dis,
        'Euclidean Distance': euc_dis,
        'MAE': mae,
        "MSE": mse,
    }


@click.command(help='''
A Tool used to compare vector in two files/folders.
If left and right args are present as folders, a file matching rule
will be used to find out which two vectors will be compared.
''')
@click.help_option('--help', '-h')
@click.version_option(version=__version__)
@click.option('-o',
              '--output-file',
              default='vec_diff_result.csv',
              help='output file name.',
              type=click.File('w'))
@click.argument('left', metavar='left_file/folder')
@click.argument('right', metavar='right_file/folder')
def cmd_main(output_file, left, right) -> None:
    main_imp(output_file, left, right)


def main_imp(output_file, left, right) -> None:
    log_level = logging.DEBUG
    tool_utils.init_root_logger("vec_diff", file_level=log_level)
    logging.info("Start vec_diff....")
    _validate_input_args(left, right)
    matches = _get_matched_files(left, right)
    logging.info(
        f"{len(matches)} files are matched between {left} and {right}.")
    lines = [
        f'{left}, {right}, Cosin Similarity,Euclidean Distance,MAE,MSE' + "\n"
    ]
    for match in matches:
        result = compare(*match)
        if result is None:
            logging.warning("lfile(%s),rfile(%s) not compared.", *match)
            continue
        result = '%s,%s,' % (path.basename(match[0]), path.basename(
            match[1])) + ','.join([str(item) for item in result.values()])
        lines.append(result + "\n")
    output_file.writelines(lines)
    logging.info("End vec_diff....")


if __name__ == '__main__':
    cmd_main()
