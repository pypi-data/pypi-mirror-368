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


from PyQt5 import QtCore, QtGui, QtWidgets

from ._spectra_selector_widget import Ui_SpectraSelectorWidget


class SpectraSelectorWidget(QtWidgets.QWidget, Ui_SpectraSelectorWidget):
    MS_LEVEL_CHOSEN = QtCore.pyqtSignal(int, int)
    PRECURSOR_RANGE_CHANGED = QtCore.pyqtSignal(float, float)
    SELECTION_CHANGED = QtCore.pyqtSignal(int, float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._setup()
        self.setEnabled(False)

    def _setup(self):
        self._ms_level.activated.connect(self._ms_level_chosen)
        self._precursor.activated.connect(self._precursor_chosen)
        self._precursor_min.editingFinished.connect(self._precursor_range_updated)
        self._precursor_max.editingFinished.connect(self._precursor_range_updated)
        self._precursor_min.setValidator(QtGui.QDoubleValidator())
        self._precursor_max.setValidator(QtGui.QDoubleValidator())

    def set_data(self, ms_levels, precursor_mz_values):
        self._ms_level.clear()
        for ms_level in ms_levels:
            self._ms_level.addItem(str(ms_level))

        self._precursor.clear()
        self._precursor.addItem("-use range-")
        for precursor_mz_value in precursor_mz_values:
            self._precursor.addItem("%.5f" % precursor_mz_value)
        self.setEnabled(True)

        self._ms_levels = ms_levels
        self._precursor_mz_values = precursor_mz_values
        self._current_ms_level = None
        self._mz_range = None
        self._set_dependend_fields()

    def _ms_level_chosen(self, idx):
        chosen_ms_level = self._ms_levels[idx]
        self.MS_LEVEL_CHOSEN.emit(self._current_ms_level, chosen_ms_level)
        self._current_ms_level = chosen_ms_level
        self._set_dependend_fields()
        if self._mz_range is not None:
            self.SELECTION_CHANGED.emit(self._current_ms_level, *self._mz_range)

    def _precursor_chosen(self, idx):
        if not self._precursor_mz_values:
            return
        if idx == 0:
            mz_min = min(self._precursor_mz_values)
            mz_max = max(self._precursor_mz_values)
        else:
            precursor_mz = self._precursor_mz_values[idx - 1]
            mz_min = precursor_mz - 0.01
            mz_max = precursor_mz + 0.01
        self.PRECURSOR_RANGE_CHANGED.emit(mz_min, mz_max)
        self._precursor_min.setText("%.5f" % mz_min)
        self._precursor_max.setText("%.5f" % mz_max)
        self._mz_range = (mz_min, mz_max)
        if self._current_ms_level is not None:
            self.SELECTION_CHANGED.emit(self._current_ms_level, mz_min, mz_max)

    def _precursor_range_updated(self):
        try:
            mz_min = float(self._precursor_min.text())
            mz_max = float(self._precursor_max.text())
        except ValueError:
            return
        self.PRECURSOR_RANGE_CHANGED.emit(mz_min, mz_max)
        self._mz_range = (mz_min, mz_max)
        if self._current_ms_level is not None:
            self.SELECTION_CHANGED.emit(self._current_ms_level, mz_min, mz_max)

    def _set_dependend_fields(self):
        not_ms_1 = self._current_ms_level is not None and self._current_ms_level > 1
        self._precursor.setEnabled(not_ms_1)
        self._precursor_min.setEnabled(not_ms_1)
        self._precursor_max.setEnabled(not_ms_1)
