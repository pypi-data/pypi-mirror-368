# Copyright (c) 2021 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.
import logging

from horizon_tc_ui.data.transformer import ShortSideResizeTransformer, \
    CenterCropTransformer, HWC2CHWTransformer, RGB2BGRTransformer, \
    ScaleTransformer, BGR2NV12Transformer, PaddedCenterCropTransformer, \
    ResizeTransformer, RGB2NV12Transformer, PadResizeTransformer, \
    BGR2RGBTransformer, WarpAffineTransformer, PadTransformer


def mobilenet_data_transformer():
    transformers = [
        ShortSideResizeTransformer(short_size=256),
        CenterCropTransformer(crop_size=224),
        HWC2CHWTransformer(),
        RGB2BGRTransformer(data_format="CHW"),
        ScaleTransformer(scale_value=255),
        BGR2NV12Transformer(data_format="CHW")
    ]
    return transformers, (224, 224)


def googlenet_data_transformer():
    transformers = [
        ShortSideResizeTransformer(short_size=256),
        CenterCropTransformer(crop_size=224),
        BGR2NV12Transformer(data_format="HWC"),
    ]
    return transformers, (224, 224)


def resnet18_data_transformer():
    transformers = [
        ShortSideResizeTransformer(short_size=256),
        CenterCropTransformer(crop_size=224),
        HWC2CHWTransformer(),
        RGB2BGRTransformer(data_format="CHW"),
        ScaleTransformer(scale_value=255),
        BGR2NV12Transformer(data_format="CHW")
    ]
    return transformers, (224, 224)


def efficientnet_lite0_data_transformer():
    image_size = 224
    transformers = [
        PaddedCenterCropTransformer(image_size=image_size, crop_pad=32),
        ResizeTransformer(target_size=(image_size, image_size),
                          mode='skimage',
                          method=3),
        HWC2CHWTransformer(),
        ScaleTransformer(scale_value=255),
        RGB2NV12Transformer(data_format="CHW")
    ]
    return transformers, (224, 224)


def efficientnet_lite1_data_transformer():
    image_size = 240
    transformers = [
        PaddedCenterCropTransformer(image_size=image_size, crop_pad=32),
        ResizeTransformer(target_size=(image_size, image_size),
                          mode='skimage',
                          method=3),
        HWC2CHWTransformer(),
        ScaleTransformer(scale_value=255),
        RGB2NV12Transformer(data_format="CHW")
    ]
    return transformers, (240, 240)


def efficientnet_lite2_data_transformer():
    image_size = 260
    transformers = [
        PaddedCenterCropTransformer(image_size=image_size, crop_pad=32),
        ResizeTransformer(target_size=(image_size, image_size),
                          mode='skimage',
                          method=3),
        HWC2CHWTransformer(),
        ScaleTransformer(scale_value=255),
        RGB2NV12Transformer(data_format="CHW")
    ]
    return transformers, (260, 260)


def efficientnet_lite3_data_transformer():
    image_size = 280
    transformers = [
        PaddedCenterCropTransformer(image_size=image_size, crop_pad=32),
        ResizeTransformer(target_size=(image_size, image_size),
                          mode='skimage',
                          method=3),
        HWC2CHWTransformer(),
        ScaleTransformer(scale_value=255),
        RGB2NV12Transformer(data_format="CHW")
    ]
    return transformers, (280, 280)


def efficientnet_lite4_data_transformer():
    image_size = 300
    transformers = [
        PaddedCenterCropTransformer(image_size=image_size, crop_pad=32),
        ResizeTransformer(target_size=(image_size, image_size),
                          mode='skimage',
                          method=3),
        HWC2CHWTransformer(),
        ScaleTransformer(scale_value=255),
        RGB2NV12Transformer(data_format="CHW")
    ]
    return transformers, (300, 300)


def vargconvnet_data_transformer():
    image_size = 224
    transformers = [
        ResizeTransformer(target_size=(256, 256)),
        CenterCropTransformer(crop_size=image_size),
        HWC2CHWTransformer(),
        RGB2NV12Transformer(data_format="CHW"),
    ]
    return transformers, (224, 224)


