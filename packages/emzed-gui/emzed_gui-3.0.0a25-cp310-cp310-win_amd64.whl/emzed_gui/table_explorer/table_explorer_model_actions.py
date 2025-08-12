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

from functools import partial

from emzed.quantification.peak_integration import available_peak_shape_models
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class TableAction(object):
    actionName = None

    def __init__(self, model, **kw):
        self.model = model
        self.args = kw
        self.memory = None
        self.__dict__.update(kw)

    def undo(self):
        pass

    def beginDelete(self, idx, idx2=None):
        if idx2 is None:
            idx2 = idx
        self.model.beginRemoveRows(QModelIndex(), idx, idx2)

    def endDelete(self):
        self.model.endRemoveRows()

    def beginInsert(self, idx, idx2=None):
        if idx2 is None:
            idx2 = idx
        self.model.beginInsertRows(QModelIndex(), idx, idx2)

    def endInsert(self):
        self.model.endInsertRows()

    def __str__(self):
        args = ", ".join("%s: %s" % it for it in list(self.toview.items()))
        return "%s(%s)" % (self.actionName, args)


class DeleteRowsAction(TableAction):
    actionName = "delete row"

    def __init__(self, model, data_row_indices):
        super(DeleteRowsAction, self).__init__(model, data_row_indices=data_row_indices)
        self.toview = dict(rows=data_row_indices)

    def do(self):
        rows_to_del = sorted(self.data_row_indices)
        table = self.model.table
        permutation = self.model.row_permutation

        # Transform permutation such that rows are removed but remaining rows
        # have same sorting order:
        # Asssume the permutation is [2, 1, 3, 5, 4, 0] and we delete rows 0 and 1 from
        # the table, this leads to [2, 3, 5, 4] which has gaps. Below we fill the gaps
        # which results in [0, 1, 3, 2]

        # basic idea: we sort permutation and replace entries by increased values
        # 0, 1, ... problem: we must restore the original order afterwards.

        # start with permutation = [2, 1, 3, 5, 4, 0]

        perm_to_order = dict((p, i) for i, p in enumerate(permutation))

        # perm_to_order is now {2: 0, 1: 1, 3: 2, 5: 3, 4: 4, 0: 5}

        for p in rows_to_del:
            del perm_to_order[p]

        # perm_to_order is now {2: 0, 3: 2, 5: 3, 4: 4}

        # 1. sort by permutations, this create sorted entries with possible gaps:
        sorted_perm_to_order = sorted(perm_to_order.items())

        # sorted_perm_to_order is [(2, 0), (3, 2), (4, 4), (5, 3)]

        # permutation is sorted with gaps, we close gaps by replacing permutation by
        # enumerated sequence 0, 1, ... but keep the original row indices:
        perms_without_gaps_to_order = [
            (i, row_idx) for (i, (p_old, row_idx)) in enumerate(sorted_perm_to_order)
        ]

        # perms_without_gaps_to_order is now [(0, 0), (1, 2), (2, 4), (3, 3)]

        # we sort back by original order
        perms_without_gaps_to_order.sort(key=lambda item: item[1])

        # perms_without_gaps_to_order is now [(0, 0), (1, 2), (3, 3), (2, 4)]

        # extract permutation values and memoryze old polsitions for undo
        new_permutation, old_positions = zip(*perms_without_gaps_to_order)

        # new permutation is now [0, 1, 3, 2]

        # we must consolidate, as we delete rows below which makes view invalid:
        self.memory = (new_permutation, old_positions, table[rows_to_del].consolidate())

        del table[rows_to_del]
        self.model.set_row_permutation(new_permutation)

        return True

    def undo(self):
        super(DeleteRowsAction, self).undo()
        self.model.beginResetModel()
        table = self.model.table
        permutation, old_positions, saved_rows = self.memory

        n_before = len(table)

        table = table.merge(saved_rows)

        new_permutation = [None] * len(table)

        for position, pi in zip(old_positions, permutation):
            new_permutation[position] = pi

        j = 0
        for i, pi in enumerate(new_permutation):
            if pi is None:
                new_permutation[i] = n_before + j
                j += 1

        self.model.table = table
        self.model.set_row_permutation(new_permutation)
        self.model.endResetModel()
        return True


