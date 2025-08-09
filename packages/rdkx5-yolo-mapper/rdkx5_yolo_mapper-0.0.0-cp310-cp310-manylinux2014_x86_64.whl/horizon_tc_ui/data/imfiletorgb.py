# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import numpy as np
import struct
import sys, getopt
import cv2, os, re


def image_to_bgr(img_file, shape_c_h_w, im_type, output_dir):
    print("converting begins ...")
    image = cv2.imdecode(np.fromfile(img_file, dtype=np.uint8), -1)
    image = cv2.resize(image, (shape_c_h_w[2], shape_c_h_w[1]))
    image = image.astype('uint8')
    b, g, r = cv2.split(image)
    height = image.shape[0]
    width = image.shape[1]
    channels = image.shape[2]
    file_base = os.path.basename(img_file).split('.')[0]
    file_path = os.path.dirname(img_file)
    if im_type == 'bgr':
        file_base = file_base + ".bgr"
    elif im_type == 'rgb':
        file_base = file_base + ".rgb"
    else:
        print("not support this file type")

    dest_file = os.path.join(file_path, file_base)
    fileSave = open(dest_file, 'wb')
    if im_type == 'bgr':
        for step in range(0, height):
            for step2 in range(0, width):
                fileSave.write(b[step, step2])
        for step in range(0, height):
            for step2 in range(0, width):
                fileSave.write(g[step, step2])
        for step in range(0, height):
            for step2 in range(0, width):
                fileSave.write(r[step, step2])
    elif im_type == 'rgb':
        for step in range(0, height):
            for step2 in range(0, width):
                fileSave.write(r[step, step2])
        for step in range(0, height):
            for step2 in range(0, width):
                fileSave.write(g[step, step2])
        for step in range(0, height):
            for step2 in range(0, width):
                fileSave.write(b[step, step2])

    fileSave.close()
    print("converting finished ...")