def yolov2_darknet19_data_transformer():
    input_shape = (608, 608)
    transformers = [
        PadResizeTransformer(target_size=input_shape),
        HWC2CHWTransformer(),
        BGR2RGBTransformer(data_format="CHW"),
        RGB2NV12Transformer(data_format="CHW")
    ]
    return transformers, input_shape


def yolov3_darknet53_data_transformer():
    input_shape = (416, 416)
    transformers = [
        PadResizeTransformer(target_size=input_shape),
        HWC2CHWTransformer(),
        BGR2RGBTransformer(data_format="CHW"),
        RGB2NV12Transformer(data_format="CHW")
    ]
    return transformers, input_shape


def yolov3_vargdarknet_data_transformer():
    input_shape = (416, 416)
    transformers = [
        ResizeTransformer(input_shape),  # input_shape (416, 416)
        BGR2NV12Transformer(data_format="HWC", cvt_mode="opencv"),
    ]
    return transformers, input_shape


def yolov4_efficientnetb0_data_transformer():
    input_shape = (512, 512)
    transformers = [
        PadResizeTransformer(target_size=input_shape,
                             pad_position='bottom_right'),
        BGR2NV12Transformer(data_format="HWC"),
    ]
    return transformers, input_shape


def yolov5_data_transformer():
    input_shape = (672, 672)
    transformers = [
        PadResizeTransformer(target_size=input_shape),
        HWC2CHWTransformer(),
        BGR2RGBTransformer(data_format="CHW"),
        RGB2NV12Transformer(data_format="CHW")
    ]
    return transformers, input_shape


def ssd_mobilenetv1_data_transformer():
    input_shape = (300, 300)
    transformers = [
        ResizeTransformer(target_size=input_shape, mode='opencv', method=1),
        HWC2CHWTransformer(),
        BGR2NV12Transformer(data_format="CHW")
    ]
    return transformers, input_shape


def efficientdetd0_data_transformer():
    input_shape = (512, 512)
    transformers = [
        PadResizeTransformer(target_size=input_shape,
                             pad_value=0.,
                             pad_position='bottom_right'),
        HWC2CHWTransformer(),
        BGR2RGBTransformer(data_format="CHW"),
        RGB2NV12Transformer(data_format="CHW")
    ]
    return transformers, input_shape


def efficient_det_data_transformer():
    input_shape = (512, 512)
    transformers = [
        PadResizeTransformer(target_size=input_shape,
                             pad_value=0.,
                             pad_position='bottom_right'),
        HWC2CHWTransformer(),
        BGR2RGBTransformer(data_format="CHW"),
        RGB2NV12Transformer(data_format="CHW")
    ]
    return transformers, input_shape


def unet_mobilenet_data_transformer():
    input_shape = (1024, 2048)
    transformers = [
        ResizeTransformer(input_shape),
        BGR2RGBTransformer(data_format="HWC"),
        RGB2NV12Transformer(data_format="HWC", cvt_mode="opencv")
    ]
    return transformers, input_shape


def mobilenet_onnx_data_transformer():
    input_shape = (224, 224)
    transformers = [
        ShortSideResizeTransformer(short_size=256),
        CenterCropTransformer(crop_size=224),
        HWC2CHWTransformer(),
        ScaleTransformer(scale_value=255),
        RGB2NV12Transformer(data_format="CHW")
    ]
    return transformers, input_shape


def centernet_data_transformer():
    input_shape = (512, 512)
    transformers = [
        BGR2RGBTransformer(data_format="HWC"),
        WarpAffineTransformer(input_shape, 1.0),
        HWC2CHWTransformer(),
        RGB2NV12Transformer(data_format="CHW")
    ]
    return transformers, input_shape


def fcos_efficientnetb0_data_transformer():
    input_shape = (512, 512)
    transformers = [
        PadResizeTransformer((512, 512),
                             pad_position='bottom_right',
                             pad_value=0),
        BGR2NV12Transformer(data_format="HWC", cvt_mode="opencv")
    ]
    return transformers, input_shape


