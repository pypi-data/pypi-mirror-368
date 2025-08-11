#! /bin/sh
# Copyright (c) 2024 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.\n\n

set -ex
cd "$(dirname $0)" || exit 1

hrt_model_exec infer \
    --model_file={{ model_file }} \
    --input_file={{ input_file }} \
    --enable_dump=true \
    --dump_format=txt \
    --dump_precision={{ dump_precision }} \
    --dump_intermediate={{ dump_intermediate }} \
    --hybrid_dequantize_process=true \
    {%- if roi_info -%}
    {{ roi_info }}
    {%- endif -%}
    --roi_infer={{ roi_infer }}
