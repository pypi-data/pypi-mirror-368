"""
Copyright Wenyi Tang 2025

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

Test the modify variable out of base scope

Example:

    with read_base():
        from .base import *  # where a crop_size=256 imported
        from .second_base import x, dict_x

    # dict_x["x"] == x
    crop_size = 128
    x = "y"
    # dict_x["x"] == "y"
"""

import os.path as osp

from mme.config import Config

data_path = osp.join(osp.dirname(osp.dirname(__file__)), "data/")


def test_config_change_base_var():
    base_cfg = Config.fromfile(
        osp.join(data_path, "config/lazy_module_config/test_base.py")
    )
    assert base_cfg.x == 1
    assert base_cfg.dict_x["x"] == 1

    cfg = Config.fromfile(
        osp.join(data_path, "config/lazy_module_config/test_change_base_var.py")
    )
    assert cfg.x == 3
    assert cfg.dict_x["x"] == 2