def fcos_resnet50_data_transformer():
    input_shape = (1024, 1024)
    transformers = [
        PadTransformer(size_divisor=1024, target_size=1024),
        BGR2NV12Transformer(data_format="HWC", cvt_mode="opencv")
    ]
    return transformers, input_shape


def fcos_resnext_data_transformer():
    input_shape = (1024, 1024)
    transformers = [
        PadTransformer(size_divisor=1024, target_size=1024),
        BGR2NV12Transformer(data_format="HWC", cvt_mode="opencv")
    ]
    return transformers, input_shape


def deeplabv3plus_efficientnetb0_data_transformer():
    input_shape = (1024, 2048)
    transformers = [
        ResizeTransformer(input_shape),
        BGR2NV12Transformer(data_format="HWC", cvt_mode="opencv"),
    ]
    return transformers, input_shape


def fastscnn_efficientnetb0_data_transformer():
    input_shape = (1024, 2048)
    transformers = [
        ResizeTransformer(input_shape),
        BGR2NV12Transformer(data_format="HWC", cvt_mode="opencv"),
    ]
    return transformers, input_shape


def efficientnasnet_m_data_transformer():
    input_shape = (300, 300)
    transformers = [
        BGR2RGBTransformer(data_format="HWC"),
        ShortSideResizeTransformer(short_size=256,
                                   data_type="uint8",
                                   interpolation="INTER_CUBIC"),
        CenterCropTransformer(crop_size=224, data_type="uint8"),
        ResizeTransformer(target_size=(300, 300),
                          data_type="uint8",
                          mode='opencv',
                          method=1,
                          interpolation="INTER_CUBIC"),
        RGB2NV12Transformer(data_format="HWC", cvt_mode="opencv"),
    ]
    return transformers, input_shape


def efficientnasnet_s_data_transformer():
    input_shape = (280, 280)
    transformers = [
        BGR2RGBTransformer(data_format="HWC"),
        ShortSideResizeTransformer(short_size=256,
                                   data_type="uint8",
                                   interpolation="INTER_CUBIC"),
        CenterCropTransformer(crop_size=224, data_type="uint8"),
        ResizeTransformer(target_size=(280, 280),
                          data_type="uint8",
                          mode='opencv',
                          method=1,
                          interpolation="INTER_CUBIC"),
        RGB2NV12Transformer(data_format="HWC", cvt_mode="opencv"),
    ]
    return transformers, input_shape


def deeplabv3plus_dilation1248_data_transformer():
    input_shape = (1024, 2048)
    transformers = [
        ResizeTransformer((1024, 2048)),
        BGR2NV12Transformer(data_format="HWC", cvt_mode="opencv"),
    ]
    return transformers, input_shape


def deeplabv3plus_efficientnet_data_transformer():
    input_shape = (1024, 2048)
    transformers = [
        ResizeTransformer(input_shape),
        BGR2NV12Transformer(data_format="HWC", cvt_mode="opencv"),
    ]
    return transformers, input_shape


def fcos_efficientnetb1_data_transformer():
    input_shape = (640, 640)
    transformers = [
        PadResizeTransformer(input_shape,
                             pad_position='bottom_right',
                             pad_value=0),
        BGR2NV12Transformer(data_format="HWC", cvt_mode="opencv"),
    ]
    return transformers, input_shape


def fcos_efficientnetb2_data_transformer():
    input_shape = (768, 768)
    transformers = [
        PadResizeTransformer((768, 768),
                             pad_position='bottom_right',
                             pad_value=0),
        BGR2NV12Transformer(data_format="HWC", cvt_mode="opencv"),
    ]
    return transformers, input_shape


def fcos_efficientnetb3_data_transformer():
    input_shape = (896, 896)
    transformers = [
        PadResizeTransformer((896, 896),
                             pad_position='bottom_right',
                             pad_value=0),
        BGR2NV12Transformer(data_format="HWC", cvt_mode="opencv"),
    ]
    return transformers, input_shape


