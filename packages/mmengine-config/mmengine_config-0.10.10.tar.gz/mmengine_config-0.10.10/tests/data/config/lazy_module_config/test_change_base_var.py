# Copyright (c) OpenMMLab. All rights reserved.
from mme.config import read_base

z = "world"
with read_base(x=2, y=[3, 4, 5], z="hello" + z):
    from .test_base import dict_x, dict_y

x = 3
