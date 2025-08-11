# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import logging
import sys
import os
from pathlib import Path

from horizon_nn.api import build_caffe, build_onnx

from horizon_tc_ui.utils.tool_utils import CStdOutHook, \
    parse_input_shape_str, edit_logger
from horizon_tc_ui.parser.caffe_parser import CaffeProto
from horizon_tc_ui.parser.onnx_parser import OnnxModel
from horizon_tc_ui.hbdtort.onnx2horizonrt import build_runtime_model_wrapper


class CheckerRunner:
    def __init__(self,
                 proto: str,
                 model: str,
                 model_type: str,
                 march: str,
                 input_shape_info: iter,
                 output=None) -> None:
        """
        In engineering practice, FPMs must be checked before conversion
        because not all of them can be converted into HGMs.
        In general, the checking process walks through the model
        coversion process,
        while simplifies some time-consuming OP conversions,
        and the tool will dump checking results along with the information
        that whether an OP is run in BPU or CPU.
        :param proto: proto file path
        :param model: model file path
        :param model_type: model type eg.['caffe', 'onnx']
        :param march: bpu march
        :param input_shape_info:
        e.g (('data', '1x3x224x224'), ('data', '1x3x224x224'))
        """
        self.proto = proto
        self.model = model
        self.model_type = model_type
        self.march = march
        self.input_names = []
        self.input_shapes = {}
        self.input_shape_info = input_shape_info
        self.hybrid_input = self.get_hybrid_input()

    def get_hybrid_input(self) -> list:
        """
        Get hybrid input according to model input type
        :return: list
        """
        if self.model_type == 'caffe':
            proto_suffix = os.path.splitext(self.proto)[-1]
            model_suffix = os.path.splitext(self.model)[-1]
            if '.proto' not in proto_suffix or '.caffe' not in model_suffix:
                logging.error('Please double check your input')
                raise ValueError(f'The model type is {self.model_type}, '
                                 f'but input proto is {self.proto} '
                                 f'and model is {self.model}')
            model = CaffeProto(self.proto)
        else:
            model_suffix = os.path.splitext(self.model)[-1]
            if model_suffix != '.onnx':
                logging.error('Please double check your input')
                raise ValueError(f'The model type is {self.model_type}, '
                                 f'but input model is {self.proto}')
            model = OnnxModel(self.model)
        hybrid_input = model.get_input_names()
        return hybrid_input

    def _get_input_dict(self) -> dict:
        if self.model_type == 'caffe':
            model = CaffeProto(self.proto)
        else:
            model = OnnxModel(self.model)
        input_name_from_model = model.get_input_names()
        # check input model name validity
        for name in self.input_names:
            if name not in input_name_from_model:
                message = 'wrong input name: %s, available: %s' % (
                    name, input_name_from_model)
                raise ValueError(message)
        input_dict = {}
        for input_name, input_shape in self.input_shapes.items():
            input_shape_model = model.get_input_dims(input_name)
            # check user input_shape and model_input_shape to see if same
            if input_shape != input_shape_model:
                logging.warning(
                    'for input "%s", user input_shape:%s is not same with model input_shape: %s'  # noqa
                    % (input_name, input_shape, input_shape_model))
            input_dict[input_name] = {'input_shape': input_shape}

        return input_dict

    def run(self, version):
        edit_logger(logging.DEBUG)
        # dump input params
        logging.info("Model type: %s" % self.model_type)
        logging.debug("march: %s" % self.march)
        for input_name, input_shape_txt in self.input_shape_info:
            self.input_shapes[input_name] = parse_input_shape_str(
                input_shape_txt)
            self.input_names.append(input_name)
        logging.info("input names %s" % self.input_names)
        logging.info("input shapes %s" % self.input_shapes)

        addtional_param = {}
        if len(self.input_shapes) > 0:
            addtional_param['input_dict'] = self._get_input_dict()
            # Start checker
        logging.info("Begin model checking....")
        Path(".hb_check").mkdir(parents=True, exist_ok=True)

        # Logs are redirected to files
        with CStdOutHook(logging, sys.stdout, True) as stdhook:  # noqa
            if self.model_type == "caffe":
                try:
                    hybrid_model = build_caffe(prototxt_file=self.proto,
                                               caffemodel_file=self.model,
                                               march=self.march,
                                               name_prefix="./.hb_check/",
                                               save_model=True,
                                               check_mode=True,
                                               **addtional_param)
                except Exception as e:
                    if "ERROR-OCCUR-DURING" in str(e):
                        raise ValueError(str(e))

                    raise ValueError(
                        "*** ERROR-OCCUR-DURING {horizon_nn.build_caffe} ***,"
                        + f" error message: {str(e)}")
            elif self.model_type == "onnx":
                try:
                    hybrid_model = build_onnx(onnx_file=self.model,
                                              march=self.march,
                                              name_prefix="./.hb_check/",
                                              save_model=True,
                                              check_mode=True,
                                              **addtional_param)
                except Exception as e:
                    if "ERROR-OCCUR-DURING" in str(e):
                        raise ValueError(str(e))

                    raise ValueError(
                        "*** ERROR-OCCUR-DURING {horizon_nn.build_onnx} ***," +
                        f" error message: {str(e)}")

        file_name = "./.hb_check/checker_hybrid_horizonrt.bin"
        input_type_rts = {}
        input_layout_rt = []
        for name in self.hybrid_input:
            input_type_rts.update({name: "yuv444_128"})
            input_layout_rt.append("NHWC")
        try:
            build_runtime_model_wrapper(hybrid_model, file_name,
                                        input_type_rts, input_layout_rt,
                                        {"hb_mapper_version": version})
        except Exception as e:
            raise ValueError(
                "*** ERROR-OCCUR-DURING {runtime.runtime_model_generation} ***"
                + f", error message: {str(e)}")
        logging.info("End model checking....")
