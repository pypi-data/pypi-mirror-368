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

import sys

import guidata
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTableView

from emzed_gui.helpers import protect_signal_handler


class EmzedTableView(QTableView):
    def __init__(self, dialog):
        super(EmzedTableView, self).__init__()
        self.dialog = dialog
        self.last_released_key = None
        if sys.platform == "darwin":
            self.monospace = QFont("Inconsolata")
            self.monospace.setPointSize(14)
            self.setFont(self.monospace)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)

    @protect_signal_handler
    def showEvent(self, evt):
        # me must load some data, else resizeColumnsToContents will only consider
        # header fields:
        self.model().fetchMore(None)

        self.resize_columns()

        if not self.isSortingEnabled():
            self.setSortingEnabled(True)
            self.sortByColumn(0, Qt.AscendingOrder)
            self.model().emptyActionStack()
            self.dialog.updateMenubar(None, None)

    def resize_columns(self):
        self.resizeColumnsToContents()

        # fix large columns
        screen_width = guidata.qapplication().screens()[0].size().width()
        # 200 pixels looks reasonable on a 1680 pixel wide display:
        max_width_in_pixel = 200 * 1680 // screen_width
        min_width_in_pixel = 55 * 1680 // screen_width

        # adjust sizes:
        for i in range(self.horizontalHeader().count()):
            size = self.columnWidth(i)
            if size > max_width_in_pixel:
                self.setColumnWidth(i, max_width_in_pixel)
            elif size < min_width_in_pixel:
                self.setColumnWidth(i, min_width_in_pixel)
            else:
                self.setColumnWidth(i, size + 5)

    @protect_signal_handler
    def keyPressEvent(self, evt):
        if evt.key() == Qt.Key_Backspace:
            selected = [
                idx.row()
                for idx in self.dialog.tableView.selectionModel().selectedRows()
            ]
            if selected:
                self.dialog.model.remove_rows(selected)

        if evt.key() not in (Qt.Key_Up, Qt.Key_Down):
            return super().keyPressEvent(evt)

        # extends selection to full row(s)
        rows = set(idx.row() for idx in self.selectedIndexes())
        if not rows:
            return super(EmzedTableView, self).keyPressEvent(evt)

        min_row = min(rows)
        max_row = max(rows)
        if evt.key() == Qt.Key_Up:
            row = min_row - 1
        else:
            row = max_row + 1
        row = min(max(row, 0), self.model().rowCount() - 1)
        ix = self.model().index(row, 0)
        self.setCurrentIndex(ix)
        self.selectRow(row)

        # we don't call super here to supress further cursor key handling
        return

    @protect_signal_handler
    def keyReleaseEvent(self, evt):
        # 1. single cursor key release triggers plot
        # 2. single cursor key release with shift key pressed is ignored
        # 3. releasing shift always triggers update

        if evt.key() not in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Shift):
            return

        # ingnore release cursors + shift
        if evt.key() in (Qt.Key_Up, Qt.Key_Down):
            self.last_released_key = evt.key()
            if evt.modifiers() & Qt.ShiftModifier:
                return

        if evt.key() == Qt.Key_Shift and self.last_released_key == Qt.Key_Shift:
            return

        self.last_released_key = evt.key()

        # fire events for updating plots
        rows = set(idx.row() for idx in self.selectedIndexes())
        if not rows:
            return super(EmzedTableView, self).keyReleaseEvent(evt)

        # it suffices to fire the event once as the handler determines
        # the plotted rows from the selected indexes
        row = next(iter(rows))
        self.verticalHeader().sectionClicked.emit(row)
