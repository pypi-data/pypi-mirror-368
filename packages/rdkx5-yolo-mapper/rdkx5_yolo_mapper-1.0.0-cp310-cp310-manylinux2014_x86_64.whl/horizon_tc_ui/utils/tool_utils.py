# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import fcntl
import logging
import logging.handlers
import os
import re
import sys
import threading
import time
import traceback
from functools import wraps

import numpy as np

from horizon_tc_ui.utils import colour

RCS = "\033[31m"  # RED_COMMENT_START
GCS = "\033[32m"  # GREEN_COMMENT_START
YCS = "\033[33m"  # YELLOW_COMMENT_START
ENDING = "\033[0m"  # COLORED_COMMENT_END


def format_time_and_thread_id(
    format_timestamp=False,
    format_thread_id=False,
):
    content = ""
    time_env = os.getenv("MAPPER_LOG_FORMAT_TIMESTAMP", None)
    if format_timestamp or time_env:
        content = "_" + str(time.strftime("%Y%m%d%H%M%S", time.localtime()))
    thread_env = os.getenv("MAPPER_LOG_FORMAT_THREAD_ID", None)
    if format_thread_id or thread_env:
        content = content + "_" + str(threading.get_ident())
    return content


def get_default_log_file(logger_name):
    if logger_name is None:
        return None
    return os.path.join(os.getcwd(), 'tool.log')


def init_tool_logger(logger_name, log_file=None):
    """
    初始化工具的logger console打INFO log file打debug

    默认打印到log目录下的tools/<logger_name>.log
    """
    file_format = '%(asctime)s %(levelname)s %(module)s %(lineno)d %(message)s'
    return init_logger(logger_name, log_file, logging.INFO, file_format,
                       logging.DEBUG)


def init_root_logger(log_name=None,
                     console_level=logging.INFO,
                     file_level=logging.DEBUG):
    """
    初始化工具的root logger
    对于使用logging.xxx输出日志的工具，需要修改root logger
    :param: log_file: 日志文件名称。if None, only console handler is configured
    :param: console_level: 输出到控制台的logger，logging level
    :param: file_level: 输出到文件的logger， logging level
    :return: None
    """
    file_format = '%(asctime)s file: %(filename)s func: %(module)s line No: %(lineno)d %(message)s'  # noqa
    log_file = log_name + format_time_and_thread_id() + ".log"
    log_path = os.getcwd() + "/" + log_file
    open(log_path, 'w').close()
    init_logger(None, log_path, console_level, file_format, file_level)
    logging.info(f"log will be stored in {log_path}")


