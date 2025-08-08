"""
Copyright Wenyi Tang 2025

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

Test nested Config

Example:

    a = Config()
    a.b = Config()

    a.to_dict()
    # {"b": {}}
"""

from mme.config import Config


def test_normal_config_to_dict_no_nested():
    a = Config()
    b = Config(a.to_dict())
    assert a.to_dict() == {}
    assert b.to_dict() == {}  # a is merged into b


def test_nested_config_to_dict():
    a = Config({"a": 0})
    a.b = Config({"b": 1})
    assert a.to_dict() == dict(a=0, b=dict(b=1))

    del a.b
    assert a.to_dict() == dict(a=0)

    a.c = dict(c=2)
    assert a.to_dict() == dict(a=0, c=dict(c=2))

    del a.c
    a.d = dict(d=Config({"d": 3}))
    assert a.to_dict() == dict(a=0, d=dict(d=dict(d=3)))


def test_nested_config_pretty_text():
    a = Config({"a": 0})
    a.b = Config({"b": 1})
    a.c = dict(c=2)
    a.d = dict(d=Config({"d": 3}))
    print(a.pretty_text)
