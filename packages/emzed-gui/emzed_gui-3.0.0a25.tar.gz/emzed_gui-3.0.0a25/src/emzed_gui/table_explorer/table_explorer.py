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


import time
import traceback

from emzed import PeakMap, Spectrum, Table
from emzed.ms_data import ImmutablePeakMap
from emzed.quantification.peak_integration import available_peak_shape_models
from PyQt5.Qt import QApplication
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QAction,
    QComboBox,
    QHeaderView,
    QLabel,
    QListWidget,
    QMenu,
    QMenuBar,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QSizePolicy,
)

from emzed_gui import ask_for_save, show_warning
from emzed_gui.emzed_dialog import EmzedDialog
from emzed_gui.helpers import debug_mode, protect_signal_handler, timethis
from emzed_gui.inspectors import has_inspector
from emzed_gui.widgets import (
    ColumnMultiSelectDialog,
    FilterCriteriaWidget,
    IntegrationWidget,
)
from emzed_gui.widgets.eic_plotting_widget import EicPlottingWidget
from emzed_gui.widgets.mz_plotting_widget import MzPlottingWidget

from .ask_value import ask_value
from .async_runner import block_and_run_in_background, ui_blocked
from .table_explorer_layout import TableExplorerLayout
from .table_explorer_model import TableModel, isUrl, supported_postfixes
from .table_view import EmzedTableView
from .text_delegate import TextDelegate


def create_button(txt=None, parent=None):
    btn = QPushButton(parent=parent)
    if txt is not None:
        btn.setText(txt)
    btn.setAutoDefault(False)
    btn.setDefault(False)
    return btn


