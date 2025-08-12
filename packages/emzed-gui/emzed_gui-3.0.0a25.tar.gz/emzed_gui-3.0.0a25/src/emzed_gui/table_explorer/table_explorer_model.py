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

import hashlib
import os
import re
import sys
import warnings
from datetime import datetime

import guidata
from emzed.config import folders
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from emzed_gui.configs import get_color
from emzed_gui.helpers import timethis

from .table_explorer_model_actions import *

ROWS_BATCH_SIZE = 100


def supported_postfixes(t, names):
    result = []
    if all(name in t.col_names for name in names):
        result.append("")

    postfixes = set(
        "__" + name.split("__", 1)[1] for name in t.col_names if "__" in name
    )
    for postfix in postfixes:
        if all(name + postfix in t.col_names for name in names):
            result.append(postfix)
    return result


def isUrl(what):
    what = str(what)
    return what.startswith("http://") or what.startswith("https://")


def parse_color(color):
    if isinstance(color, tuple):
        if len(color) not in (3, 4):
            return None
        if all(isinstance(ci, float) for ci in color):
            try:
                return QColor.fromRgbF(*color)
            except ValueError:
                return
        try:
            return QColor(*color)
        except ValueError:
            return

    if isinstance(color, str):
        if color.startswith("#"):
            return QColor(color)
    else:
        try:
            color_fields = tuple(map(int, color.split(",")))
            return QColor(*color_fields)
        except ValueError:
            return


