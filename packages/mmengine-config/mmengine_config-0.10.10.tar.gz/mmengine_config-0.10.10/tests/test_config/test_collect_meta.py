# Copyright (c) OpenMMLab. All rights reserved.
import os.path

import pytest

from mme.config.utils import _get_external_cfg_base_path, _get_package_and_cfg_path

try:
    import mmdet

    mmdet_fail = False
except ImportError:
    mmdet_fail = True


def test_get_external_cfg_base_path(tmp_path):
    package_path = tmp_path
    rel_cfg_path = os.path.join("cfg_dir", "cfg_file")
    cfg_dir = tmp_path / ".mim" / "configs" / "cfg_dir"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    f = open(cfg_dir / "cfg_file", "w")
    f.close()
    cfg_path = _get_external_cfg_base_path(str(package_path), rel_cfg_path)
    assert cfg_path == f'{os.path.join(str(cfg_dir), "cfg_file")}'


@pytest.mark.skipif(mmdet_fail, reason="mmdet is not installed")
def test_get_external_cfg_path():
    external_cfg_path = "mmdet::path/cfg"
    package, rel_cfg_path = _get_package_and_cfg_path(external_cfg_path)
    assert package == "mmdet"
    assert rel_cfg_path == "path/cfg"
    # external config must contain `::`.
    external_cfg_path = "path/cfg"
    with pytest.raises(ValueError):
        _get_package_and_cfg_path(external_cfg_path)
    # Use `:::` as operator will raise an error.
    external_cfg_path = "mmdet:::path/cfg"
    with pytest.raises(ValueError):
        _get_package_and_cfg_path(external_cfg_path)
    # Use `:` as operator will raise an error.
    external_cfg_path = "mmdet:path/cfg"
    with pytest.raises(ValueError):
        _get_package_and_cfg_path(external_cfg_path)
    # Too much `::`
    external_cfg_path = "mmdet::path/cfg::error"
    with pytest.raises(ValueError):
        _get_package_and_cfg_path(external_cfg_path)