class CloneRowAction(TableAction):
    actionName = "clone row"

    def __init__(self, model, widget_row_idx, data_row_idx):
        super(CloneRowAction, self).__init__(
            model, widget_row_idx=widget_row_idx, data_row_idx=data_row_idx
        )
        self.toview = dict(row=widget_row_idx)

    def do(self):
        table = self.model.table
        permutation = self.model.row_permutation
        permutation_copy = permutation[:]

        # new entry in permutation
        table.add_row(table[self.data_row_idx])
        last_row = len(table) - 1
        if self.widget_row_idx == len(permutation) - 1:
            permutation.append(last_row)
        else:
            permutation.insert(self.widget_row_idx + 1, last_row)

        self.model.set_row_permutation(permutation)
        self.memory = (permutation_copy, last_row)
        return True

    def undo(self):
        super(CloneRowAction, self).undo()
        table = self.model.table
        permutation, row_idx = self.memory
        self.model.set_row_permutation(permutation)
        del table[row_idx]
        return True


class SortTableAction(TableAction):
    actionName = "sort table"

    def __init__(self, model, sort_data):
        super(SortTableAction, self).__init__(model, sort_data=sort_data)
        self.toview = dict(sortByColumn=sort_data)

    def do(self):
        table = self.model.table
        self.memory = self.model.row_permutation
        permutation = table._sorting_permutation(self.sort_data)
        self.model.set_row_permutation(permutation)
        return True

    def undo(self):
        super(SortTableAction, self).undo()
        self.model.set_row_permutation(self.memory)
        return True


class ChangeAllValuesInColumnAction(TableAction):
    actionName = "change all values"

    def __init__(
        self, model, widget_col_index, data_row_indices, data_col_index, value
    ):
        super(ChangeAllValuesInColumnAction, self).__init__(
            model,
            widget_col_index=widget_col_index,
            data_row_indices=data_row_indices,
            data_col_index=data_col_index,
            value=value,
        )
        self.toview = dict(column=widget_col_index, value=value)

    def do(self):
        table = self.model.table
        # +1 to avoid _index entry of Row class:
        self.memory = [
            row[self.data_col_index + 1] for row in table[self.data_row_indices]
        ]
        self.model.beginResetModel()
        table._set_value(self.data_row_indices, self.data_col_index, self.value)
        self.model.endResetModel()
        return True

    def undo(self):
        super(ChangeAllValuesInColumnAction, self).undo()

        self.model.beginResetModel()
        # todo: implement this in emzed to support multiple values!
        self.model.table._set_values(
            self.data_row_indices, self.data_col_index, self.memory
        )
        self.model.endResetModel()
        return True


class ChangeValueAction(TableAction):
    actionName = "change value"

    def __init__(self, model, idx, row_idx, col_idx, value):
        super(ChangeValueAction, self).__init__(
            model, idx=idx, row_idx=row_idx, col_idx=col_idx, value=value
        )
        self.toview = dict(row=idx.row(), column=idx.column(), value=value)

    def do(self):
        table = self.model.table

        # +1 because of _index field:
        self.memory = table[self.row_idx][self.col_idx + 1]

        if self.memory == self.value:
            return False

        table._set_value([self.row_idx], self.col_idx, self.value)

        self.model.dataChanged.emit(self.idx, self.idx)
        return True

    def undo(self):
        super(ChangeValueAction, self).undo()
        table = self.model.table
        table._set_value([self.row_idx], self.col_idx, self.memory)
        self.model.dataChanged.emit(self.idx, self.idx)
        return True