class TableModel(QAbstractTableModel):
    LIGHT_BLUE = QColor(200, 200, 255)
    WHITE = QColor(255, 255, 255)

    VISIBLE_ROWS_CHANGE = pyqtSignal(int, int)
    SORT_TRIGGERED = pyqtSignal(str, bool)
    ACTION_LIST_CHANGED = pyqtSignal(object, object)

    def __init__(self, table, parent):
        super().__init__(parent)
        self.table = table
        self.parent = parent

        self._cache = {}
        self._color_cache = {}
        self._rows_loaded = 0

        nc = len(self.table.col_names)
        self.indizesOfVisibleCols = [
            j for j in range(nc) if self.table.col_formats[j] is not None
        ]
        self.widgetColToDataCol = dict(enumerate(self.indizesOfVisibleCols))
        nr = len(table)

        self.row_permutation = list(range(nr))
        self.visible_rows = set(range(nr))
        self.update_row_view()

        self.emptyActionStack()

        self._prefetch_rows()

        self.active_filter_expression = ""
        self.setFiltersEnabled(False)

        self.selected_data_rows = []
        self.counter_for_calls_to_sort = 0
        self.load_preset_hidden_column_names()
        self.has_color = "color" in table.col_names

        self.monospace = QFont("Inconsolata")

        if sys.platform == "darwin":
            self.monospace.setPointSize(14)

    def _prefetch_rows(self):
        imax = min(max(0, len(self.table) - 1), max(1000, ROWS_BATCH_SIZE))
        for index in range(imax):
            self._get_table_row(index)
        self.fetchMore(None)

    def set_row_permutation(self, permutation):
        self.row_permutation = list(permutation)

    def transform_table(self, function, parent):
        self.beginResetModel()
        try:
            function(self.table, parent=parent)
            if not isinstance(self, (TableModel)):
                raise ValueError(
                    "the callback %s did not return a valid emzed table." % function
                )
            self.table.resetInternals()
            self.update_row_view(reset=True)
        finally:
            self.endResetModel()

    def update_row_view(self, reset=False):
        """handles changes in permutation (sorting) and filtering of rows"""
        if reset:
            self.visible_rows = range(len(self.table))
        self.widgetRowToDataRow = [
            row_idx for row_idx in self.row_permutation if row_idx in self.visible_rows
        ]
        self.dataRowToWidgetRow = {
            row: i for (i, row) in enumerate(self.widgetRowToDataRow)
        }
        self.colors_selected_rows = {}

    def set_selected_widget_rows(self, widget_rows):
        self.selected_data_rows = self.transform_row_idx_widget_to_model(widget_rows)

    def setFiltersEnabled(self, flag):
        self.filters_enabled = flag
        self.update_visible_rows_for_given_limits()

    def emptyActionStack(self):
        self.actions = []
        self.redoActions = []

    def rowCount(self, index=QModelIndex()):
        if index.isValid():
            return 0
        return min(self._rows_loaded, len(self.visible_rows))

    def columnCount(self, index=QModelIndex()):
        return len(self.widgetColToDataCol)

    def column_name(self, index):
        if isinstance(index, int):
            col = self.widgetColToDataCol[index]
        else:
            __, col = self.table_index(index)
        return self.table.col_names[col]

    def column_type(self, index):
        if isinstance(index, int):
            col = self.widgetColToDataCol[index]
        else:
            __, col = self.table_index(index)
        return self.table.col_types[col]

    def table_index(self, index):
        cidx = self.widgetColToDataCol[index.column()]
        ridx = self.widgetRowToDataRow[index.row()]
        return ridx, cidx

    def _get_table_row(self, ridx):
        if ridx not in self._cache:
            self._cache[ridx] = self.table[ridx]
        return self._cache[ridx]

    def canFetchMore(self, index):
        if index.isValid():
            return False
        return self._rows_loaded < len(self.visible_rows)

    def fetchMore(self, parent):
        if parent is not None and parent.isValid():
            return

        remainder = len(self.visible_rows) - self._rows_loaded
        to_fetch = min(ROWS_BATCH_SIZE, remainder)
        if to_fetch <= 0:
            return

        self.beginInsertRows(
            QModelIndex(), self._rows_loaded, self._rows_loaded + to_fetch - 1
        )

        self._rows_loaded += to_fetch

        self.endInsertRows()

    def cell_value(self, index):
        ridx, cidx = self.table_index(index)

        try:
            row = self._get_table_row(ridx)
        except IndexError:
            raise IndexError(
                "invalid access of row %d of table of length %d"
                % (ridx, len(self.table))
            )
        try:
            # rows hold _index column
            value = row[cidx + 1]
        except IndexError:
            raise IndexError(
                "invalid access of column %d of row of length %d" % (ridx, len(row))
            )

        return value

    def row(self, index):
        ridx, cidx = self.table_index(index)
        return self._get_table_row(ridx)

    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def font(self, index):
        font = self.monospace
        content = self.data(index, Qt.DisplayRole)
        font.setUnderline(isUrl(content))
        return font

    def check_state_data(self, index, role):
        if role == Qt.CheckStateRole:
            value = self.cell_value(index)
            if value is None:
                return "-"  # QVariant()
            return Qt.Checked if value else Qt.Unchecked
        elif role == Qt.DisplayRole:
            return ""
        return QVariant()

    def get_color(self, index):
        ridx, cidx = self.table_index(index)
        if (ridx, cidx) in self._color_cache:
            return self._color_cache[ridx, cidx]
        try:
            row = self._get_table_row(ridx)
        except IndexError:
            raise IndexError(
                "invalid access of row %d of table of length %d"
                % (ridx, len(self.table))
            )
        # fill cache for given row
        color = row["color"]
        if color is None:
            for cidx_ in range(len(row)):
                self._color_cache[ridx, cidx_] = None
        elif isinstance(color, str):
            for cidx_ in range(len(row)):
                self._color_cache[ridx, cidx_] = parse_color(color)
        elif isinstance(color, dict):
            for cidx_ in range(len(row)):
                name = self.table.col_names[cidx_]
                column_color = color.get(name)
                if column_color is not None:
                    self._color_cache[ridx, cidx_] = parse_color(column_color)
                else:
                    self._color_cache[ridx, cidx_] = None
        else:
            return

        return self._color_cache[ridx, cidx]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        if role == Qt.FontRole:
            return self.font(index)

        elif role == Qt.BackgroundRole and self.has_color:
            color = self.get_color(index)
            if color is not None:
                return QBrush(color)
            return QVariant()

        elif role != Qt.DisplayRole:
            return QVariant()

        value = self.cell_value(index)

        ridx, cidx = self.table_index(index)
        fmter = self.table._model._col_formatters[self.table.col_names[cidx]]

        if isinstance(value, datetime):
            fmt = self.table.col_formats[cidx]
            if fmt in ("%r", "%s"):
                shown = value.strftime(self.DATE_FORMAT)
            else:
                try:
                    shown = fmter(value)
                except Exception:
                    shown = value.strftime(self.DATE_FORMAT)
        else:
            shown = fmter(value) + " "
        return shown

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Vertical:
            if role == Qt.ForegroundRole:
                color = self.colors_selected_rows.get(section)
                if color is not None:
                    return QBrush(QColor(color))
            if role == Qt.DisplayRole:
                if section in self.colors_selected_rows:
                    return chr(0x2588) * 2
                return "  "

        elif orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                dataIdx = self.widgetColToDataCol[section]
                return str(self.table.col_names[dataIdx])

    def set_row_header_colors(self, widget_row_indices, color_row_headers):
        self.colors_selected_rows = {}
        if not widget_row_indices:
            return
        for i, widget_row_idx in enumerate(widget_row_indices):
            self.colors_selected_rows[widget_row_idx] = (
                get_color(i) if color_row_headers else "#909090"
            )
        self.headerDataChanged.emit(Qt.Vertical, 0, self.rowCount())

    def runAction(self, clz, *a):
        action = clz(self, *a)
        self.clear_cache()
        changed_data = action.do()
        if not changed_data:
            return changed_data
        self.actions.append(action)
        self.redoActions = []
        self.emit_updated_actions()
        return changed_data

    def clear_cache(self):
        self._cache.clear()
        self._color_cache.clear()

    def emit_updated_actions(self):
        last_action = str(self.actions[-1]) if self.actions else None
        last_redo_action = str(self.redoActions[-1]) if self.redoActions else None
        self.ACTION_LIST_CHANGED.emit(last_action, last_redo_action)

    def infoLastAction(self):
        if len(self.actions):
            return str(self.actions[-1])
        return None

    def infoRedoAction(self):
        if len(self.redoActions):
            return str(self.redoActions[-1])
        return None

    def undoLastAction(self):
        if not len(self.actions):
            return
        action = self.actions.pop()
        self.beginResetModel()
        changed_data = action.undo()
        if changed_data:
            self.clear_cache()
        self.update_visible_rows_for_given_limits(force_reset=True)
        self.redoActions.append(action)
        self.endResetModel()
        self.emit_updated_actions()

    def redoLastAction(self):
        if not len(self.redoActions):
            return
        action = self.redoActions.pop()
        self.beginResetModel()
        changed_data = action.do()
        if changed_data:
            self.clear_cache()
        self.update_visible_rows_for_given_limits(
            force_reset=True
        )  # does endResetModel
        self.actions.append(action)
        self.endResetModel()
        self.emit_updated_actions()

    def sort(self, colIdx, order=Qt.AscendingOrder):
        # this function is called the first time when the view calls setSortingEnabled,
        # but with descending order. We suppress this here and trigger ordering
        # seperately.

        if not len(self.widgetColToDataCol):
            return

        self.counter_for_calls_to_sort += 1
        if self.counter_for_calls_to_sort == 1:
            return

        dataColIdx = self.widgetColToDataCol[colIdx]
        name = self.table.col_names[dataColIdx]
        self.sort_by([(name, "asc" if order == Qt.AscendingOrder else "desc")])
        self.SORT_TRIGGERED.emit(name, order == Qt.AscendingOrder)

    def widget_col(self, col_name):
        data_col_idx = self.table.col_names.index(col_name)
        for widget_col, data_col in list(self.widgetColToDataCol.items()):
            if data_col == data_col_idx:
                return widget_col

    def sort_by(self, sort_data):
        data_cols = [(name, order.startswith("asc")) for (name, order) in sort_data]
        self.beginResetModel()
        self.runAction(SortTableAction, data_cols)
        self.update_row_view()
        self.endResetModel()

    def eic_col_names(self):
        return ["peakmap", "mzmin", "mzmax", "rtmin", "rtmax"]

    def chromatogram_col_names(self):
        return ["chromatogram"]

    def get_eic_postfixes(self):
        return supported_postfixes(self.table, self.eic_col_names())

    def get_chromatogram_postfixes(self):
        return supported_postfixes(self.table, self.chromatogram_col_names())

    def has_peaks(self):
        return self.check_for_any(self.eic_col_names())

    def has_chromatograms(self):
        return self.check_for_any(self.chromatogram_integration_col_names())

    def hasSpectra(self):
        return any(n.startswith("spectra") for n in self.table.col_names)

    def integration_col_names(self):
        return ["area", "rmse", "peak_shape_model", "model", "valid_model"]

    def chromatogram_integration_col_names(self):
        return [n + "_chromatogram" for n in self.integration_col_names()]

    def getIntegrationValues(self, data_row_idx, p):
        def get(nn):
            row = self._get_table_row(data_row_idx)
            return row[nn + p]

        return dict((nn + p, get(nn)) for nn in self.integration_col_names())

    def has_peakshape_model(self):
        return (
            self.check_for_any(self.eic_col_names())
            and self.check_for_any(self.integration_col_names())
        ) or (
            self.check_for_any(self.chromatogram_integration_col_names())
            and self.check_for_any(self.chromatogram_integration_col_names())
        )

    def check_for_any(self, names):
        """
        checks if names appear at least once as prefixes in current colNames
        """
        return len(supported_postfixes(self.table, names)) > 0

    def getTitle(self):
        table = self.table
        if table.title:
            title = table.title
        else:
            title = os.path.basename(table.meta_data.get("source", ""))
        return title

    def getShownColumnName(self, col_idx):
        """lookup name of visible column #col_idx"""
        data_col_idx = self.widgetColToDataCol[col_idx]
        return self.table.col_names[data_col_idx]

    def lookup(self, look_for, col_name):
        look_for = str(look_for).strip()
        formatter = self.table.col_formatters[col_name]
        for row, value in enumerate(getattr(self.table, col_name)):
            if formatter(value).strip() == look_for:
                return row
        return None

    def getPeakmaps(self, data_row_idx):
        peakMaps = []
        for postfix in supported_postfixes(self.table, ["peakmap"]):
            pm = self._get_table_row(data_row_idx)["peakmap" + postfix]
            peakMaps.append(pm)
        return peakMaps

    def _get_models(self, data_row_idx, postfixes, model_col):
        row = self._get_table_row(data_row_idx)
        for postfix in supported_postfixes(self.table, [model_col]):
            if postfixes is not None and postfix not in postfixes:
                continue
            model = row[model_col + postfix]
            yield model

    def get_peak_shape_models(self, data_row_idx, postfixes=None):
        yield from self._get_models(data_row_idx, postfixes, "model")

    def get_chromatogram_models(self, data_row_idx, postfixes=None):
        yield from self._get_models(data_row_idx, postfixes, "model_chromatogram")

    def get_plotting_data(self, data_row_idx, postfixes=None):
        row = self._get_table_row(data_row_idx)
        names = self.eic_col_names()
        for postfix in supported_postfixes(self.table, names):
            if postfixes is not None and postfix not in postfixes:
                continue
            peakmap, mzmin, mzmax, rtmin, rtmax = (row[key + postfix] for key in names)
            peak_id = row.get("id" + postfix, "")
            if all(
                (
                    rtmin is not None,
                    rtmax is not None,
                    mzmin is not None,
                    mzmax is not None,
                    peakmap is not None,
                )
            ):
                yield postfix, peak_id, rtmin, rtmax, mzmin, mzmax, peakmap

    def get_chromatograms(self, data_row_idx, postfixes=None):
        row = self._get_table_row(data_row_idx)
        names = self.chromatogram_col_names()
        for postfix in supported_postfixes(self.table, names):
            if postfixes is not None and postfix not in postfixes:
                continue
            chromatogram, *_ = (row[key + postfix] for key in names)
            if chromatogram is None:
                continue

            rtmin = chromatogram.rts.min()
            rtmax = chromatogram.rts.max()
            peak_id = row.get("id" + postfix, "")
            if all(
                (
                    rtmin is not None,
                    rtmax is not None,
                    chromatogram is not None,
                )
            ):
                yield postfix, peak_id, rtmin, rtmax, chromatogram

    def get_ms2_spectra(self, data_row_idx):
        spectra = []
        postfixes = []
        for p in supported_postfixes(self.table, ("spectra_ms2",)):
            row = self._get_table_row(data_row_idx)
            specs = row["spectra_ms2" + p]
            spectra.append(specs)
            postfixes.append(p)
        return postfixes, spectra

    def numbersOfEicsPerRow(self):
        return len(supported_postfixes(self.table, self.eic_col_names()))

    def __len__(self):
        return len(self.widgetRowToDataRow)

    def computeEics(self, data_row_idx):
        eics = []
        mzmins = []
        mzmaxs = []
        rtmins = []
        rtmaxs = []
        allrts = []
        row = self._get_table_row(data_row_idx)
        for p in supported_postfixes(self.table, self.eic_col_names()):
            # values = self.table.getValues(self.table.rows[data_row_idx])
            pm = row["peakmap" + p]
            mzmin = row["mzmin" + p]
            mzmax = row["mzmax" + p]
            rtmin = row["rtmin" + p]
            rtmax = row["rtmax" + p]
            if (
                mzmin is None
                or mzmax is None
                or rtmin is None
                or rtmax is None
                or pm is None
            ):
                chromo = [], []
            else:
                chromo = pm.chromatogram(mzmin, mzmax, rtmin, rtmax)
                mzmins.append(mzmin)
                mzmaxs.append(mzmax)
                rtmins.append(rtmin)
                rtmaxs.append(rtmax)
            eics.append(chromo)
            allrts.extend(chromo[0])
        if not mzmins:
            return eics, 0, 0, 0, 0, sorted(allrts)
        return eics, min(rtmins), max(rtmaxs), sorted(allrts)

    def rows_with_same_values(self, col_name, widget_row_indices):
        # we are using a dict instead a set to keep the order
        # (dicts are ordered in Python, but sets not)
        result = dict()
        for widget_row_idx in widget_row_indices:
            # we avoid duplicate lookups for multi select:
            if widget_row_idx not in result:
                result.update(self.rows_with_same_value(col_name, widget_row_idx))
        return list(result.keys())

    def rows_with_same_value(self, col_name, widget_row_idx):
        data_row_idx = self.widgetRowToDataRow[widget_row_idx]

        selected_value = self._get_table_row(data_row_idx)[col_name]

        selected_data_rows = timethis(self.table._find_matching_rows)(
            col_name, selected_value
        )
        selected_data_rows = [r for r in selected_data_rows if r in self.visible_rows]
        # we are using a dict instead a set to keep the order
        # (dicts are ordered in Python, but sets not)
        return {self.dataRowToWidgetRow[i]: 1 for i in selected_data_rows}

    def transform_row_idx_widget_to_model(self, row_idxs):
        return [self.widgetRowToDataRow[i] for i in row_idxs]

    def getEics(self, data_row_idx):
        eics = []
        rtmins = []
        rtmaxs = []
        allrts = []
        row = self._get_table_row(data_row_idx)
        for p in supported_postfixes(self.table, ["eic"]):
            rtmin = row.get("rtmin" + p)  # might be missing in table
            rtmax = row.get("rtmax" + p)  # might be missing in table
            eic = row["eic" + p]  # must be there !
            if eic is not None:
                eics.append(eic)
                rts, iis = eic
                if rtmin is not None:
                    rtmins.append(rtmin)
                else:
                    rtmins.append(min(rts))
                if rtmax is not None:
                    rtmaxs.append(rtmax)
                else:
                    rtmaxs.append(max(rts))
                allrts.extend(rts)
        return (
            eics,
            min(rtmins) if rtmins else None,
            max(rtmaxs) if rtmaxs else None,
            sorted(allrts),
        )

    def remove_filtered(self):
        to_delete = list(range(len(self.widgetRowToDataRow)))
        self.remove_rows(to_delete)

    def limits_changed(self, filter_expression):
        self.active_filter_expression = filter_expression
        self.update_visible_rows_for_given_limits()

    @profile
    def update_visible_rows_for_given_limits(self, force_reset=False):
        if self.filters_enabled is False:
            filter_expression = None
        else:
            if not self.active_filter_expression:
                filter_expression = None
            else:
                filter_expression = self.active_filter_expression

        if filter_expression:
            try:
                visible_rows = self.table._indices_for_rows_matching(filter_expression)
            except Exception:
                visible_rows = range(len(self.table))
        else:
            visible_rows = range(len(self.table))

        if not isinstance(visible_rows, (set, range)):
            warnings.warn(
                "visible rows is not of type set or range, this might"
                " sacrifice performance of table explorer."
            )

        if force_reset or visible_rows != self.visible_rows:
            self.beginResetModel()
            self.visible_rows = visible_rows
            self._rows_loaded = 0
            self.update_row_view()
            self.endResetModel()
            self.emit_visible_rows_change()

    def emit_visible_rows_change(self):
        n_visible = len(self.widgetRowToDataRow)
        self.VISIBLE_ROWS_CHANGE.emit(len(self.table), n_visible)

    def save_table(self, path):
        ext = os.path.splitext(path)[1]
        if ext == ".csv":
            self.table[self.widgetRowToDataRow].save_csv(
                path, as_printed=True, overwrite=True
            )
        elif ext in (".xls", ".xlsx"):
            self.table[self.widgetRowToDataRow].save_excel(path, overwrite=True)
        elif ext == ".table":
            self.table[self.widgetRowToDataRow].save(path, overwrite=True)
        else:
            raise RuntimeError("extension of type %s can not be handled" % ext)

    def columnames_with_visibility(self):
        avail = self.indizesOfVisibleCols
        names = [self.table.col_names[i] for i in avail]
        visible = [i in list(self.widgetColToDataCol.values()) for i in avail]
        return names, visible

    def visible_column_names(self):
        avail = self.indizesOfVisibleCols
        names = [self.table.col_names[i] for i in avail]
        return names

    def _set_visible_cols(self, col_indices):
        self.beginResetModel()
        self.widgetColToDataCol = dict(enumerate(col_indices))
        self.endResetModel()

    def _settings_path(self):
        folder = os.path.join(folders.get_emzed_folder(), "table_explorer")
        if not os.path.exists(folder):
            os.makedirs(folder)
        digest = hashlib.md5()
        for name in self.table.col_names:
            digest.update(name.encode("utf-8"))
        file_name = "table_view_setting_%s.txt" % digest.hexdigest()
        path = os.path.join(folder, file_name)
        return path

    def save_preset_hidden_column_names(self):
        path = self._settings_path()
        names = self.table.col_names
        try:
            with open(path, "w") as fp:
                for i, j in list(self.widgetColToDataCol.items()):
                    print(i, names[j], file=fp)
        except IOError as e:
            print(e)

    def load_preset_hidden_column_names(self):
        path = self._settings_path()
        if os.path.exists(path):
            shown = set()
            dd = {}
            names = self.table.col_names
            try:
                with open(path, "r") as fp:
                    for line in fp:
                        i, name = line.strip().split(" ", 1)
                        if name in names:
                            dd[int(i)] = names.index(name)
                            shown.add(name)
                self.beginResetModel()
                self.widgetColToDataCol = dd
                self.endResetModel()
            except (IOError, ValueError) as e:
                print(e)
            return shown

    def hide_columns(self, names_to_hide):
        names = self.table.col_names
        col_indices = []
        for ix in self.indizesOfVisibleCols:
            name = names[ix]
            if name not in names_to_hide:
                col_indices.append(ix)
        self._set_visible_cols(col_indices)

    def implements(self, method_name):
        return hasattr(self, method_name)

    @staticmethod
    def table_model_for(table, parent=None):
        if table.is_mutable():
            return MutableTableModel(table, parent)
        else:
            return TableModel(table, parent)


