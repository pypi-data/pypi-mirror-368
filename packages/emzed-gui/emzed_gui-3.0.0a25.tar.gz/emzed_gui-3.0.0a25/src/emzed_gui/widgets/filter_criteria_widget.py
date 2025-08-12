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


import fnmatch

from emzed import MzType, RtType
from PyQt5 import QtCore, QtWidgets

from ._choose_range import Ui_ChooseRange
from ._choose_value import Ui_ChooseValue
from ._filter_criteria_widget import Ui_FilterCriteriaWidget
from ._string_filter import Ui_StringFilter


class FilterCriteriaWidget(QtWidgets.QWidget, Ui_FilterCriteriaWidget):
    LIMITS_CHANGED = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._choosers = []

    def setup(self):
        self.setEnabled(False)

    def _addChooser(self, chooser):
        self._hlayout.addWidget(chooser)
        self._hlayout.setAlignment(chooser, QtCore.Qt.AlignTop)
        chooser.INDICATE_CHANGE.connect(self.value_commited)
        self._choosers.append(chooser)

    def value_commited(self, name):
        expressions = []
        for chooser in self._choosers:
            expression = chooser.get_filter()
            if expression is not None:
                expressions.append(expression)
        self.LIMITS_CHANGED.emit(" AND ".join(expressions))

    def _setup_float_chooser(self, name, db_col_name, t):
        fmtter = t._model._col_formatters[name]
        try:
            txt = fmtter(0.0)
        except Exception:
            txt = ""
        if txt.endswith("m"):
            ch = ChooseTimeRange(name, db_col_name, t)
        else:
            ch = ChooseFloatRange(name, db_col_name, t)
        return ch

    def configure(self, emzed_table):
        t = emzed_table
        for fmt, name, type_ in zip(t.col_formats, t.col_names, t.col_types):
            db_col_name = t._model.col_name_mapping[name]
            if fmt is not None:
                ch = None
                if type_ in (float, MzType):
                    ch = ChooseFloatRange(name, db_col_name, t)
                if type_ is RtType:
                    ch = ChooseTimeRange(name, db_col_name, t)
                if type_ in (bool,):  # CheckState):
                    ch = ChooseValue(name, db_col_name, t, [True, False])
                elif type_ is int:
                    ch = ChooseIntRange(name, db_col_name, t)
                elif type_ is str:
                    ch = StringFilterPattern(name, db_col_name, t)
                if ch is not None:
                    self._addChooser(ch)
        self._hlayout.addStretch(1)
        if not len(self._choosers):
            self.filters_enabled = False
            self.setVisible(False)
            return
        self.setEnabled(True)

    def hide_filters(self, names):
        for c in self._choosers:
            c.setVisible(c.name not in names)

    def update(self, name):
        for chooser in self._choosers:
            if chooser.name == name:
                chooser.update()


class _ChooseNumberRange(QtWidgets.QWidget, Ui_ChooseRange):
    INDICATE_CHANGE = QtCore.pyqtSignal(str)

    def __init__(self, name, db_col_name, table, min_=None, max_=None, parent=None):
        super().__init__(parent)
        self.setupUi(parent)
        self.name = name
        self.db_col_name = db_col_name
        self.table = table
        self.column_name.setText(self.name)
        if min_ is not None:
            self.lower_bound.setText(min_)
        if max_ is not None:
            self.upper_bound.setText(max_)

    def setupUi(self, parent):
        super().setupUi(self)
        self.lower_bound.setMinimumWidth(40)
        self.upper_bound.setMinimumWidth(40)
        self.lower_bound.returnPressed.connect(self.return_pressed)
        self.upper_bound.returnPressed.connect(self.return_pressed)

    def return_pressed(self):
        self.INDICATE_CHANGE.emit(self.name)

    def update(self):
        pass

    def get_filter(self):
        v1 = str(self.lower_bound.text()).strip()
        v2 = str(self.upper_bound.text()).strip()
        try:
            v1 = self._convert(v1) if v1 else None
        except Exception:
            v1 = None
        try:
            v2 = self._convert(v2) if v2 else None
        except Exception:
            v2 = None
        return sql_range_filter(self.db_col_name, v1, v2)


