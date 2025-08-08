# Copyright (c) OpenMMLab. All rights reserved.
from mme.config import read_base

with read_base():
    from .test_base import dict_y

dict_y.update(x=dict(y=2))