class MutableTableModel(TableModel):
    def __init__(self, table, parent):
        super(MutableTableModel, self).__init__(table, parent)
        self.nonEditables = set()

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.EditRole:
            shown = super(MutableTableModel, self).data(index, Qt.DisplayRole)
            return str(shown)
        else:
            return super(MutableTableModel, self).data(index, role)

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        default = super().flags(index)
        # urls are not editable
        if isUrl(self.data(index)):
            return default
        if self.widgetColToDataCol[index.column()] in self.nonEditables:
            return default
        # TODO
        if self.column_type(index) is bool:
            return Qt.ItemFlags(default)  #  | Qt.ItemIsUserCheckable)

        if 0 and self.column_type(index) is CheckState:
            value = self.cell_value(index)
            if value is None:
                return Qt.ItemFlags(default)
            else:
                return Qt.ItemFlags(
                    default | Qt.ItemIsEditable | Qt.ItemIsUserCheckable
                )
        else:
            return Qt.ItemFlags(default | Qt.ItemIsEditable)

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        if not (0 <= index.row() < self.rowCount()):
            return False

        ridx, cidx = self.table_index(index)
        expectedType = self.table.col_types[cidx]
        if value.strip() == "-":
            value = None
        # TODO
        elif 0 and expectedType is CheckState:
            value = value == Qt.Checked
        elif expectedType != object:
            value = value.strip()
            # floating point number + "m" for minutes:
            if re.match(r"^((\d+[ ]*m)|(\d*.\d*[ ]*m))$", value):
                try:
                    value = 60.0 * float(value[:-1])
                except Exception:
                    guidata.qapplication().beep()
                    return False
            if expectedType == datetime:
                try:
                    value = datetime.strptime(value, self.DATE_FORMAT)
                except Exception:
                    guidata.qapplication().beep()
                    return False
            elif expectedType == bool:
                if value.lower() in ("true", "false", "t", "f"):
                    value = value.lower() in ("true", "t")
                else:
                    guidata.qapplication().beep()
                    return False
            else:
                try:
                    value = expectedType(value)
                except Exception:
                    guidata.qapplication().beep()
                    return False

        self.runAction(ChangeValueAction, index, ridx, cidx, value)
        return True

    def addNonEditable(self, idx):
        self.nonEditables.add(idx)

    def clone_row(self, widget_row_idx):
        data_row_idx = self.widgetRowToDataRow[widget_row_idx]
        self.beginInsertRows(QModelIndex(), widget_row_idx, widget_row_idx)
        self.runAction(CloneRowAction, widget_row_idx, data_row_idx)
        self.endInsertRows()
        self.update_visible_rows_for_given_limits()  # does endResetModel
        return True

    def remove_rows(self, widget_row_indices):
        data_row_indices = self.transform_row_idx_widget_to_model(widget_row_indices)
        mini = min(widget_row_indices)
        maxi = max(widget_row_indices)
        self.beginRemoveRows(QModelIndex(), mini, maxi)
        self.runAction(DeleteRowsAction, data_row_indices)
        self.endRemoveRows()
        self.update_visible_rows_for_given_limits()  # does endResetModel
        return True

    def restrict_to_visible_rows(self):
        shown_data_rows = self.widgetRowToDataRow
        delete_data_rows = set(range(len(self.table))) - set(shown_data_rows)
        self.beginResetModel()
        self.runAction(DeleteRowsAction, delete_data_rows)
        self.endResetModel()
        self.update_visible_rows_for_given_limits()  # does endResetModel
        return True

    def set_all(self, widget_col_index, value):
        data_col_index = self.widgetColToDataCol[widget_col_index]
        data_row_indices = self.widgetRowToDataRow
        self.beginResetModel()
        done = self.runAction(
            ChangeAllValuesInColumnAction,
            widget_col_index,
            data_row_indices,
            data_col_index,
            value,
        )
        if done:
            self.update_visible_rows_for_given_limits()
        self.beginResetModel()
        return done

    def integrate(self, label, method, rtmin, rtmax):
        data, *rest = label.split("_", 1)
        postfix = "_" + rest[0] if rest else ""

        action_class = (
            IntegrateAction if data == "peakmap" else ChromatogramIntegrateAction
        )

        widget_row_indices = [
            self.dataRowToWidgetRow[data_row_index]
            for data_row_index in self.selected_data_rows
        ]
        if widget_row_indices:
            self.runAction(
                action_class,
                self.selected_data_rows,
                postfix,
                method,
                rtmin,
                rtmax,
                widget_row_indices,
            )

            self.clear_cache()

    def setNonEditable(self, colBaseName, group):
        for postfix in supported_postfixes(self.table, group):
            if colBaseName + postfix in self.table.col_names:
                self.addNonEditable(colBaseName + postfix)