def init_logger(logger_name, log_file, console_level, file_format, file_level):
    if not log_file:
        log_file = get_default_log_file(logger_name)
    # 配置logger整体
    logger = logging.getLogger(logger_name)
    if logger_name is None:  # clear default console logger for root logger
        logger.handlers.clear()
    logger.setLevel(logging.DEBUG)

    # 配置console 打印INFO级别
    console = logging.StreamHandler()
    console.setLevel(console_level)
    console.setFormatter(
        colour.ColouredFormatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(console)

    if log_file is None:
        return logger
    log_file = os.path.expanduser(log_file)
    # 单个文件最大1m 最多10个文件
    fa = logging.handlers.RotatingFileHandler(log_file, 'a', 1024 * 1024, 10)
    fa.setLevel(file_level)
    formater = logging.Formatter(file_format)
    fa.setFormatter(formater)
    logger.addHandler(fa)
    return logger


def edit_logger(file_level):
    logger = logging.getLogger(None)
    if logger.handlers[-1].level == file_level:
        return logger
    logging.info(
        f"setting log file level to {logging.getLevelName(file_level)}")
    logger.handlers[-1].setLevel(file_level)
    return logger


def edit_console_logger(console_level):
    logger = logging.getLogger(None)
    if logger.handlers[0].level == console_level:
        return logger
    logging.info(
        f"setting log file level to {logging.getLevelName(console_level)}")
    logger.handlers[0].setLevel(console_level)
    return logger


def on_exception_exit(func):
    """异常则返回对应的值"""
    @wraps(func)
    def __decorator(*args, **kargs):
        try:
            func(*args, **kargs)
        except Exception as e:
            logging.debug(f'exception in command: {func.__name__}')
            logging.debug(traceback.format_exc())
            logging.error(e)
            exit(-1)

    return __decorator


def report_flag_start(report_name):
    logging.info('===REPORT-START{%s}===' % report_name)


def report_flag_end(report_name):
    logging.info('===REPORT-END{%s}===' % report_name)


def get_report_flag_type(line):
    if '===REPORT-END' in line:
        return 'END'
    if '===REPORT-START' in line:
        return 'START'
    return None


def parse_report_type(line):
    if get_report_flag_type(line) is None:
        return None, None
    pattern = re.compile(r'^===REPORT-((?:START)|(?:END))\{(.*)\}===$')
    ret = pattern.findall(line)
    if len(ret) == 0:
        return None, None
    return ret[0]


class SimplePythonStdHook(object):
    """ Hook python stdout, print to terminal and write to logger.

    This class is none-thread-safe."""
    def __init__(self, logger=None):
        self._terminal = sys.stdout
        self._logger = logger
        self._started = False

    def hook(self):
        if self._started:
            return
        self._started = True
        sys.stdout = self

    def write(self, message):
        self._terminal.write(message)
        if not self._logger:
            return
        if 'error' in message.lower():
            self._logger.error(message)
        elif 'warn' in message.lower():
            self._logger.warning(message)
        else:
            self._logger.info(message)

    def flush(self):
        self._terminal.flush()

    def restore(self):
        if not self._started:
            return
        self._started = False
        sys.stdout = self._terminal

    def fileno(self):
        return 1


class CStdOutHook(object):
    """Class used to hook specific stream

    This class is none-thread-safe."""
    def __init__(self, logger, hooked_stream=None, sync_write=True):
        self._logger = logger
        self._hooked_stream = hooked_stream
        self._sync_write = sync_write
        if self._hooked_stream is None:
            self._hooked_stream = sys.stdout
        self._hooked_stream_fd = self._hooked_stream.fileno()
        self._hooked_message = ""
        self._escape_char = "\b"
        # Create a pipe so the stream can be captured:
        self._pipe_out, self._pipe_in = os.pipe()

        fl = fcntl.fcntl(self._pipe_in, fcntl.F_GETFL)
        fcntl.fcntl(self._pipe_in, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        self._started = False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        """
        Start capturing the stream data.
        """
        if self._started:
            return
        self._started = True
        self._hooked_message = ""
        # Save a copy of the stream:
        self._dup_stream_fd = os.dup(self._hooked_stream_fd)
        # Replace the original stream with our write pipe:
        os.dup2(self._pipe_in, self._hooked_stream_fd)
        os.close(self._pipe_in)

        if self._sync_write:
            # Start thread that will read the stream:
            self._pipe_reader_thread = threading.Thread(
                target=self.pipe_reader, daemon=True)
            self._pipe_reader_thread.start()
            # Make sure that the thread is running and os.read() has executed:
            time.sleep(0.01)

    def stop(self):
        """
        Stop capturing the stream data and save the text in `_hooked_message`.
        """
        if not self._started:
            return
        self._started = False
        # Print the escape character to make the pipe_reader method stop:
        self._hooked_stream.write(self._escape_char)
        # Flush the stream to make sure all our data goes in before
        # the escape character:
        self._hooked_stream.flush()
        if self._sync_write:
            # wait until the thread finishes so we are sure that
            # we have receive the last character:
            self._pipe_reader_thread.join()
        else:
            self.readOutput()
        os.close(self._pipe_out)
        # Restore the original stream:
        os.dup2(self._dup_stream_fd, self._hooked_stream_fd)
        # Close the duplicate stream:
        os.close(self._dup_stream_fd)

    def filterProgressBar(self, message):
        """Filter message like '[======================================-           ]  75%'
        """  # noqa
        match_object = re.match(r'\s*\[[=\-\s]+\]\s*[0-9]+%\s*', message)
        if match_object:
            return True
        else:
            return False

    def pipe_reader(self):
        """
        Read the stream data (one byte at a time)
        and save the text in `_hooked_message`.
        """
        progress_bar_completed = False
        while True:
            char = os.read(self._pipe_out,
                           1).decode(self._hooked_stream.encoding)
            if not char or self._escape_char in char:
                break
            self._hooked_message += str(char)

            if self.filterProgressBar(self._hooked_message):
                if not progress_bar_completed:
                    if "100%" in self._hooked_message:
                        progress_bar_completed = True

                    if "100%" in self._hooked_message and '\n' not in self._hooked_message:  # noqa
                        self._hooked_message = self._hooked_message.replace(
                            "100%", "100%\n")

                    sys.stderr.write(self._hooked_message)
                self._hooked_message = ""
                continue

            if '\n' in char:
                if 'error' in self._hooked_message.lower():
                    self._logger.error(self._hooked_message)
                elif 'warn' in self._hooked_message.lower():
                    self._logger.warning(self._hooked_message)
                else:
                    if "\n" == self._hooked_message:
                        pass
                    else:
                        self._logger.info(self._hooked_message)
                self._hooked_message = ""


class RedirectStdStreams(object):
    def __init__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr

    def __enter__(self):
        self.old_stdout.flush()
        self.old_stderr.flush()
        sys.stderr = sys.stdout

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stderr.flush()
        sys.stdout.flush()
        sys.stderr = self.old_stderr


def parse_input_shape_str(input_shape_txt):
    if input_shape_txt == '':
        return []
    try:
        input_shape_txt = input_shape_txt.strip().lower()
        input_list = input_shape_txt.split('x')
        input_list = list(map(int, input_list))
    except ValueError as e:
        logging.warning('parse input_shape wrong: %s' % e)
        return []
    return input_list


def get_all_data(generator):
    """Put all data from generator together

        Arguments:
            generator: The image data generator.

        Returns:
            The data set conains all the data iterated from input generator.
        """
    data_set = [np.array(i) for i in generator]
    logging.debug(f"num of calibration data: {len(data_set)}")
    logging.debug(f"calibration data shape: {data_set[0].shape}")
    return data_set


def dump_raw_output(model_output, file_name="dump.log"):
    with open(file_name, "w") as file_handle:
        for output_item in model_output:
            output_raveled = output_item.ravel()
            print("output_raveled shape:", output_raveled.shape)
            for item in output_raveled:
                file_handle.write(f"{item:.6f} \n")


def dump_box(boxes, file_name="box_info.log"):
    with open(file_name, "w") as file_handle:
        for box_item in boxes:
            assert len(box_item) == 6
            file_handle.write(
                f"{box_item[0]:.6f}, {box_item[1]:.6f}, {box_item[2]:.6f}, {box_item[3]:.6f}, {box_item[4]:.6f}, {box_item[5]:.0f} \n"  # noqa
            )


def dump_seg(segs, file_name="seg_info.log"):
    segs = segs.reshape(-1, )
    with open(file_name, "w") as file_handle:
        seg_count = 0
        block_count = 0
        file_handle.write(f"block_{block_count} ")
        for seg_item in segs:
            if seg_count >= 8000:
                seg_count = 0
                block_count += 1
                file_handle.write(f"\nblock_{block_count} ")
            file_handle.write(f"{seg_item} ")
            seg_count += 1


def get_hw_index(input_layout):
    if input_layout == "NHWC":
        return 1, 2
    # NCHW
    elif input_layout == "NCHW":
        return 2, 3
    else:
        raise ValueError(f"invalid input_layout {input_layout}")


def format_string(s):
    if s is None:
        return ""
    if not isinstance(s, str):
        raise ValueError(f"{s} is not a string")
    return s.replace('\'', ' ').replace('\"', ' ').strip()


def get_list_from_txt(s):
    if not s:
        return []
    s = format_string(s)
    s = s[:-1] if s.endswith(';') else s
    s = s.split(';')
    s = [x.strip() for x in s]
    s = [None if x == 'None' or x == "" else x for x in s]
    return s


def get_item_from_string(s, *, func=None):
    s = format_string(s).replace(',', ' ').strip().split()
    if func:
        s = [func(x) for x in s]
    return s


def error_message(m):
    return RCS + m + ENDING


def green_message(m):
    return GCS + m + ENDING


def warning_message(m):
    return YCS + m + ENDING


def update_input_shape(layout, input_shape: str):
    input_shape_list = list(map(int, input_shape.split("x")))
    if layout == "NCHW":
        return str(input_shape_list[0]) + "x" + str(
            input_shape_list[3]) + "x" + str(input_shape_list[1]) + "x" + str(
                input_shape_list[2])

    if layout == "NHWC":
        return str(input_shape_list[0]) + "x" + str(
            input_shape_list[2]) + "x" + str(input_shape_list[3]) + "x" + str(
                input_shape_list[1])


def get_input_batch(input_shape: str, input_batch: str) -> str:
    shape_list = list(map(int, input_shape.split("x")))
    if len(shape_list) != 4:
        return input_batch

    if shape_list[0] == 1:
        return input_batch
    elif shape_list[0] > 1:
        return "invalid (valid only when input_shape[0] == 1)"
    else:
        return "Exception occurred while getting input batch"


def get_index_list(list_1: list, list_2: list) -> list:
    """
    list_2 to list_1 angular label collection
    Returns: index_list

    """
    _list = []
    _dict = {}

    num = 0
    for i in list_2:
        index_list = _dict.get(i, [])
        index_list.append(num)
        _dict[i] = index_list
        num += 1

    for j in list_1:
        index_list = _dict[j]
        _list.append(index_list[0])

        index_list.pop(0)
        _dict[j] = index_list

    return _list


def get_nodes_by_type(graph, node_type):
    node_list = []
    for node_item in graph.node:
        if node_item.op_type in node_type:
            node_list.append(node_item)
    return node_list


def get_conv_output_map(graph):
    "Get convolution node name and output tensor name mapping dict"
    node_list = get_nodes_by_type(graph, [
        'Conv', 'HzQuantizedConv', 'HzSQuantizedConv',
        "HzSQuantizedConvTranspose", "ConvTranspose"
    ])
    return node_list


def get_file_name(file: str) -> str:
    """Get file name without ext
    """
    base_name = os.path.basename(file)
    return os.path.splitext(base_name)[0]
