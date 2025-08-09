# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import os
import sys
import logging
import subprocess

# 默认打印到stderr
default_print_fun = lambda x: print(x, file=sys.stderr)
# 不打印
none_print_fun = lambda x: None


def run_cmd(cmd, print_fun=default_print_fun, timeout=600):
    """
    执行命令 返回{'ret': <ret>, 'stdout': <stdout>, 'stderr': <stderr}
    """
    p = subprocess.Popen(cmd,
                         shell=True,
                         universal_newlines=True,
                         stderr=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    try:
        (stdout, stderr) = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        print_fun('timeout!')
        p.kill()
        (stdout, stderr) = p.communicate()
    ret = p.returncode

    print_fun("======")
    print_fun("cmd:\n%s\n\nret:%d\n\nstdout:\n%s\n\nstderr:\n%s\n\n" %
              (cmd, ret, stdout, stderr))

    return {'ret': ret, 'stdout': stdout, 'stderr': stderr}


def __assert_ret(ret, cmd, action):
    if ret != 0:
        if action:
            raise Exception('failed to %s! ret=%d' % (action, ret))
        else:
            raise Exception('failed to run[%s]! ret=%d' % (cmd, ret))


def check_output(cmd, print_fun=default_print_fun, timeout=600, action=None):
    """
    执行命令 返回output 如果ret非0抛异常
    """
    result = run_cmd(cmd, print_fun, timeout)
    __assert_ret(result['ret'], cmd, action)
    return result['stdout']


def call(cmd, print_fun=default_print_fun, timeout=600):
    """
    执行命令 返回返回码
    """
    return run_cmd(cmd, print_fun, timeout)['ret']


def check_call(cmd, print_fun=default_print_fun, timeout=600, action=None):
    """
    执行命令，检查是否成功，不成功抛异常
    """
    result = run_cmd(cmd, print_fun, timeout)
    __assert_ret(result['ret'], cmd, action)


def subprocess_run(cmd_list, workspace=None, timeout=None, retry=3):
    if not workspace:
        workspace = os.getcwd()
    cp = subprocess.run(cmd_list,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True,
                        cwd=workspace,
                        timeout=timeout)

    if cp.returncode != 0:
        logging.error("subprocess_run failed!")
        logging.error(f"workspace: {workspace}")
        logging.error(f"return code: {cp.returncode}")
        logging.error(f"stdout: {cp.stdout}")
        logging.error(f"stderr: {cp.stderr}")
    if cp.returncode == 137 and retry != 0:
        cp.returncode = subprocess_run(cmd_list, workspace, timeout, retry - 1)
    return cp.returncode


def subprocess_run_full(cmd_list, workspace=None, timeout=None, retry=3):
    if not workspace:
        workspace = os.getcwd()
    cp = subprocess.run(cmd_list,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True,
                        cwd=workspace,
                        timeout=timeout)
    if cp.returncode != 0:
        logging.error("subprocess_run failed!")
        logging.error(f"workspace: {workspace}")
        logging.error(f"return code: {cp.returncode}")
        logging.error(f"stdout: {cp.stdout}")
        logging.error(f"stderr: {cp.stderr}")
    if cp.returncode == 137 and retry != 0:
        cp.returncode = subprocess_run(cmd_list, workspace, timeout, retry - 1)
    return cp.returncode, cp.stdout, cp.stderr