class TableExplorer(EmzedDialog, TableExplorerLayout):
    def __init__(
        self,
        tables,
        offerAbortOption,
        parent=None,
        close_callback=None,
        custom_buttons_config=None,
    ):
        super(TableExplorer, self).__init__(parent)

        if custom_buttons_config is None:
            custom_buttons_config = []

        if not all(
            isinstance(item, tuple) for item in custom_buttons_config
        ) or not all(len(item) == 2 for item in custom_buttons_config):
            raise ValueError(
                "except list of tuples (label, callback) for custom_buttons_config"
            )

        self.custom_buttons_config = custom_buttons_config

        # function which is called when window is closed. the arguments passed are
        # boolean
        # flags indication for every table if it was modified:
        self.close_callback = close_callback

        # Destroying the C++ object right after closing the dialog box, otherwise it may
        # be garbage-collected in another QThread thus leading to a segmentation fault
        # on UNIX or an application crash on Windows
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setWindowFlags(
            Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        )

        self.offerAbortOption = offerAbortOption

        self.models = [
            TableModel.table_model_for(table, parent=self) for table in tables
        ]
        self.model = None
        self.tableView = None

        self.hadFeatures = None

        self.setupWidgets()
        self.setupLayout()
        self.connectSignals()

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)
        self.setSizeGripEnabled(True)

        self.current_model_index = 0
        self.setupViewForTable()

        self.current_to_plot = None
        self.in_plot = False

    def done(self, i):
        return super().done(i)

    def reject(self):
        super(TableExplorer, self).reject()
        modified = [len(m.actions) > 0 for m in self.models]
        if self.close_callback is not None:
            try:
                self.close_callback(*modified)
            except Exception:
                traceback.print_exc()

    def keyPressEvent(self, e):
        # disable handling escape key
        if e.key() != Qt.Key_Escape:
            super(TableExplorer, self).keyPressEvent(e)

    def setupWidgets(self):
        self.setupMenuBar()
        self.setupTableViews()

        # TODO: next call is slow. only setup if we have plots in any of the
        # tables?
        self.setupPlottingWidgets()
        self.setupIntegrationWidgets()
        self.setupToolWidgets()
        self.setupCallbackButtons()  #
        if self.offerAbortOption:
            self.setupAcceptButtons()

    def setupMenuBar(self):
        self.menubar = QMenuBar(self)
        menu = self.buildEditMenu()
        self.menubar.addMenu(menu)
        self.chooseTableActions = []
        if len(self.models) > 1:
            menu = self.buildChooseTableMenu()
            self.menubar.addMenu(menu)

    def buildEditMenu(self):
        self.undoAction = QAction("Undo", self)
        self.undoAction.setShortcut(QKeySequence("Ctrl+Z"))
        self.redoAction = QAction("Redo", self)
        self.redoAction.setShortcut(QKeySequence("Ctrl+Y"))
        menu = QMenu("Edit", self.menubar)
        menu.addAction(self.undoAction)
        menu.addAction(self.redoAction)
        return menu

    def setupTableViews(self):
        self.tableViews = []
        self.filterWidgets = []
        self.filters_enabled = False
        for i, model in enumerate(self.models):
            self.tableViews.append(self.setupTableViewFor(model))
            self.filterWidgets.append(self.setupFilterWidgetFor(model.table))

    def setupFilterWidgetFor(self, table):
        w = FilterCriteriaWidget(self)
        w.configure(table)
        w.LIMITS_CHANGED.connect(self.limits_changed)
        return w

    def limits_changed(self, filters):
        timethis(self.model.limits_changed)(filters)

    def set_delegates(self):
        if self.model.has_color:
            self.tableView.setItemDelegate(TextDelegate(self.tableView, self.model))

    def remove_delegates(self):
        types = self.model.table.col_types
        for i, j in list(self.model.widgetColToDataCol.items()):
            # TODO
            if 0 and types[j] in (bool, CallBack):
                self.tableView.setItemDelegateForColumn(i, None)

    def setupTableViewFor(self, model):
        tableView = EmzedTableView(self)
        tableView.setModel(model)
        tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        tableView.horizontalHeader().setSectionsMovable(1)
        pol = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tableView.setSizePolicy(pol)
        tableView.setVisible(False)
        # before filling the table, disabling sorting accelerates table
        # construction, sorting is enabled in TableView.showEvent, which is
        # called after construction
        tableView.setSortingEnabled(False)
        return tableView

    def buildChooseTableMenu(self):
        menu = QMenu("Choose Table", self.menubar)
        for i, model in enumerate(self.models):
            action = QAction(" [%d]: %s" % (i, model.getTitle()), self)
            menu.addAction(action)
            self.chooseTableActions.append(action)
        return menu

    def setupPlottingWidgets(self):
        self.mz_plotter = MzPlottingWidget()
        self.eic_plotter = EicPlottingWidget()

        pol = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        pol.setVerticalStretch(5)

        self.eic_plotter.setSizePolicy(pol)
        self.mz_plotter.setSizePolicy(pol)

        self.spec_label = QLabel("Spectra:")
        self.spec_label = QLabel("")
        self.choose_spec = QListWidget()
        self.choose_spec.setFixedHeight(90)
        self.choose_spec.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def setupIntegrationWidgets(self):
        self.integration_widget = IntegrationWidget(self)
        names = sorted(available_peak_shape_models.keys())
        self.integration_widget.set_integration_methods(names)

    def setupToolWidgets(self):
        self.chooseGroubLabel = QLabel("Expand selection:", parent=self)
        self.chooseGroupColumn = QComboBox(parent=self)
        self.chooseGroupColumn.setMinimumWidth(150)

        self.choose_visible_columns_button = create_button("Visible columns")

        self.filter_on_button = create_button("Filter rows")

        self.sort_label = QLabel("sort by:", parent=self)

        self.sort_fields_widgets = []
        self.sort_order_widgets = []
        for i in range(3):
            w = QComboBox(parent=self)
            w.setMinimumWidth(100)
            self.sort_fields_widgets.append(w)
            w = QComboBox(parent=self)
            w.addItems(["asc", "desc"])
            w.setMaximumWidth(60)
            self.sort_order_widgets.append(w)

        self.restrict_to_filtered_button = create_button("Restrict to filter result")
        self.remove_filtered_button = create_button("Remove filter result")
        self.export_table_button = create_button("Export table")

        self.restrict_to_filtered_button.setEnabled(False)
        self.remove_filtered_button.setEnabled(False)

    def setupCallbackButtons(self):
        self.extra_buttons = []
        for label, callback in self.custom_buttons_config:
            button = create_button(label, self)
            self.extra_buttons.append(button)

            def handler(event, callback=callback, self=self):
                try:
                    self.setEnabled(False)
                    self.setCursor(Qt.WaitCursor)
                    self.model.transform_table(callback, parent=self)
                finally:
                    self.setEnabled(True)
                    self.setCursor(Qt.ArrowCursor)
                index = self.current_model_index
                self.filterWidgets[index] = self.setupFilterWidgetFor(self.model.table)
                self.setupViewForTable()

            button.clicked.connect(handler)

    def setupAcceptButtons(self):
        self.ok_button = create_button("Ok", parent=self)
        self.abort_button = create_button("Abort", parent=self)
        self.result = 1  # default for closing

    def enable_integration_widgets(self, flag=True):
        self.integration_widget.setEnabled(flag)

    def enable_spec_chooser_widgets(self, flag=True):
        self.spec_label.setVisible(flag)
        self.choose_spec.setEnabled(flag)

    def set_window_title(self, n_rows_total, n_rows_visible):
        model_title = self.model.getTitle()
        title = "%d out of %d rows from %s" % (
            n_rows_visible,
            n_rows_total,
            model_title,
        )
        self.setWindowTitle(title)

    def setup_model_dependent_look(self):
        has_peaks = self.model.has_peaks()
        has_peakshape_model = self.model.has_peakshape_model()
        has_chromatograms = self.model.has_chromatograms()
        hasSpectra = self.model.hasSpectra()

        self.chromatogram_only_mode = (
            has_chromatograms and not has_peaks
        )  # includes: not isIntegrated !
        self.has_chromatograms = has_chromatograms
        self.has_peaks = has_peaks
        self.has_peakshape_model = has_peakshape_model
        self.allow_integration = has_peakshape_model and self.model.implements(
            "integrate"
        )
        self.has_spectra = hasSpectra and not self.chromatogram_only_mode

        self.eic_plotter.setVisible(self.chromatogram_only_mode or self.has_peaks)
        self.eic_plotter.enable_range(not self.chromatogram_only_mode)

        if self.has_peaks or self.has_spectra:
            show_mz = True
        else:
            show_mz = False

        self.mz_plotter.setVisible(show_mz)

        self.enable_integration_widgets(self.allow_integration)
        self.enable_spec_chooser_widgets(
            self.has_spectra or self.has_peaks or self.has_chromatograms
        )
        self.middleFrame.setVisible(self.allow_integration or self.has_spectra)

        self.choose_spec.clear()

    @protect_signal_handler
    def handleClick(self, index, model):
        content = model.data(index)
        if isUrl(content):
            QDesktopServices.openUrl(QUrl(content))
        else:
            self.tableView.selectRow(index.row())
            self.tableView.verticalHeader().sectionClicked.emit(index.row())
            self.row_clicked(index.row())

    def connectSignals(self):
        for i, action in enumerate(self.chooseTableActions):
            handler = lambda *a, i=i: self.setupViewForTable(i)
            handler = protect_signal_handler(handler)
            action.triggered.connect(handler)

        for view in self.tableViews:
            vh = view.verticalHeader()
            vh.setContextMenuPolicy(Qt.CustomContextMenu)
            vh.customContextMenuRequested.connect(self.openContextMenuVerticalHeader)
            vh.sectionClicked.connect(self.row_clicked)

            hh = view.horizontalHeader()
            hh.setContextMenuPolicy(Qt.CustomContextMenu)
            hh.customContextMenuRequested.connect(self.openContextMenuHorizontalHeader)

            model = view.model()
            handler = lambda idx, model=model: self.handleClick(idx, model)
            handler = protect_signal_handler(handler)
            model.ACTION_LIST_CHANGED.connect(self.updateMenubar)
            view.clicked.connect(handler)
            view.doubleClicked.connect(self.handle_double_click)

        self.integration_widget.TRIGGER_INTEGRATION.connect(self.do_integrate)
        self.choose_spec.itemSelectionChanged.connect(self.spectrumChosen)

        if self.offerAbortOption:
            self.ok_button.clicked.connect(self.ok)
            self.abort_button.clicked.connect(self.abort)

        self.choose_visible_columns_button.clicked.connect(self.choose_visible_columns)

        self.filter_on_button.clicked.connect(self.filter_toggle)
        self.remove_filtered_button.clicked.connect(self.remove_filtered)

        self.restrict_to_filtered_button.clicked.connect(self.restrict_to_filtered)

        self.export_table_button.clicked.connect(self.export_table)

        for sort_field_w in self.sort_fields_widgets:
            sort_field_w.activated.connect(self.sort_fields_changed)

        for sort_order_w in self.sort_order_widgets:
            sort_order_w.activated.connect(self.sort_fields_changed)

        self.eic_plotter.SELECTED_RANGE_CHANGED.connect(self.eic_selection_changed)

    @protect_signal_handler
    def sort_fields_changed(self, __):
        sort_data = [
            (str(f0.currentText()), str(f1.currentText()))
            for f0, f1 in zip(self.sort_fields_widgets, self.sort_order_widgets)
        ]
        sort_data = [(f0, f1) for (f0, f1) in sort_data if f0 != "-" and f0 != ""]
        if sort_data:
            self.model.sort_by(sort_data)
            main_name, main_order = sort_data[0]
            idx = self.model.widget_col(main_name)
            if idx is not None:
                header = self.tableView.horizontalHeader()
                header.blockSignals(True)
                header.setSortIndicator(
                    idx,
                    Qt.AscendingOrder
                    if main_order.startswith("asc")
                    else Qt.DescendingOrder,
                )
                header.blockSignals(False)

    @protect_signal_handler
    def filter_toggle(self, *a):
        self.filters_enabled = not self.filters_enabled
        for model in self.models:
            model.setFiltersEnabled(self.filters_enabled)
        self.filter_widgets_container.setVisible(self.filters_enabled)
        self.restrict_to_filtered_button.setEnabled(self.filters_enabled)
        self.remove_filtered_button.setEnabled(self.filters_enabled)
        if self.filters_enabled:
            # we add spaces becaus on mac the text field cut when rendered
            self.filter_on_button.setText("Disable row filtering")
            self.export_table_button.setText("Export filtered")
        else:
            # we add spaces becaus on mac the text field cut when rendered
            self.filter_on_button.setText("Enable row filtering")
            self.export_table_button.setText("Export table")

    @protect_signal_handler
    def choose_visible_columns(self, *a):
        self.remove_delegates()
        col_names, is_currently_visible = self.model.columnames_with_visibility()
        if not col_names:
            return

        # zip, sort and unzip then:
        col_names, is_currently_visible = list(
            zip(*sorted(zip(col_names, is_currently_visible)))
        )
        dlg = ColumnMultiSelectDialog(col_names, is_currently_visible)
        dlg.exec_()
        if dlg.column_settings is None:
            return

        # did we change visibility of columns?
        should_be_visible = [v for (_, _, v) in dlg.column_settings]
        if should_be_visible == list(is_currently_visible):
            return

        hide_names = [n for (n, col_idx, visible) in dlg.column_settings if not visible]
        self.update_hidden_columns(hide_names)
        self.model.save_preset_hidden_column_names()
        self.tableView.resize_columns()

    def update_hidden_columns(self, hidden_names):
        self.model.hide_columns(hidden_names)
        self.set_delegates()
        self.setup_choose_group_column_widget(hidden_names)
        self.setup_sort_fields(hidden_names)
        self.current_filter_widget.hide_filters(hidden_names)
        if self.model.table.is_mutable():
            self.model.table.meta_data["hide_in_explorer"] = hidden_names
        self.setup_sort_fields(hidden_names)

    @protect_signal_handler
    def remove_filtered(self, *a):
        self.model.remove_filtered()

    @protect_signal_handler
    def restrict_to_filtered(self, *a):
        block_and_run_in_background(self, self.model.restrict_to_visible_rows)

    @protect_signal_handler
    def export_table(self, *a):
        n = len(self.model)
        if n > 1000:
            answer = QMessageBox.question(
                self,
                "Are you sure ?",
                "the final table would contain "
                "%d lines. Are you sure to continue ?" % n,
                QMessageBox.Ok | QMessageBox.Cancel,
            )
            if answer == QMessageBox.Cancel:
                return
        path = ask_for_save(extensions=["csv", "xlsx", "xls", "table"])
        if path is not None:
            self.setEnabled(False)
            self.setCursor(Qt.WaitCursor)
            self.blockSignals(True)
            try:
                self.model.save_table(path)
            except Exception as e:
                show_warning(f"something went wrong: {e!s}")
            finally:
                self.setEnabled(True)
                self.setCursor(Qt.ArrowCursor)
                self.blockSignals(False)

    @protect_signal_handler
    def handle_double_click(self, idx):
        row_idx, col_idx = self.model.table_index(idx)
        row = self.model.row(idx)
        cell_value = self.model.cell_value(idx)
        col_type = self.model.table.col_types[col_idx]

        if col_type is bool:
            if cell_value is None:
                cell_value = "True"
            elif cell_value is True:
                cell_value = "False"
            else:
                cell_value = "-"
            self.model.setData(idx, cell_value)
            return

        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()

        # local import avoids circular import
        from emzed_gui import inspect

        if isinstance(cell_value, ImmutablePeakMap):
            col_name = self.model.column_name(idx)
            if "__" in col_name:
                __, __, postfix = col_name.partition("__")
            else:
                postfix = ""

            base_cols = ("rtmin", "rtmax", "mzmin", "mzmax")

            if all(name + postfix in row for name in base_cols):
                window = tuple(row[name + postfix] for name in base_cols)
            else:
                window = None
            inspect(cell_value, modal=False, parent=self, window=window)

        elif isinstance(cell_value, Table):
            inspect(cell_value, modal=False, parent=self)

        QApplication.setOverrideCursor(Qt.ArrowCursor)

    def disconnectModelSignals(self):
        self.model.dataChanged.disconnect(self.dataChanged)
        self.model.modelReset.disconnect(self.handle_model_reset)
        self.undoAction.triggered.disconnect(self.model.undoLastAction)
        self.redoAction.triggered.disconnect(self.model.redoLastAction)

    def connectModelSignals(self):
        self.model.dataChanged.connect(self.dataChanged)
        self.model.modelReset.connect(self.handle_model_reset)
        self.undoAction.triggered.connect(self.model.undoLastAction)
        self.redoAction.triggered.connect(self.model.redoLastAction)

        self.model.VISIBLE_ROWS_CHANGE.connect(self.set_window_title)
        self.model.SORT_TRIGGERED.connect(self.sort_by_click_in_header)

    @protect_signal_handler
    def sort_by_click_in_header(self, name, is_ascending):
        for f in self.sort_fields_widgets:
            f.blockSignals(True)
        for f in self.sort_order_widgets:
            f.blockSignals(True)

        main_widget = self.sort_fields_widgets[0]
        idx = main_widget.findText(name)
        main_widget.setCurrentIndex(idx)
        for i in range(1, len(self.sort_fields_widgets)):
            self.sort_fields_widgets[i].setCurrentIndex(0)

        for f in self.sort_fields_widgets:
            f.blockSignals(False)
        for f in self.sort_order_widgets:
            f.blockSignals(False)

        self.sort_order_widgets[0].setCurrentIndex(1 - int(is_ascending))

    def group_column_selected(self, idx):
        self.tableView.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def updateMenubar(self, undoInfo, redoInfo):
        self.undoAction.setEnabled(undoInfo is not None)
        self.redoAction.setEnabled(redoInfo is not None)
        if undoInfo:
            self.undoAction.setText("Undo: %s" % undoInfo)
        if redoInfo:
            self.redoAction.setText("Redo: %s" % redoInfo)

    def setupViewForTable(self, i=None, *a):
        if i is None:
            i = self.current_model_index
        self.current_model_index = i

        for j, action in enumerate(self.chooseTableActions):
            txt = str(action.text())  # QString -> Python unicode
            if txt.startswith("*"):
                txt = " " + txt[1:]
                action.setText(txt)
            if i == j:
                action.setText("*" + txt[1:])

        self.table_view_container.setCurrentIndex(i)
        self.filter_widgets_container.setCurrentIndex(i)

        if self.model is not None:
            self.disconnectModelSignals()
        self.model = self.models[i]
        self.current_filter_widget = self.filterWidgets[i]
        self.tableView = self.tableViews[i]

        hidden = self.model.table.meta_data.get("hide_in_explorer", ())
        self.update_hidden_columns(hidden)
        try:
            shown = self.model.load_preset_hidden_column_names()
            hidden = list(set(self.model.table.col_names) - shown)
            self.update_hidden_columns(hidden)
        except Exception:
            pass

        self.setup_model_dependent_look()
        if self.model.implements("setNonEditable"):
            self.model.setNonEditable(
                "peak_shape_model", ["area", "rmse", "peak_shape_model", "params"]
            )

        if self.model.implements("addNonEditable"):
            for i, col_name in enumerate(self.model.table.col_names):
                t = self.model.table.col_types[i]
                if (
                    t in (list, tuple, object, dict, set)
                    or t is None
                    or has_inspector(t)
                ):
                    self.model.addNonEditable(i)

        mod = self.model
        postfixes_peaks = supported_postfixes(mod.table, mod.integration_col_names())
        postfixes_chromatograms = supported_postfixes(
            mod.table, mod.chromatogram_integration_col_names()
        )

        labels = [f"peakmap{pf}" for pf in postfixes_peaks] + [
            f"chromatogram{pf}" for pf in postfixes_chromatograms
        ]

        self.integration_widget.set_postfixes(labels)

        self.setup_choose_group_column_widget(hidden)
        self.setup_sort_fields(hidden)
        self.connectModelSignals()
        self.updateMenubar(None, None)
        self.set_window_title(len(self.model.table), len(self.model.table))

    def setup_choose_group_column_widget(self, hidden_names):
        before = None
        if self.chooseGroupColumn.currentIndex() >= 0:
            before = str(self.chooseGroupColumn.currentText())
        self.chooseGroupColumn.clear()
        t = self.model.table
        candidates = [n for (n, f) in zip(t.col_names, t.col_formats) if f is not None]
        visible_names = [n for n in candidates if n not in hidden_names]
        all_choices = ["- manual multi select -"] + sorted(visible_names)
        self.chooseGroupColumn.addItems(all_choices)
        if before is not None and before in all_choices:
            idx = all_choices.index(before)
            self.chooseGroupColumn.setCurrentIndex(idx)

    def setup_sort_fields(self, hidden_names):
        before = []
        for field in self.sort_fields_widgets:
            if field.currentIndex() >= 0:
                before.append(str(field.currentText()))
            else:
                before.append(None)

        t = self.model.table
        candidates = [n for (n, f) in zip(t.col_names, t.col_formats) if f is not None]
        visible_names = [n for n in candidates if n not in hidden_names]

        all_choices = ["-"] + visible_names

        for field in self.sort_fields_widgets:
            field.clear()
            field.addItems(all_choices)

        for choice_before, field in zip(before, self.sort_fields_widgets):
            if choice_before is not None and choice_before in all_choices:
                idx = all_choices.index(choice_before)
                field.setCurrentIndex(idx)

    @protect_signal_handler
    def handle_model_reset(self):
        for name in self.model.table.col_names:
            self.current_filter_widget.update(name)

    def reset_sort_fields(self):
        for field in self.sort_fields_widgets:
            field.setCurrentIndex(0)

    def dataChanged(self, ix1, ix2, *_):
        minr, maxr = sorted((ix1.row(), ix2.row()))
        minc, maxc = sorted((ix1.column(), ix2.column()))
        for r in range(minr, maxr + 1):
            for c in range(minc, maxc + 1):
                idx = self.model.createIndex(r, c)
                self.tableView.update(idx)

        minc = self.model.widgetColToDataCol[minc]
        maxc = self.model.widgetColToDataCol[maxc]
        minr = self.model.widgetRowToDataRow[minr]
        maxr = self.model.widgetRowToDataRow[maxr]

        for name in self.model.table.col_names[minc : maxc + 1]:
            self.current_filter_widget.update(name)

        if self.has_peaks or self.has_chromatograms:
            if any(minr <= index <= maxr for index in self.model.selected_data_rows):
                self.plot_peaks(reset_limits=False, force=True)

        self.reset_sort_fields()

    @protect_signal_handler
    def abort(self, *_):
        self.result = 1
        self.close()

    @protect_signal_handler
    def ok(self, *_):
        self.result = 0
        self.close()

    @protect_signal_handler
    def openContextMenuHorizontalHeader(self, point):
        widget_col_index = self.tableView.horizontalHeader().logicalIndexAt(point)
        column_type = self.model.column_type(widget_col_index)

        menu = QMenu()
        if column_type in (object, PeakMap, Table):
            menu.addAction("set all to None")
        else:
            menu.addAction("set all")

        appear_at = self.tableView.horizontalHeader().mapToGlobal(point)
        chosen = menu.exec_(appear_at)
        if chosen is None:
            return
        column_name = self.model.column_name(widget_col_index)
        if column_type in (object, PeakMap, Table):
            value = None
        else:
            canceled, value = ask_value(column_name, column_type)
            if canceled:
                return
        with ui_blocked(self):
            self.model.set_all(widget_col_index, value)

    @protect_signal_handler
    def openContextMenuVerticalHeader(self, point):
        index = self.tableView.verticalHeader().logicalIndexAt(point)
        menu = QMenu()

        if self.model.implements("clone_row"):
            cloneAction = menu.addAction("Clone row")
        else:
            cloneAction = None

        if self.model.implements("remove_rows"):
            removeAction = menu.addAction("Delete row")
        else:
            removeAction = None
        undoInfo = self.model.infoLastAction()
        redoInfo = self.model.infoRedoAction()

        if undoInfo is not None:
            undoAction = menu.addAction("Undo %s" % undoInfo)
        if redoInfo is not None:
            redoAction = menu.addAction("Redo %s" % redoInfo)
        appearAt = self.tableView.verticalHeader().mapToGlobal(point)
        choosenAction = menu.exec_(appearAt)
        if choosenAction == removeAction:
            selected = [
                idx.row() for idx in self.tableView.selectionModel().selectedRows()
            ]
            if not selected:
                selected = [index]
            self.model.remove_rows(selected)
        elif choosenAction == cloneAction:
            self.model.clone_row(index)
        elif undoInfo is not None and choosenAction == undoAction:
            self.model.undoLastAction()
        elif redoInfo is not None and choosenAction == redoAction:
            self.model.redoLastAction()

    @protect_signal_handler
    def do_integrate(self, method, label):
        # QString -> Python str:
        method = str(method)
        label = str(label)
        rtmin, rtmax = self.eic_plotter.get_range_selection_limits()
        self.model.integrate(label, method, rtmin, rtmax)

    def row_clicked(self, widget_row_idx):
        selected_rows_indices = [
            idx.row() for idx in self.tableView.selectionModel().selectedRows()
        ]
        self.model.set_row_header_colors(
            selected_rows_indices,
            color_row_headers=self.has_spectra
            or self.has_peaks
            or self.has_chromatograms,
        )

        group_by_idx = self.chooseGroupColumn.currentIndex()
        if group_by_idx > 0:
            self.select_rows_in_group(selected_rows_indices)
            return

        self.select_row()
        self.tableView.viewport().update()

    def select_row(self):
        start = time.time()
        process_events = QApplication.processEvents

        def handle_row_click():
            to_select = [
                idx.row() for idx in self.tableView.selectionModel().selectedRows()
            ]
            self.model.set_selected_widget_rows(to_select)

            return to_select

        def update(to_select, start=start):
            if to_select is not None:
                self.model.set_selected_widget_rows(to_select)

            self.choose_spec.blockSignals(True)
            yield
            try:
                self.setup_postfix_chooser()
            finally:
                self.choose_spec.blockSignals(False)

            if (self.has_peaks or self.has_chromatograms) and not self.has_spectra:
                # has spectra also triggers plot_peaks!
                self.plot_peaks()
            if self.has_spectra:
                yield
                self.spectrumChosen()
            if self.allow_integration:
                self.setup_integration_widget()
                yield

            # self.setCursor(Qt.ArrowCursor)
            needed = time.time() - start
            if debug_mode:
                print("row click done, needed %.2f s" % needed)

        selected_rows = handle_row_click()
        process_events()
        started = time.time()
        try:
            for _ in update(selected_rows):
                if time.time() > started + 0.3:
                    self.setCursor(Qt.WaitCursor)
                process_events()
        finally:
            self.setCursor(Qt.ArrowCursor)
            self.setEnabled(True)

    def select_rows_in_group(self, selected_rows_indices):
        rows = self._find_rows_in_same_group(selected_rows_indices)
        if rows:
            N = 50
            if len(rows) > N:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "multiselect would mark %d lines. "
                    "reduced number of lines to %d" % (len(rows), N),
                )
                rows = rows[:N]
            self.tableView.blockSignals(True)
            try:
                self._activate_rows_in_group(rows, selected_rows_indices)
            finally:
                self.tableView.blockSignals(False)

    def _find_rows_in_same_group(self, selected_rows_indices):
        col_name = str(self.chooseGroupColumn.currentText())
        self.tableView.blockSignals(True)
        try:
            to_select = timethis(self.model.rows_with_same_values)(
                col_name, selected_rows_indices
            )
            return to_select
        finally:
            self.tableView.blockSignals(False)

    def _activate_rows_in_group(self, to_select, selected_rows_indices):
        mode_before = self.tableView.selectionMode()
        scrollbar_before = self.tableView.verticalScrollBar().value()

        self.tableView.setSelectionMode(QAbstractItemView.MultiSelection)
        for i in to_select:
            # avoid "double click!" which de-selects current row
            if i not in selected_rows_indices:
                self.tableView.selectRow(i)
        self.tableView.setSelectionMode(mode_before)
        self.tableView.verticalScrollBar().setValue(scrollbar_before)

        self.model.set_selected_widget_rows(to_select)

        self.model.set_row_header_colors(
            to_select,
            color_row_headers=self.has_spectra
            or self.has_peaks
            or self.has_chromatograms,
        )

        if not self.chromatogram_only_mode:
            self.choose_spec.blockSignals(True)
            try:
                self.setup_postfix_chooser()
            finally:
                self.choose_spec.blockSignals(False)

        if self.has_peaks or self.has_chromatograms:
            self.plot_peaks()
        if self.has_spectra:
            self.spectrumChosen()
            pass
        if self.allow_integration:
            self.setup_integration_widget()

    def setup_integration_widget(self):
        rows = self.model.selected_data_rows
        models = set(
            m.model_name
            for row in rows
            for m in self.model.get_peak_shape_models(row)
            if m is not None
        )
        models |= set(
            m.model_name
            for row in rows
            for m in self.model.get_chromatogram_models(row)
            if m is not None
        )
        if len(models) == 1:
            model = models.pop()
            self.integration_widget.set_integration_method(model)
        else:
            self.integration_widget.set_integration_method(None)

    def setup_postfix_chooser(self):
        former_indices = [i.row() for i in self.choose_spec.selectedIndexes()]

        self.choose_spec.clear()

        data = []
        labels = []
        for pf in set(self.model.get_eic_postfixes()):
            data.append(pf)
            labels.append(f"peakmap{pf}")

        for pf in set(self.model.get_chromatogram_postfixes()):
            data.append(pf)
            labels.append(f"chromatogram{pf}")

        rows = self.model.selected_data_rows

        for idx in rows:
            pf, s = self.model.get_ms2_spectra(idx)
            for pfi, si in zip(pf, s):
                if si is not None:
                    for sii in si:
                        label = "spectra%s rt=%.2fm" % (pfi, sii.rt / 60.0)
                        if sii.precursors:
                            mz, intensity, polarity = sii.precursors[0]
                            label += " pre=(%.5f, %.2e)" % (mz, intensity)
                        labels.append(label)
                        data.append(sii)

        self.data_in_choser = data
        self.choose_spec.setVisible(len(data) > 0)
        self.spec_label.setVisible(len(data) > 0)

        for label in labels:
            self.choose_spec.addItem(label)

        if data and not former_indices:
            former_indices = [0]

        for former_index in former_indices:
            item = self.choose_spec.item(former_index)
            if item is None:
                continue
            self.choose_spec.blockSignals(True)
            item.setSelected(True)
            self.choose_spec.blockSignals(False)

    @protect_signal_handler
    def spectrumChosen(self):
        selected_data = [
            (idx.row(), self.data_in_choser[idx.row()])
            for idx in self.choose_spec.selectedIndexes()
        ]
        labels = [item.data(0) for item in self.choose_spec.selectedItems()]
        spectra_labels = []
        spectra = []
        for label, data_item in zip(labels, selected_data):
            if isinstance(data_item[1], Spectrum):
                spectra_labels.append(label)
                spectra.append(data_item)

        if labels and not spectra:
            self.plot_peaks(force=True)

        if spectra:
            self.mz_plotter.plot_spectra(spectra, spectra_labels)
            self.mz_plotter.resetAxes()
            self.mz_plotter.replot()

    def selected_postfixes(self):
        selected_data = [
            self.data_in_choser[idx.row()] for idx in self.choose_spec.selectedIndexes()
        ]
        return sorted(set(d for d in selected_data if isinstance(d, str)))

    def eic_selection_changed(self, rtmin, rtmax):
        for _ in self._update_mz_plot((rtmin, rtmax)):
            pass
        self.mz_plotter.plot.replot()

    def _selected_rows_plot_data(self, rt_window, rows):
        peak_data = []
        chromatograms = []
        postfixes = self.selected_postfixes() or None
        for idx in rows:
            for (
                pf,
                peak_id,
                rtmin,
                rtmax,
                mzmin,
                mzmax,
                pm,
            ) in self.model.get_plotting_data(idx, postfixes):
                if rt_window is not None:
                    rtmin, rtmax = rt_window

                label = str(peak_id) + pf
                peak_data.append((idx, pm, rtmin, rtmax, mzmin, mzmax, label))

            for (
                pf,
                peak_id,
                rtmin,
                rtmax,
                ms_chromatogram,
            ) in self.model.get_chromatograms(idx, postfixes):
                if rt_window is not None:
                    rtmin, rtmax = rt_window
                label = str(peak_id) + pf
                chromatograms.append((idx, rtmin, rtmax, ms_chromatogram, label))

        return peak_data, chromatograms

    def _selected_peak_shape_models(self):
        models = []
        postfixes = self.selected_postfixes() or None
        for idx in self.model.selected_data_rows:
            for model in self.model.get_peak_shape_models(idx, postfixes):
                if model is not None:
                    models.append(model)
        return models

    def _selected_chromatogram_models(self):
        models = []
        postfixes = self.selected_postfixes() or None
        for idx in self.model.selected_data_rows:
            for model in self.model.get_chromatogram_models(idx, postfixes):
                if model is not None:
                    models.append(model)
        return models

    def plot_peaks(self, reset_limits=True, force=False):
        if not force and self.current_to_plot == self.model.selected_data_rows:
            # duplicate call
            return
        self.current_to_plot = self.model.selected_data_rows

        if self.current_to_plot is None:
            return

        rows = self.current_to_plot
        peak_data, chromatograms = self._selected_rows_plot_data(None, rows)

        self.mz_plotter.reset()
        if peak_data or chromatograms:
            self._plot_peaks(peak_data, chromatograms)
        else:
            self.eic_plotter.reset()

        if reset_limits:
            self.eic_plotter.reset_rt_limits(fac=0.1)
        else:
            self.eic_plotter.replot()

        self.mz_plotter.replot()
        self.mz_plotter.reset_mz_limits(0.1)

    def _plot_peaks(self, peak_data, chromatograms):
        peak_shape_models = self._selected_peak_shape_models()
        chromatogram_models = self._selected_chromatogram_models()

        n_plots = len(peak_data) + len(chromatograms)
        if self.has_peakshape_model:
            n_plots += len(peak_data)

        # mz plotter
        n_plots += len(peak_data) + 1

        for _ in self._plot_with_progress(
            n_plots,
            self.eic_plotter.plot_eics_iter(
                peak_data, chromatograms, peak_shape_models, chromatogram_models
            ),
            self.mz_plotter.plot_peaks_iter(peak_data, background=True),
        ):
            QApplication.processEvents()

    def _plot_with_progress(self, n_total, *steps):
        dlg = QProgressDialog("extract eics", "", 0, n_total, parent=self)
        dlg.setCancelButton(None)
        started = time.time()
        try:
            i = 0
            for step in steps:
                for task in step:
                    if i > 1:
                        time_left = (time.time() - started) / i * (n_total - i)
                        if time_left > 0.5:
                            dlg.show()
                    dlg.setValue(i)
                    if dlg.wasCanceled():
                        return
                    i += 1
                    yield
        finally:
            dlg.close()

    def _update_mz_plot(self, rt_window=None):
        """rtmin and rtmax may overwrite the values from the selected rows !"""

        peak_data, chromatograms = self._selected_rows_plot_data(
            rt_window, self.model.selected_data_rows
        )

        yield

        if not peak_data:
            self.mz_plotter.reset()
            return

        n = len(peak_data)

        dlg = QProgressDialog("extract spectra", "", 0, n, parent=self)
        dlg.setCancelButton(None)
        started = time.time()

        try:
            for i, _ in enumerate(
                self.mz_plotter.plot_peaks_iter(peak_data, background=True)
            ):
                if i > 1:
                    time_left = (time.time() - started) / i * (n - i)
                    if time_left > 0.5:
                        dlg.show()
                dlg.setValue(i)
                if dlg.wasCanceled():
                    break
                yield

            self.mz_plotter.replot()
        finally:
            if dlg is not None:
                dlg.close()
