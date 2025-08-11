# Copyright (c) 2024 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

from dataclasses import dataclass
from typing import Any


@dataclass
class ConfigBase:
    def get(self, name: str, value: Any = None) -> Any:
        res = getattr(self, name, value)
        return res

    def __getitem__(self, item: str) -> Any:
        res = getattr(self, item)
        if res is None:
            raise KeyError(item)
        return res

    def __setitem__(self, item_name: str, item_value: Any) -> None:
        setattr(self, item_name, item_value)
