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


from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QDialog

from ._column_selection_dialog import Ui_ColumnMultiSelectDialog


class ColumnMultiSelectDialog(QDialog):
    def __init__(self, names, states, n_shown=20, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.ui = Ui_ColumnMultiSelectDialog()
        self.ui.setupUi(self)

        assert len(names) == len(states)
        self.setup(names, states, n_shown)
        self.column_settings = None

    def setup(self, names, states, n_shown):
        n = len(names)
        n_shown = min(n_shown, n)
        oversize = n > n_shown
        self.model = model = QtGui.QStandardItemModel(self)

        for name, state in zip(names, states):
            item = QtGui.QStandardItem(name)
            check = QtCore.Qt.Checked if state else QtCore.Qt.Unchecked
            item.setCheckState(check)
            item.setCheckable(True)
            model.appendRow(item)

        list_ = self.ui.column_names
        list_.setModel(model)

        if oversize:
            extra_w = list_.verticalScrollBar().sizeHint().width()
        else:
            extra_w = 0

        w_buttons = (
            self.ui.apply_button.sizeHint().width()
            + self.ui.cancel_button.sizeHint().width()
        )
        w_list = list_.sizeHintForColumn(0) + 2 * list_.frameWidth() + extra_w
        w = max(w_list, w_buttons)
        h = list_.sizeHintForRow(0) * n_shown + 2 * list_.frameWidth()
        list_.setFixedSize(w, h)

        self.setFixedSize(w, h + self.ui.apply_button.height())

        self.ui.apply_button.clicked.connect(self.apply_button_clicked)
        self.ui.cancel_button.clicked.connect(self.cancel_button_clicked)

    def cancel_button_clicked(self, __):
        self.done(1)

    def apply_button_clicked(self, __):
        self.column_settings = []
        for row_idx in range(self.model.rowCount()):
            item = self.model.item(row_idx, 0)
            self.column_settings.append(
                (str(item.text()), row_idx, item.checkState() == QtCore.Qt.Checked)
            )
        self.done(0)
