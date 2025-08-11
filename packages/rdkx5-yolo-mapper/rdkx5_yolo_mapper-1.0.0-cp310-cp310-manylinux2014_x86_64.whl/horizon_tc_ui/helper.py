# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import logging

from horizon_tc_ui.data.transformer import AddTransformer, \
    RGB2BGRTransformer, RGB2NV12Transformer, NV12ToYUV444Transformer, \
    RGB2YUV444Transformer, ResizeTransformer, ScaleTransformer, \
    HWC2CHWTransformer, RGB2GRAY_128Transformer, \
    RGB2YUVBT601VIDEOTransformer, BGR2RGBTransformer, BGR2NV12Transformer, \
    BGR2YUV444Transformer, BGR2YUVBT601VIDEOTransformer


class ModelProtoBase:
    def __init__(self):
        pass

    def get_input_names(self):
        raise NotImplementedError

    def get_input_dims(self, input_name):
        return []


def get_raw_transformer(input_type_rt, input_type_train, input_layout_train,
                        image_height, image_width):

    data_format = input_layout_train[1:]
    if input_type_train == "rgb":
        if input_type_rt in ["rgb"]:
            return [AddTransformer(-128)]
        elif input_type_rt in ["bgr"]:
            return [
                RGB2BGRTransformer(data_format=data_format),
                AddTransformer(-128)
            ]
        elif input_type_rt in [
                'nv12',
        ]:
            return [
                RGB2NV12Transformer(data_format=data_format),
                NV12ToYUV444Transformer((image_height, image_width),
                                        yuv444_output_layout=data_format),
                AddTransformer(-128)
            ]
        elif input_type_rt in ['yuv444', 'yuv444_128']:
            return [
                RGB2YUV444Transformer(data_format=data_format),
                AddTransformer(-128)
            ]
        elif input_type_rt in ["yuv420sp_bt601_video"]:
            return [RGB2YUVBT601VIDEOTransformer(data_format=data_format)]
        else:
            logging.warning(f"transform from {input_type_train} to "
                            f"{input_type_rt} is not supported.")
            logging.warning("Trying default transformer (-128) only")
            return [AddTransformer(-128)]

    elif input_type_train == "bgr":
        if input_type_rt in ["bgr"]:
            return [AddTransformer(-128)]
        elif input_type_rt in ["rgb"]:
            return [
                BGR2RGBTransformer(data_format=data_format),
                AddTransformer(-128)
            ]
        elif input_type_rt in [
                'nv12',
        ]:
            return [
                BGR2NV12Transformer(data_format=data_format),
                NV12ToYUV444Transformer((image_height, image_width),
                                        yuv444_output_layout=data_format),
                AddTransformer(-128)
            ]
        elif input_type_rt in ['yuv444', 'yuv444_128']:
            return [
                BGR2YUV444Transformer(data_format=data_format),
                AddTransformer(-128)
            ]
        elif input_type_rt in ["yuv420sp_bt601_video"]:
            return [BGR2YUVBT601VIDEOTransformer(data_format=data_format)]
        else:
            logging.warning(f"transform from {input_type_train} to "
                            f"{input_type_rt} is not supported.")
            logging.warning("Trying default transformer (-128) only")
            return [AddTransformer(-128)]

    elif input_type_train == "yuv444":
        if input_type_rt in ['yuv444', "yuv444_128", "nv12"]:
            return [AddTransformer(-128)]
        else:
            logging.warning(f"transform from {input_type_train} to "
                            f"{input_type_rt} is not supported.")
            logging.warning("Trying default transformer (-128) only")
            return [AddTransformer(-128)]

    elif input_type_train == "gray":
        if input_type_rt in ["gray"]:
            return [AddTransformer(-128)]
        else:
            logging.warning(f"transform from {input_type_train} to "
                            f"{input_type_rt} is not supported.")
            logging.warning("Trying default transformer (-128) only")
            return [AddTransformer(-128)]

    elif input_type_train.startswith('featuremap'):
        if input_type_rt == input_type_train:
            return []
        else:
            logging.warning(f"transform from {input_type_train} to "
                            f"{input_type_rt} is not supported.")
            logging.warning("No default transformer used")
            return []
    else:
        logging.warning(f"transform from {input_type_train} to "
                        f"{input_type_rt} is not supported.")
        logging.warning("Trying default transformer (-128) only")
        return [AddTransformer(-128)]


def get_default_transformer(input_type_rt, input_type_train,
                            input_layout_train, image_height, image_width):
    transformers = [
        ResizeTransformer((image_height, image_width)),
        ScaleTransformer(255),
    ]

    # 如果模型输入是NCHW, 则需要把读进来的图片(NHWC)转换一下layout
    if input_layout_train != "NHWC":
        transformers += HWC2CHWTransformer(),

    layout = input_layout_train[1:]
    trans_dict = {
        'rgb': [AddTransformer(-128)],
        'rgbp': [AddTransformer(-128)],
        'bgr': [RGB2BGRTransformer(data_format=layout),
                AddTransformer(-128)],
        'bgrp': [RGB2BGRTransformer(data_format=layout),
                 AddTransformer(-128)],
        'nv12': [
            RGB2NV12Transformer(data_format=layout),
            NV12ToYUV444Transformer((image_height, image_width),
                                    yuv444_output_layout=layout),
            AddTransformer(-128)
        ],
        'yuv444': [
            RGB2YUV444Transformer(data_format=layout),
            AddTransformer(-128)
        ],
        # 'yuv444': [RGB2YUV444_128Transformer(data_format=layout)],
        'yuv444_128': [
            RGB2YUV444Transformer(data_format=layout),
            AddTransformer(-128)
        ],
        'gray': [RGB2GRAY_128Transformer(data_format=layout)],
        'yuv420sp_bt601_video': [
            RGB2YUVBT601VIDEOTransformer(data_format=layout)
        ],
    }
    transformers += trans_dict[input_type_rt]
    return transformers