class IntegrateAction(TableAction):
    actionName = "integrate"

    def __init__(
        self,
        model,
        data_row_indices,
        postfix,
        peak_shape_model_name,
        rtmin,
        rtmax,
        widget_row_indices,
        appendum="",
    ):
        super().__init__(
            model,
            data_row_indices=data_row_indices,
            postfix=postfix,
            peak_shape_model_name=peak_shape_model_name,
            rtmin=rtmin,
            rtmax=rtmax,
            widget_row_indices=widget_row_indices,
            memory=[],
        )
        self.toview = dict(
            rtmin=rtmin, rtmax=rtmax, model=peak_shape_model_name, postfix=postfix
        )
        self.appendum = appendum

    def do(self):
        integrator = available_peak_shape_models.get(self.peak_shape_model_name)
        table = self.model.table
        for data_row_idx in self.data_row_indices:
            row = table[data_row_idx]
            postfix = self.postfix

            mz_peak_cols = ["mzmin", "mzmax", "rtmin", "rtmax", "peakmap"]

            area = rmse = model = is_valid = None
            if integrator and all(row[f + postfix] is not None for f in mz_peak_cols):
                pm = row["peakmap" + postfix]
                mzmin = row["mzmin" + postfix]
                mzmax = row["mzmax" + postfix]
                model = integrator.fit(
                    pm, self.rtmin, self.rtmax, mzmin, mzmax, ms_level=None
                )

                area = model.area
                rmse = model.rmse
                is_valid = model.is_valid

            self._save_current_state_and_set_cell_values(
                table,
                data_row_idx,
                area,
                rmse,
                model,
                is_valid,
            )

        self.emit_data_changed()

        return True

    def _save_current_state_and_set_cell_values(
        self, table, data_row_idx, area, rmse, model, is_valid
    ):
        self.memory.append(table[data_row_idx])
        app = self.appendum + self.postfix
        set_value = partial(table._set_value, [data_row_idx])
        set_value("peak_shape_model" + app, self.peak_shape_model_name)
        set_value("rtmin" + app, self.rtmin)
        set_value("rtmax" + app, self.rtmax)
        set_value("area" + app, area)
        set_value("rmse" + app, rmse)
        set_value("model" + app, model)
        set_value("valid_model" + app, is_valid)

    def undo(self):
        super().undo()
        table = self.model.table
        for m, data_row_idx in zip(self.memory, self.data_row_indices):
            app = self.appendum + self.postfix
            set_value = partial(table._set_value, [data_row_idx])

            set_value("peak_shape_model" + app, getattr(m, "peak_shape_model" + app))
            set_value("rtmin" + app, getattr(m, "rtmin" + app))
            set_value("rtmax" + app, getattr(m, "rtmax" + app))
            set_value("area" + app, getattr(m, "area" + app))
            set_value("rmse" + app, getattr(m, "rmse" + app))
            set_value("model" + app, getattr(m, "model" + app))
            set_value("valid_model" + app, getattr(m, "valid_model" + app))
        self.emit_data_changed()
        return True

    def emit_data_changed(self):
        tl = self.model.createIndex(min(self.widget_row_indices), 0)
        tr = self.model.createIndex(
            max(self.widget_row_indices), self.model.columnCount() - 1
        )
        self.model.dataChanged.emit(tl, tr)


class ChromatogramIntegrateAction(IntegrateAction):
    actionName = "integrate_chromatogram"

    def __init__(
        self,
        model,
        data_row_indices,
        postfix,
        peak_shape_model_name,
        rtmin,
        rtmax,
        widget_row_indices,
    ):
        super().__init__(
            model,
            data_row_indices,
            postfix,
            peak_shape_model_name,
            rtmin,
            rtmax,
            widget_row_indices,
            "_chromatogram",
        )

    def do(self):
        integrator = available_peak_shape_models.get(self.peak_shape_model_name)
        table = self.model.table
        for data_row_idx in self.data_row_indices:
            row = table[data_row_idx]
            postfix = self.postfix
            chromatogram_cols = [
                "rtmin_chromatogram",
                "rtmax_chromatogram",
                "chromatogram",
            ]

            area = rmse = model = is_valid = None
            if integrator and all(
                row[f + postfix] is not None for f in chromatogram_cols
            ):
                chromatogram = row["chromatogram" + postfix]

                model = integrator.fit_chromatogram(
                    self.rtmin, self.rtmax, chromatogram
                )
                area = model.area
                rmse = model.rmse
                is_valid = model.is_valid

            self._save_current_state_and_set_cell_values(
                table, data_row_idx, area, rmse, model, is_valid
            )

        self.emit_data_changed()

        return True