data_transformer_info = {
    "mobilenetv1":
        mobilenet_data_transformer(),
    "mobilenetv2":
        mobilenet_data_transformer(),
    "googlenet":
        googlenet_data_transformer(),
    "resnet18":
        resnet18_data_transformer(),
    "efficientnet_lite0":
        efficientnet_lite0_data_transformer(),
    "efficientnet_lite1":
        efficientnet_lite1_data_transformer(),
    "efficientnet_lite2":
        efficientnet_lite2_data_transformer(),
    "efficientnet_lite3":
        efficientnet_lite3_data_transformer(),
    "efficientnet_lite4":
        efficientnet_lite4_data_transformer(),
    "vargconvnet":
        vargconvnet_data_transformer(),
    "yolov2":
        yolov2_darknet19_data_transformer(),
    "yolov2_darknet19":
        yolov2_darknet19_data_transformer(),
    "yolov3":
        yolov3_darknet53_data_transformer(),
    "yolov3_darknet53":
        yolov3_darknet53_data_transformer(),
    "yolov3_vargdarknet":
        yolov3_vargdarknet_data_transformer(),
    "yolov4_efficientnetb0":
        yolov4_efficientnetb0_data_transformer(),
    "yolov5":
        yolov5_data_transformer(),
    "yolov5s":
        yolov5_data_transformer(),
    "yolov5x":
        yolov5_data_transformer(),
    "mobilenet_ssd":
        ssd_mobilenetv1_data_transformer(),
    "ssd_mobilenetv1":
        ssd_mobilenetv1_data_transformer(),
    "efficientdetd0":
        efficientdetd0_data_transformer(),
    "efficient_det":
        efficientdetd0_data_transformer(),
    "mobilenet_unet":
        unet_mobilenet_data_transformer(),
    "unet_mobilenet":
        unet_mobilenet_data_transformer(),
    "mobilenet_onnx":
        mobilenet_onnx_data_transformer(),
    "centernet":
        centernet_data_transformer(),
    "centernet_resnet50":
        centernet_data_transformer(),
    "centernet_resnet101":
        centernet_data_transformer(),
    "fcos_efficientnetb0":
        fcos_efficientnetb0_data_transformer(),
    "fcos":
        fcos_efficientnetb0_data_transformer(),
    "fcos_resnet50":
        fcos_resnet50_data_transformer(),
    "fcos_resnext":
        fcos_resnext_data_transformer(),
    "deeplabv3plus_efficientnetb0":
        deeplabv3plus_efficientnetb0_data_transformer(),
    "fastscnn_efficientnetb0":
        fastscnn_efficientnetb0_data_transformer(),
    "efficientnasnet_m":
        efficientnasnet_m_data_transformer(),
    "efficientnasnet_s":
        efficientnasnet_s_data_transformer(),
    "deeplabv3plus_dilation1248":
        deeplabv3plus_dilation1248_data_transformer(),
    "deeplabv3plus_efficientnetm1":
        deeplabv3plus_efficientnet_data_transformer(),
    "deeplabv3plus_efficientnetm2":
        deeplabv3plus_efficientnet_data_transformer(),
    "community_qat_fcos_efficientnetb0":
        fcos_efficientnetb0_data_transformer(),
    "community_qat_fcos_efficientnetb2":
        fcos_efficientnetb2_data_transformer(),
    "community_qat_fcos_efficientnetb3":
        fcos_efficientnetb3_data_transformer(),
    "preq_qat_fcos_efficientnetb0":
        fcos_efficientnetb0_data_transformer(),
    "preq_qat_fcos_efficientnetb1":
        fcos_efficientnetb1_data_transformer(),
    "preq_qat_fcos_efficientnetb2":
        fcos_efficientnetb2_data_transformer(),
    "preq_qat_fcos_efficientnetb3":
        fcos_efficientnetb3_data_transformer(),
}


def get_data_transformer_info(model_name):
    transformers, dst = data_transformer_info.get(model_name)
    if transformers is None:
        logging.error("model type input wrong!!!")
        logging.info(
            "accepted model type: "
            f"{str(', '.join([i for i in data_transformer_info.keys()]))}")
        exit(1)
    return transformers, dst
