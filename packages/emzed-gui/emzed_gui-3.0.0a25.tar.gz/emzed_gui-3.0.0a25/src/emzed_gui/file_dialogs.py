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


import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QFileDialog

from .simple_dialogs import show_warning


def _normalize_network_paths(paths):
    if sys.platform == "win32":
        # sometimes probs with network paths like "//gram/omics/....":
        return [p.replace("/", "\\") for p in paths]
    return paths


class _FileDialog:
    __app = None

    def __init__(self, start_at=None, extensions=None, caption=None):
        if _FileDialog.__app is None:
            _FileDialog.__app = QApplication([])
        if start_at is None:
            start_at = os.getcwd()
        self.di = QFileDialog(directory=start_at, caption=caption)
        if extensions is not None:
            filter_ = "(%s)" % " ".join("*." + e for e in extensions)
            self.di.setNameFilter(filter_)

    def set_file_mode(self, mode):
        self.di.setFileMode(mode)

    def set_accept_mode(self, mode):
        self.di.setAcceptMode(mode)

    def show(self):
        self.di.setOption(QFileDialog.DontUseNativeDialog)
        self.di.setWindowFlags(Qt.Window)
        self.di.setViewMode(QFileDialog.Detail)
        self.di.activateWindow()
        self.di.raise_()
        if self.di.exec_():
            files = self.di.selectedFiles()
            self.di.close()
            return _normalize_network_paths(files)
        return None


def ask_for_directory(start_at=None, caption="Choose Folder"):
    """
    asks for a single directory.

    you can provide a startup directory with parameter start_at.

    returns the path to the selected directory as a string,
    or None if the user aborts the dialog.
    """
    fd = _FileDialog(start_at=start_at, caption=caption)
    fd.set_file_mode(QFileDialog.Directory)
    result = fd.show()
    if result is not None:
        return result[0]
    return None


def ask_for_save(start_at=None, extensions=None, caption="Save As"):
    """
    asks for a single file, which needs not to exist.

    you can provide a startup directory with parameter start_at.
    you can restrict the files by providing a list of extensions.
    eg::

        askForSave(extensions=["csv"])

    or::

        askForSave(extensions=["mzXML", "mxData"])

    returns the path of the selected file as a string,
    or None if the user aborts the dialog.
    """
    while True:
        fd = _FileDialog(start_at=start_at, extensions=extensions, caption=caption)
        fd.set_file_mode(QFileDialog.AnyFile)
        fd.set_accept_mode(QFileDialog.AcceptSave)
        chosen = fd.show()
        if chosen is not None:
            chosen = chosen[0]
        if (
            chosen is None
            or extensions is None
            or any(chosen.endswith(ext) for ext in extensions)
        ):
            return chosen

        show_warning("please use valid file name extension")


def ask_for_single_file(start_at=None, extensions=None, caption="Open File"):
    """
    asks for a single file.

    you can provide a startup directory with parameter start_at.
    you can restrict the files to select by providing a list
    of extensions.
    eg::

        ask_for_single_file(extensions=["csv"])

    or::

        ask_for_single_file(extensions=["mzXML", "mxData"])

    returns the path of the selected file as a string,
    or None if the user aborts the dialog.
    """
    fd = _FileDialog(start_at=start_at, extensions=extensions, caption=caption)
    fd.set_file_mode(QFileDialog.ExistingFile)
    result = fd.show()
    if result is not None:
        return result[0]
    return None


def ask_for_multiple_files(start_at=None, extensions=None, caption="Open Files"):
    """
    asks for a single or multiple files.

    you can provide a startup directory with parameter start_at.
    you can restrict the files to select by providing a list
    of extensions.
    eg::

        ask_for_multiple_files(extensions=["csv"])

    or::

        ask_for_multiple_files(extensions=["mzXML", "mxData"])

    returns the paths of the selected files as a list of strings,
    or None if the user aborts the dialog.
    """
    fd = _FileDialog(start_at=start_at, extensions=extensions, caption=caption)
    fd.set_file_mode(QFileDialog.ExistingFiles)
    return fd.show()
