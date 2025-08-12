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


from PyQt5 import QtCore, QtWidgets

from ._integration_widget import Ui_IntegrationWidget


class IntegrationWidget(QtWidgets.QWidget, Ui_IntegrationWidget):
    TRIGGER_INTEGRATION = QtCore.pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        super().setupUi(self)
        self.setEnabled(False)
        self._compute_button.clicked.connect(self._button_pressed)
        self._compute_button.setEnabled(False)
        self._methods.activated.connect(self._item_activated)

    def set_integration_methods(self, names):
        self._methods.clear()
        self._methods.addItem("-")
        for name in names:
            self._methods.addItem(name)
        self.setEnabled(True)

    def set_integration_method(self, name, block_signals=True):
        if block_signals:
            self._methods.blockSignals(True)
        try:
            if name is None:
                name = "-"
            index = self._methods.findText(name)
            if index != -1:
                self._methods.setCurrentIndex(index)
        finally:
            if block_signals:
                self._methods.blockSignals(False)

        self._compute_button.setEnabled(True)

    def set_postfixes(self, postfixes):
        self._postfixes.clear()
        for postfix in postfixes:
            self._postfixes.addItem(postfix)

        self._postfixes.setEnabled(len(postfixes) > 1)

    def _item_activated(self, index):
        self._compute_button.setEnabled(self._methods.currentText() != "-")

    def _button_pressed(self):
        self.TRIGGER_INTEGRATION.emit(
            self._methods.currentText(), self._postfixes.currentText()
        )
