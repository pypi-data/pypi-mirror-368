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

from ._view_range_widget import Ui_ViewRangeWidget

MZ_ABS_FMT = "%.6f"
PPM_FMT = "%.1f"
RT_FMT = "%.2f"


def parse_float(q_text_edit):
    try:
        return float(q_text_edit.text())
    except ValueError:
        return None


class ViewRangeWidget(QtWidgets.QWidget, Ui_ViewRangeWidget):
    RANGE_CHANGED = QtCore.pyqtSignal(float, float, float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._setup()

    def set_view_range(self, rt_min, rt_max, mz_min, mz_max):
        rt_min, rt_max = sorted((rt_min, rt_max))
        mz_min, mz_max = sorted((mz_min, mz_max))
        self.blockSignals(True)
        self._set_rt(rt_min, rt_max)
        self._set_mz(mz_min, mz_max)
        center = (mz_min + mz_max) / 2
        width = (mz_max - mz_min) / 2
        self._set_mz_by_center(center, width)
        self.blockSignals(False)
        self.setEnabled(True)

    def _setup(self):
        self.setEnabled(False)
        self._use_ppm.setChecked(True)
        self._use_ppm.stateChanged.connect(self._use_ppm_changed)
        rt_range_fields = [self._rt_min, self._rt_max]
        mz_range_fields = [self._mz_min, self._mz_max]
        mz_range_by_center_fields = [self._mz_center, self._mz_width]

        for w in rt_range_fields + mz_range_fields + mz_range_by_center_fields:
            w.setValidator(QtGui.QDoubleValidator())

        for w in rt_range_fields:
            w.editingFinished.connect(self._rt_fields_update)

        for w in mz_range_fields:
            w.editingFinished.connect(self._mz_fields_update)

        for w in mz_range_by_center_fields:
            w.editingFinished.connect(self._mz_by_center_fields_update)

    def _mz_fields_update(self):
        mz_min = parse_float(self._mz_min)
        mz_max = parse_float(self._mz_max)
        center = (mz_min + mz_max) / 2
        width = (mz_max - mz_min) / 2
        self._set_mz_by_center(center, width)
        self._emit_range_update()

    def _emit_range_update(self):
        rt_min = parse_float(self._rt_min) * 60
        rt_max = parse_float(self._rt_max) * 60
        mz_min = parse_float(self._mz_min)
        mz_max = parse_float(self._mz_max)
        if all(v is not None for v in (rt_min, rt_max, mz_min, mz_max)):
            self.RANGE_CHANGED.emit(rt_min, rt_max, mz_min, mz_max)

    def _rt_fields_update(self):
        self._emit_range_update()

    def _mz_by_center_fields_update(self):
        center = parse_float(self._mz_center)
        width = parse_float(self._mz_width)
        if self._use_ppm.checkState():
            width = center * width * 1e-6
        mz_min = center - width
        mz_max = center + width
        self._set_mz(mz_min, mz_max)

    def _use_ppm_changed(self, new_check_state):
        width = parse_float(self._mz_width)
        center = parse_float(self._mz_center)
        if new_check_state:
            self._set_width_as_ppm(center, width)
        else:
            width = center * width * 1e-6
            self._set_width_abs(width)

    def _set_rt(self, rt_min, rt_max):
        self._rt_min.setText(RT_FMT % (rt_min / 60))
        self._rt_max.setText(RT_FMT % (rt_max / 60))
        self._emit_range_update()

    def _set_mz(self, mz_min, mz_max):
        self._mz_min.setText(MZ_ABS_FMT % mz_min)
        self._mz_max.setText(MZ_ABS_FMT % mz_max)
        self._emit_range_update()

    def _set_mz_by_center(self, center, width):
        if self._use_ppm.checkState():
            self._set_width_as_ppm(center, width)
        else:
            self._set_width_abs(width)
        self._mz_center.setText(MZ_ABS_FMT % center)

    def _set_width_as_ppm(self, center, width):
        width = width / center * 1e6
        self._mz_width.setText(PPM_FMT % width)

    def _set_width_abs(self, width):
        self._mz_width.setText(MZ_ABS_FMT % width)
