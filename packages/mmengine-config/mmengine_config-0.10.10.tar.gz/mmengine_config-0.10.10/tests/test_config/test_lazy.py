# Copyright (c) OpenMMLab. All rights reserved.
import ast
import copy
import os.path as osp
from importlib import import_module
from importlib.util import find_spec
from typing import Any, Dict
from unittest import TestCase

import numpy
import numpy.linalg as linalg
from rich.progress import Progress

from mme.config.lazy import LazyAttr, LazyObject
from mme.config.utils import ImportTransformer, _gather_abs_import_lazyobj


class TestImportTransformer(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data_dir = osp.join(  # type: ignore
            osp.dirname(__file__), "..", "data", "config", "lazy_module_config"
        )
        super().setUpClass()

    def test_lazy_module(self):
        cfg_path = osp.join(self.data_dir, "test_ast_transform.py")
        with open(cfg_path) as f:
            codestr = f.read()
        codeobj = ast.parse(codestr)
        global_dict: Dict[str, Any] = {
            "LazyObject": LazyObject,
        }
        base_dict = {
            "._base_.default_runtime": {"default_scope": "test_config"},
            "._base_.scheduler": {"val_cfg": {}},
        }
        codeobj = ImportTransformer(global_dict, base_dict).visit(codeobj)
        codeobj, _ = _gather_abs_import_lazyobj(codeobj)
        codeobj = ast.fix_missing_locations(codeobj)

        exec(compile(codeobj, cfg_path, mode="exec"), global_dict, global_dict)
        # 1. absolute import
        # 1.1 import module as LazyObject
        lazy_numpy = global_dict["numpy"]
        self.assertIsInstance(lazy_numpy, LazyObject)

        # 1.2 getattr as LazyAttr
        self.assertIsInstance(lazy_numpy.linalg, LazyAttr)
        self.assertIsInstance(lazy_numpy.compat, LazyAttr)

        # 1.3 Build module from LazyObject. amp and functional can be accessed
        imported_numpy = lazy_numpy.build()
        self.assertIs(imported_numpy.linalg, linalg)

        # 1.4.1 Build module from LazyAttr
        imported_linalg = lazy_numpy.linalg.build()
        self.assertIs(imported_linalg, linalg)

        # 1.4.2 build class method from LazyAttr
        start = global_dict["start"]
        self.assertEqual(start.module, "rich.progress.Progress")
        self.assertEqual(str(start), "start")
        self.assertIs(start.build(), Progress.start)

        # 1.5 import ... as, and build module from LazyObject
        lazy_linalg = global_dict["linalg"]
        self.assertIsInstance(lazy_linalg, LazyObject)
        self.assertIs(lazy_linalg.build(), linalg)
        self.assertIsInstance(lazy_linalg.norm, LazyAttr)
        self.assertIs(lazy_linalg.norm.build(), linalg.norm)

        # 2.3 from ... import builtin module or obj from `mmengine.Config`
        self.assertIs(global_dict["find_module"], find_spec)

        # 3 test import base config
        # 3.1 simple from ... import and from ... import ... as
        self.assertEqual(global_dict["scope"], "test_config")
        self.assertDictEqual(global_dict["val_cfg"], {})

        # 4. Error catching
        cfg_path = osp.join(self.data_dir, "test_ast_transform_error_catching1.py")
        with open(cfg_path) as f:
            codestr = f.read()
        codeobj = ast.parse(codestr)
        global_dict = {"LazyObject": LazyObject}
        with self.assertRaisesRegex(
            RuntimeError, r"Illegal syntax in config! `from xxx import \*`"
        ):
            codeobj = ImportTransformer(global_dict).visit(codeobj)


class TestLazyObject(TestCase):

    def test_init(self):
        LazyObject("mmengine")
        LazyObject("mmengine.fileio")
        LazyObject("mmengine.fileio", "LocalBackend")

        # module must be str
        with self.assertRaises(TypeError):
            LazyObject(1)

        # imported must be a sequence of string or None
        with self.assertRaises(TypeError):
            LazyObject("mmengine", ["error_type"])

    def test_build(self):
        lazy_mmengine = LazyObject("mmengine")
        mmengine = import_module("mmengine")
        self.assertIs(lazy_mmengine.build(), mmengine)

        lazy_mmengine_fileio = LazyObject("mmengine.fileio")
        self.assertIs(lazy_mmengine_fileio.build(), import_module("mmengine.fileio"))

        lazy_local_backend = LazyObject("mmengine.fileio", "LocalBackend")
        LocalBackend = import_module("mmengine.fileio").LocalBackend
        self.assertIs(lazy_local_backend.build(), LocalBackend)

        # TODO: The commented test is required, we need to test the built
        # LazyObject can access the `mmengine.dataset`. We need to clean the
        # environment to make sure the `dataset` is not imported before, and
        # it is triggered by lazy_mmengine.build(). However, if we simply
        # pop the `mmengine.dataset` will lead to other tests failed, of which
        # reason is still unknown. We need to figure out the reason and fix it
        # in the latter

        # sys.modules.pop('mmengine.config')
        # sys.modules.pop('mmengine.fileio')
        # sys.modules.pop('mmengine')
        # lazy_mmengine = LazyObject(['mmengine', 'mmengine.dataset'])
        # self.assertIs(lazy_mmengine.build().dataset,
        #               import_module('mmengine.config'))
        copied = copy.deepcopy(lazy_local_backend)
        self.assertDictEqual(copied.__dict__, lazy_local_backend.__dict__)

        with self.assertRaises(RuntimeError):
            lazy_mmengine()

        with self.assertRaises(ImportError):
            LazyObject("unknown").build()


class TestLazyAttr(TestCase):
    # Since LazyAttr should only be built from LazyObect, we only test
    # the build method here.
    def test_build(self):
        lazy_mmengine = LazyObject("mmengine")
        local_backend = lazy_mmengine.fileio.LocalBackend
        LocalBackend = import_module("mmengine.fileio").LocalBackend
        self.assertIs(local_backend.build(), LocalBackend)

        copied = copy.deepcopy(local_backend)
        self.assertDictEqual(copied.__dict__, local_backend.__dict__)

        self.assertIsInstance(local_backend(), LocalBackend)

        with self.assertRaisesRegex(
            ImportError, "Failed to import mmengine.fileio.LocalBackend.unknown"
        ):
            local_backend.unknown.build()