def sql_range_filter(name, v1, v2):
    if v1 is not None and v2 is not None:
        return f"({v1} <= {name} AND {name} <= {v2})"
    elif v1 is not None:
        return f"({v1} <= {name})"
    elif v2 is not None:
        return f"({name} <= {v2})"
    else:
        return None


class ChooseFloatRange(_ChooseNumberRange):
    def _convert(self, txt):
        return float(txt)


class ChooseIntRange(_ChooseNumberRange):
    def _convert(self, txt):
        return int(txt)


class ChooseTimeRange(_ChooseNumberRange):
    def __init__(self, name, db_col_name, table, min_=None, max_=None, parent=None):
        super().__init__(name, db_col_name, table, min_, max_, parent)
        self.column_name.setText("%s [m]" % self.name)

    def _convert(self, txt):
        txt = txt.rstrip("m").rstrip()
        return 60.0 * float(txt) if txt else None


class ChooseValue(QtWidgets.QWidget, Ui_ChooseValue):
    INDICATE_CHANGE = QtCore.pyqtSignal(str)

    def __init__(self, name, db_col_name, table, choices, parent=None):
        super().__init__(parent)
        self.setupUi(parent)
        self.name = name
        self.db_col_name = db_col_name
        self.table = table
        self.choices = choices
        self.column_name.setText(self.name)
        self.update()

    def setupUi(self, parent):
        super().setupUi(self)
        self.values.currentIndexChanged.connect(self.choice_changed)

    def choice_changed(self, *a):
        self.INDICATE_CHANGE.emit(self.name)

    def get_filter(self):
        t = self.pure_values[self.values.currentIndex()]
        if t is None:
            return None
        if t == "-":
            t = None

        if t is None:
            return f"({self.name} IS NULL)"

        return f"({self.db_col_name} = {t})"

    def update(self):
        before = self.values.currentText()
        self.pure_values = [None] + self.choices
        new_items = [""] + list(map(str, self.choices))

        # block emiting signals, because the setup / update of the values below would
        # trigger emitting a curretnIndexChanged signal !
        old_state = self.values.blockSignals(True)

        self.values.clear()
        self.values.addItems(new_items)
        if before in new_items:
            self.values.setCurrentIndex(new_items.index(before))

        # unblock:
        self.values.blockSignals(old_state)


class StringFilterPattern(QtWidgets.QWidget, Ui_StringFilter):
    INDICATE_CHANGE = QtCore.pyqtSignal(str)

    def __init__(self, name, db_col_name, table, pattern=None, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.name = name
        self.db_col_name = db_col_name
        self.table = table
        self.column_name.setText(self.name)
        if pattern is not None:
            self.pattern.setText(pattern)

    def setupUi(self, parent):
        super().setupUi(self)
        self.pattern.setMinimumWidth(40)
        self.pattern.returnPressed.connect(self.return_pressed)

    def return_pressed(self):
        self.INDICATE_CHANGE.emit(self.name)

    def get_filter(self, *a):
        pattern = str(self.pattern.text())
        if pattern == "":
            return None

        if not any(c in pattern for c in "?*[]"):
            return f"({self.db_col_name} = '{pattern}')"

        regex = fnmatch.translate(pattern)
        return f"re_match('{regex}', {self.db_col_name})"

        # some optimzations for faster comparison functions !
        if "?" not in pattern:
            if "*" not in pattern:

                def _filter(v, pattern=pattern):
                    return v == pattern

                return self.name, _filter

            if pattern.endswith("*") and "*" not in pattern[:-1]:

                def _filter(v, prefix=pattern[:-1]):
                    return v.startswith(prefix)

                return self.name, _filter

            elif pattern.startswith("*") and "*" not in pattern[1:]:

                def _filter(v, postfix=pattern[1:]):
                    return v.endswith(postfix)

                return self.name, _filter

            elif (
                pattern.startswith("*")
                and pattern.endswith("*")
                and "*" not in pattern[1:-1]
            ):

                def _filter(v, stem=pattern[1:-1]):
                    return stem in v

                return self.name, _filter

        def _filter(v, pattern=pattern):
            return fnmatch(v, pattern)

        return self.name, _filter
