"""
Copyright Wenyi Tang 2025

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

Test config update to keep old values.

Example:

    with read_base():
        from .base import dict_y  # where dict_y has dict_x

    # dict_y["x"] == dict(x=1)"
    dict_y["x"] = dict(y=2)
"""

import os.path as osp

from mme.config import Config

data_path = osp.join(osp.dirname(osp.dirname(__file__)), "data/")


def test_config_inheritance():
    cfg = Config.fromfile(
        osp.join(data_path, "config/lazy_module_config/test_inheritance.py")
    )
    assert "x" in cfg.dict_y["x"]
    assert cfg.dict_y["x"]["x"] == 1
    assert cfg.dict_y["x"]["y"] == 2
