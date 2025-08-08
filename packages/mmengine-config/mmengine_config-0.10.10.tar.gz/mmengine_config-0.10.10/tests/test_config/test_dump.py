import tempfile

from mme.config import Config, ConfigDict
from mme.config.lazy import LazyObject


def test_reload_from_dump_lazyobject():
    """Test that LazyObject can be reloaded from a dumped config."""
    lazy_obj = LazyObject("mme.config.config", "Config")
    ConfigDict.lazy = True
    cfg = Config(ConfigDict({"dataset": {"type": lazy_obj}}))
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg.dump(tmpdir + "/config.py")
        new_cfg = Config.fromfile(tmpdir + "/config.py")
    assert new_cfg.dataset.type == "mme.config.config.Config"


def test_reload_from_dump():
    """Test that a dumped config can be reloaded."""
    cfg = Config({"dataset": {"type": Config}})
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg.dump(tmpdir + "/config.py")
        new_cfg = Config.fromfile(tmpdir + "/config.py")
    assert new_cfg.dataset.type == "mme.config.config.Config"
