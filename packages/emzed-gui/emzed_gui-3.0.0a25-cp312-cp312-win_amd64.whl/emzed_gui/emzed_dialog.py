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


import contextlib
import gc
import sys

import guidata
import pkg_resources
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import QDialog

_instances = set()
_killed = set()


class EmzedDialog(QDialog):
    def __init__(self, *a, **kw):
        super(EmzedDialog, self).__init__(*a, **kw)
        data = pkg_resources.resource_string("emzed_gui.resources", "icon64.png")
        img = QImage()
        img.loadFromData(data)
        pixmap = QPixmap.fromImage(img)
        self.setWindowIcon(QIcon(pixmap))

        # keep reference if used from cli like in spyder to keep dialog alive
        # and avoid garbage collection
        _instances.add(self)
        for inst in _killed.copy():
            if inst in _instances:
                _instances.remove(inst)
            _killed.remove(inst)

    def closeEvent(self, event):
        # we postpone killing to opening the next dialog as killing here crashes
        # the spyder kernel
        _killed.add(self)
        event.accept()

    def processEvents(self):
        guidata.qapplication().processEvents()

    def setWaitCursor(self):
        self.setCursor(Qt.WaitCursor)

    def setArrowCursor(self):
        self.setCursor(Qt.ArrowCursor)
