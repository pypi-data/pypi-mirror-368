# Copyright (c) 2022 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.
import logging

import cv2
import numpy as np

from horizon_tc_ui.data.transformer import (BGR2NV12Transformer,
                                            BGR2YUV444Transformer,
                                            CHW2HWCTransformer,
                                            HWC2CHWTransformer,
                                            NV12ToYUV444Transformer)
from horizon_tc_ui.utils.tool_utils import get_index_list


class Data:
    # TODO
    def __init__(self,
                 march: str,
                 input_type_rt: str,
                 input_layout_rt: str,
                 input_batch: str,
                 input_name: str,
                 input_shape: list,
                 image: str or np.ndarray,
                 input_source: str = 'ddr') -> None:
        self.march = march
        self.input_type_rt = input_type_rt
        self.input_layout_rt = input_layout_rt
        self.input_batch = input_batch if input_batch else 1
        self.input_name = input_name
        self.input_shape = input_shape
        self.image = image
        self.input_source = input_source
        self.check()

    def check(self):
        self.check_required()

    def check_required(self):
        if not self.input_name:
            raise ValueError("please provide either input_name")

        if not self.input_shape:
            raise ValueError("please provide either input_shape")

    def get_wh(self):
        input_layout_rt = ""
        if self.input_shape[1] == 3 or self.input_shape[1] == 1:
            input_layout_rt = "NCHW"
        if self.input_shape[3] == 3 or self.input_shape[3] == 1:
            input_layout_rt = "NHWC"

        if input_layout_rt == "":
            width = height = ""
        elif input_layout_rt == "NCHW":
            width, height = self.input_shape[3], self.input_shape[2]
        else:
            width, height = self.input_shape[2], self.input_shape[1]

        return width, height

    def get_input_by_random_number(self):
        if self.input_type_rt == "featuremap":
            return (np.random.random(self.input_shape) * 255).astype(
                np.float32)
        if self.input_type_rt == "nv12":
            images = (np.random.random(self.input_shape) * 255).astype(
                np.uint8)

            input_data = []
            for image in images:
                if self.input_layout_rt == "NCHW":
                    transformer = CHW2HWCTransformer()
                    image = transformer([image])[0]
                transformer = BGR2NV12Transformer(data_format="HWC",
                                                  cvt_mode="opencv")
                image = transformer([image])[0]
                input_data.append(image)

            return np.array(input_data)
        else:
            return (np.random.random(self.input_shape) * 255).astype(np.uint8)

    def get_input_by_binary(self, input_type: str = ""):
        try:
            if self.input_type_rt == "featuremap" or "float" in input_type:
                image = np.fromfile(self.image, dtype=np.float32)
            else:
                image = np.fromfile(self.image, dtype=np.uint8)
        except Exception as e:
            logging.error(str(e))
            raise ValueError("failed to load data from file input_img")

        try:
            if self.input_type_rt == "nv12":
                image = np.array(np.split(image, self.input_shape[0]))
            else:
                image = image.reshape(self.input_shape)
        except Exception:
            raise ValueError(f"failed to reshape input data size {image.size} "
                             f"to input shape {self.input_shape}")

        return image

    def read_picture(self):
        if self.input_type_rt == 'gray':
            color_mode = cv2.IMREAD_GRAYSCALE
        else:
            color_mode = cv2.IMREAD_COLOR

        width, height = self.get_wh()
        image = cv2.imread(self.image, color_mode)
        try:
            return cv2.resize(image, (width, height),
                              interpolation=cv2.INTER_AREA)
        except Exception:
            raise ValueError('opencv resize failed. '
                             f'The size of {self.image} is not as expected.')

    def get_input_by_transformer(self, image):
        if self.input_type_rt == "gray":
            image = image[:, :, np.newaxis]

        if self.input_type_rt == "nv12":
            transformer = BGR2NV12Transformer(data_format="HWC",
                                              cvt_mode="opencv")
            image = transformer([image])[0]

        if self.input_type_rt == "yuv444":
            image = image.astype(np.float32)
            transformer = BGR2YUV444Transformer(data_format="HWC")
            image = transformer([image])[0]
            image = image.astype(np.uint8)

        if self.input_type_rt != "nv12" and self.input_layout_rt == "NCHW":
            transformer = HWC2CHWTransformer()
            image = transformer([image])[0]

        return np.array([image])

    def get_input_by_batch(self, image):
        if self.input_source == 'resizer':
            return image
        input_data = []
        for i in range(int(self.input_batch)):
            input_data.append(image[0])
        return np.array(input_data)

    def get_input_by_picture(self):
        if self.input_type_rt == "featuremap":
            raise ValueError("For the type of featuremap, "
                             "please give the preprocessed image file")
        image = self.read_picture()
        image = self.get_input_by_transformer(image)

        if int(self.input_batch) > 1:
            image = self.get_input_by_batch(image)

        return np.array(image)

    def get_input_by_nv12_to_yuv444(self):
        target_size = self.get_wh()[::-1]
        transformer = NV12ToYUV444Transformer(target_size=target_size)
        image = transformer(self.image)
        if self.input_layout_rt == "NCHW":
            transformer = HWC2CHWTransformer()
            image = transformer(image)
        return np.array(image)

    def get_input_by_transpose(self):
        image = self.image
        # This image comes from the bin model input,
        # resizer model does not support batch merge inputs.
        if self.input_source == 'resizer':
            image = np.repeat(image, repeats=self.input_batch, axis=0)
        image_shape = list(image.shape)
        logging.debug(f"image shape: {image_shape}")

        if self.input_shape[0] == 1 and int(self.input_batch) > 1:
            self.input_shape[0] = int(self.input_batch)
        logging.debug(f"input shape: {self.input_shape}")

        if sorted(image_shape) != sorted(self.input_shape):
            logging.debug(image_shape, self.input_shape)
            raise ValueError("The shape of the input data does not match "
                             "the input shape of the model. Please check.")

        index_list = get_index_list(self.input_shape, image_shape)
        logging.debug(f"transpose: {index_list}")
        image = image.transpose(index_list)
        logging.debug(f"input data shape: {image.shape}")
        return image

    def get_input_data_for_bin(self):
        if self.image is None or self.image == "":
            input_data = self.get_input_by_random_number()

            if self.input_shape[0] == 1 and int(self.input_batch) > 1:
                input_data = self.get_input_by_batch(input_data)

            return input_data

        if self.image.endswith(".bin"):
            return self.get_input_by_binary()

        if len(self.input_shape) != 4:
            raise ValueError(
                "The pre-processing of non four-dimensional input "
                "does not support the image format temporarily.")
        return self.get_input_by_picture()

    def get_input_date_for_onnx(self, input_type: str = ""):
        if self.image is None or (isinstance(self.image, np.ndarray)
                                  and self.image.size == 0):
            raise ValueError(
                "When reasoning with the separate onnx model, "
                "you need to specify the image after preprocessing.")

        if isinstance(self.image, str):
            self.image = self.get_input_by_binary()

        if isinstance(self.image, np.ndarray):
            if self.input_type_rt == "nv12":
                self.image = self.get_input_by_nv12_to_yuv444()
            return self.get_input_by_transpose()

        if self.image.endswith(".bin"):
            return self.get_input_by_binary(input_type)

        raise ValueError("The onnx model cannot use images without "
                         "pre-processing for reasoning")
