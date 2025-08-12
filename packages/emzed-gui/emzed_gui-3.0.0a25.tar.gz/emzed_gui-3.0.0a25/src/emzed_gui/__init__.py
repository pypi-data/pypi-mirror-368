# This file is part of emzed (https://emzed.ethz.ch), a software toolbox for analysing
# LCMS data with Python.
#
# Copyright (C) 2020 ETH Zurich, SIS ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.

# ruff: noqa: E402, F401, F821

import collections as _collections
import pdb as _pdb
import sys as _sys  # noqa E402
import warnings as _warnings  # noqa E402
from importlib.metadata import version as _version
from inspect import currentframe as _currentframe  # noqa E402

# patch for guidata: (some classes were moved in python 3.10)
try:
    import collections.abc as _collections_abc

    _collections.__dict__.update(_collections_abc.__dict__)
except (ImportError, AttributeError):
    pass

# fix gettext issues between python versions:
import gettext as _gettext

_orig = _gettext.translation


def _translation(*a, **kw):
    # codeset was removed in python3.11, and does not matter anyhow:
    kw.pop("codeset", None)
    return _orig(*a, **kw)


_gettext.translation = _translation


import numpy as _np

# fix issue with guiqwt not compatible with recent numpy:
_np.float = _np.float64


if _sys.platform == "linux":
    # importing matplotlib crashes on linux, this hack avoids this:
    import ctypes as _ctypes

    try:
        _dll = _ctypes.CDLL("libgcc_s.so.1")
    except OSError:
        pass


class _Dummy:
    def __getattr__(self, name):
        return None


# QtPrintSupport is broken on linux somehow, but we don't need it anyway,
# thus we inject a fake module:
_sys.modules["PyQt5.QtPrintSupport"] = _Dummy()

import guiqwt303 as _guiqwt303

_sys.modules["guiqwt"] = _guiqwt303


__version__ = _version(__package__)

# profile decorator is only predefined when we run code with
# line_profiler (kernprof):
try:
    profile
except NameError:
    __builtins__["profile"] = lambda fun: fun


def _silent_del(self):
    pass


from . import _qt_compat

_qt_compat.install()

with _warnings.catch_warnings():
    # guiqwt creates logs of warnings

    import os as _os

    _os.environ["QT_API"] = "pyqt5"

    _warnings.filterwarnings("ignore")
    from guiqwt.curve import CurvePlot as _CurvePlot

    _CurvePlot.__del__ = _silent_del

    # import to supress warnings during first import:
    import guidata as _guidata

    from .dialog_builder import DialogBuilder
    from .file_dialogs import (
        ask_for_directory,
        ask_for_multiple_files,
        ask_for_save,
        ask_for_single_file,
    )
    from .inspect import inspect
    from .simple_dialogs import ask_yes_no, show_information, show_warning

    # cleanup namespace polution due to implicit imports:

    del simple_dialogs
    del dialog_builder
    del file_dialogs


def _pyqt_enabled_set_trace():
    from PyQt5.QtCore import pyqtRemoveInputHook

    pyqtRemoveInputHook()
    from pdb import set_trace

    is_pdbpp = hasattr(_pdb, "set_tracex")
    if is_pdbpp:
        return _pdb.set_trace(_currentframe().f_back)
    return set_trace()


def qapplication():
    from PyQt5.Qt import QApplication
    from PyQt5.QtCore import Qt

    app = QApplication.instance()
    if not app:
        app = QApplication([])
    if _sys.platform == "darwin":
        import importlib.resources as ir

        from PyQt5.QtGui import QFontDatabase

        # load font for later use:
        font_file = str(ir.files(__package__) / "assets" / "Inconsolata-Regular.ttf")
        QFontDatabase.addApplicationFont(font_file)
    return app


_sys.breakpointhook = _pyqt_enabled_set_trace
