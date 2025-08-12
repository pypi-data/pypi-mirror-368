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


import os

from emzed import PeakMap
from PyQt5.Qt import QKeySequence
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAction,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from emzed_gui.emzed_dialog import EmzedDialog
from emzed_gui.file_dialogs import ask_for_save, ask_for_single_file
from emzed_gui.helpers import protect_signal_handler
from emzed_gui.widgets.eic_plotting_widget import EicPlottingWidget
from emzed_gui.widgets.image_scaling_widget import ImageScalingWidget
from emzed_gui.widgets.mz_plotting_widget import MzPlottingWidget
from emzed_gui.widgets.peakmap_plotting_widget import PeakMapPlottingWidget, get_range
from emzed_gui.widgets.spectra_selector_widget import SpectraSelectorWidget
from emzed_gui.widgets.view_range_widget import ViewRangeWidget


class History(object):
    def __init__(self):
        self.clear()

    def clear(self):
        self.items = []
        self.position = -1

    def new_head(self, item, max_len=20):
        del self.items[self.position + 1 :]
        self.items.append(item)
        if len(self.items) > max_len:
            # keep head !
            self.items = [self.items[0]] + self.items[-max_len - 1 :]
            self.position = len(self.items) - 1
        else:
            self.position += 1

    def go_back(self):
        if self.position > 0:
            self.position -= 1
            return self.items[self.position]
        return None

    def go_forward(self):
        if self.position < len(self.items) - 1:
            self.position += 1
            return self.items[self.position]
        return None

    def go_to_beginning(self):
        if self.position > 0:
            self.position = 0
            return self.items[self.position]
        return None

    def go_to_end(self):
        if self.position < len(self.items) - 1:
            self.position = len(self.items) - 1
            return self.items[self.position]
        return None

    def set_position(self, position):
        if 0 <= position < len(self.items) and position != self.position:
            self.position = position
            return self.items[self.position]
        return None


def create_table_widget(table, parent):
    formats = table.getColFormats()
    names = table.getColNames()
    indices_of_visible_columns = [j for (j, f) in enumerate(formats) if f is not None]
    headers = ["ok"] + [names[j] for j in indices_of_visible_columns]
    n_rows = len(table)

    widget = QTableWidget(n_rows, 1 + len(indices_of_visible_columns), parent=parent)
    widget.setHorizontalHeaderLabels(headers)
    widget.setMinimumSize(200, 200)

    widget.horizontalHeader().setResizeMode(QHeaderView.Interactive)

    for i, row in enumerate(table.rows):
        item = QTableWidgetItem()
        item.setCheckState(Qt.Unchecked)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable)
        widget.setItem(i, 0, item)
        for j0, j in enumerate(indices_of_visible_columns):
            value = row[j]
            formatter = table.colFormatters[j]
            item = QTableWidgetItem(formatter(value))
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            widget.setItem(i, j0 + 1, item)
    return widget


class PeakMapExplorer(EmzedDialog):
    def __init__(self, parent=None):
        super(PeakMapExplorer, self).__init__(parent)
        self.setWindowFlags(
            Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        )
        self.ok_rows = []

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.gamma = 3.0

        self.last_used_directory_for_load = None
        self.last_used_directory_for_save = None

        self.history = History()

    def keyPressEvent(self, e):
        # avoid closing of dialog when Esc key pressed:
        if e.key() != Qt.Key_Escape:
            return super(PeakMapExplorer, self).keyPressEvent(e)

    def set_window_title(self):
        if self.peakmap2 is None:
            title = os.path.basename(self.peakmap.meta_data.get("source", ""))
        else:
            p1 = os.path.basename(self.peakmap.meta_data.get("source", ""))
            p2 = os.path.basename(self.peakmap2.meta_data.get("source", ""))
            title = "yellow=%s, blue=%s" % (p1, p2)
        super(PeakMapExplorer, self).setWindowTitle(title)

    def setup(self, peakmap, peakmap2=None, table=None, window=None):
        self.table = table
        self.dual_mode = peakmap2 is not None
        self.setup_table_widgets()
        self.setup_input_widgets()
        self.setup_menu_bar()
        self.history_list = QComboBox(self)

        self.setup_plot_widgets()

        self.setup_layout()
        self.connect_signals_and_slots()
        self.setup_data(peakmap, peakmap2, table, window)

    def setup_data(self, peakmap, peakmap2=None, table=None, window=None):
        def collect_precursor_mz(pm):
            for s in pm:
                if s.precursors:
                    if s.ms_level > 1:
                        yield s.precursors[0][0]

        self.ms_levels = set(peakmap.ms_levels())
        self.precursor_mz = set(collect_precursor_mz(peakmap))
        if peakmap2 is not None:
            self.ms_levels &= set(peakmap2.ms_levels())
            self.precursor_mz &= set(collect_precursor_mz(peakmap2))

        self.ms_levels = sorted(self.ms_levels)
        self.precursor_mz = sorted(self.precursor_mz)
        self.full_pm = peakmap
        self.full_pm2 = peakmap2
        self.setup_ms2_widgets()
        self.current_ms_level = self.ms_levels[0]
        self.process_peakmap(self.current_ms_level)

        self.update_menu()

        self.peakmap_plotter.set_peakmaps(self.peakmap, self.peakmap2)
        self.peakmap_plotter.set_logarithmic_scale(1)
        self.peakmap_plotter.set_gamma(self.gamma)

        self.eic_plotter.set_zoom_limits(self.rtmin, self.rtmax)
        self.mz_plotter.set_zoom_limits(self.mzmin, self.mzmax)

        self.setup_initial_values()
        self.plot_peakmap()

        rtmin, rtmax = peakmap.rt_range()
        mzmin, mzmax = peakmap.mz_range()
        if peakmap2 is not None:
            rtmin2, rtmax2 = peakmap2.rt_range()
            mzmin2, mzmax2 = peakmap2.mz_range()
            rtmin = min(rtmin, rtmin2)
            rtmax = max(rtmax, rtmax2)
            mzmin = min(mzmin, mzmin2)
            mzmax = max(mzmax, mzmax2)

        self.history.clear()
        self.peakmap_view_range_changed(rtmin, rtmax, mzmin, mzmax)

        if window is not None:
            rtmin, rtmax, mzmin, mzmax = window

            rtmin = max(rtmin, self.rtmin)
            rtmax = min(rtmax, self.rtmax)

            mzmin = max(mzmin, self.mzmin)
            mzmax = min(mzmax, self.mzmax)
            # also adds history entry:
            self.peakmap_view_range_changed(rtmin, rtmax, mzmin, mzmax)

    def setup_ms2_widgets(self):
        self.spectra_selector_widget.set_data(self.ms_levels, self.precursor_mz)

    def setup_table_widgets(self):
        if self.table is not None:
            self.table_widget = create_table_widget(self.table, self)
            self.select_all_peaks = QPushButton("Select all peaks", self)
            self.unselect_all_peaks = QPushButton("Unselect all peaks", self)
            self.done_button = QPushButton("Done", self)

    def setup_menu_bar(self):
        self.menu_bar = QMenuBar(self)
        self.menu = QMenu("Peakmap Explorer", self.menu_bar)
        self.menu_bar.addMenu(self.menu)

    def update_menu(self):
        self.menu.clear()
        if not self.dual_mode:
            self.load_action = QAction("Load Peakmap", self)
            self.load_action.setShortcut(QKeySequence("Ctrl+L"))
            self.load_action2 = None
            self.menu.addAction(self.load_action)
            self.load_action.triggered.connect(self.do_load)
        else:
            self.load_action = QAction("Load Yellow Peakmap", self)
            self.load_action2 = QAction("Load Blue Peakmap", self)
            self.menu.addAction(self.load_action)
            self.menu.addAction(self.load_action2)
            self.load_action.triggered.connect(self.do_load_yellow)
            self.load_action2.triggered.connect(self.do_load_blue)

        self.save_action = QAction("Save selected range as image", self)
        self.save_action.setShortcut(QKeySequence("Ctrl+S"))
        self.menu.addAction(self.save_action)
        self.save_action.triggered.connect(self.do_save)

        # help_menu = QMenu("Help", self.menu_bar)
        # self.help_action = QAction("Help", self)
        # self.help_action.setShortcut(QKeySequence("F1"))
        # help_menu.addAction(self.help_action)
        # self.menu_bar.addMenu(help_menu)

    def process_peakmap(self, ms_level=None, pre_mz_min=None, pre_mz_max=None):
        peakmap = self.full_pm
        if ms_level is None:
            ms_level = min(peakmap.ms_levels())

        peakmap = peakmap.extract(
            precursormzmin=pre_mz_min,
            precursormzmax=pre_mz_max,
            mslevelmin=ms_level,
            mslevelmax=ms_level,
        )

        peakmap2 = None

        if self.full_pm2 is not None:
            peakmap2 = self.full_pm2
            peakmap2 = peakmap2.extract(
                precursormzmin=pre_mz_min,
                precursormzmax=pre_mz_max,
                mslevelmin=ms_level,
                mslevelmax=ms_level,
            )

        self.peakmap = peakmap
        self.peakmap2 = peakmap2

        self.rtmin, self.rtmax, self.mzmin, self.mzmax = get_range(peakmap, peakmap2)

        self.set_window_title()

    def setup_initial_values(self):
        imax = self.peakmap_plotter.get_total_imax()
        self.image_scaling_widget.set_max_intensity(imax)
        self.image_scaling_widget.set_gamma(self.gamma)

        self.view_range_widget.set_view_range(
            self.rtmin, self.rtmax, self.mzmin, self.mzmax
        )

    def setup_input_widgets(self):
        self.image_scaling_widget = ImageScalingWidget(self)
        self.spectra_selector_widget = SpectraSelectorWidget(self)
        self.view_range_widget = ViewRangeWidget(self)

    def setup_plot_widgets(self):
        self.peakmap_plotter = PeakMapPlottingWidget()
        self.eic_plotter = EicPlottingWidget(with_range=False)
        self.mz_plotter = MzPlottingWidget(show_legend=self.dual_mode)

    def setup_layout(self):
        outer_layout = QVBoxLayout()
        outer_layout.addWidget(self.menu_bar)
        outer_layout.setStretch(0, 1)

        h_splitter = QSplitter(self)
        h_splitter.setOrientation(Qt.Horizontal)

        # FIRST COLUMN of h_splitter is chromatogram + peakmap:
        # ############################

        v_splitter1 = QSplitter(self)
        v_splitter1.setOrientation(Qt.Vertical)
        v_splitter1.addWidget(self.eic_plotter)
        v_splitter1.addWidget(self.peakmap_plotter)
        self.peakmap_plotter.setMinimumSize(250, 200)
        v_splitter1.setStretchFactor(0, 1)
        v_splitter1.setStretchFactor(1, 3)

        h_splitter.addWidget(v_splitter1)
        h_splitter.setStretchFactor(0, 2)

        # SECOND COLUMN of h_splittier holds controlx boxes + mz plot
        # #######################

        v_splitter2 = QSplitter(self)
        v_splitter2.setOrientation(Qt.Vertical)

        v_splitter2.addWidget(self.image_scaling_widget)
        v_splitter2.addWidget(self.spectra_selector_widget)
        v_splitter2.addWidget(self.view_range_widget)
        v_splitter2.addWidget(self.history_list)
        v_splitter2.addWidget(self.mz_plotter)

        v_splitter2.setStretchFactor(0, 0)
        v_splitter2.setStretchFactor(1, 0)
        v_splitter2.setStretchFactor(2, 0)
        v_splitter2.setStretchFactor(3, 0)
        v_splitter2.setStretchFactor(4, 1)

        h_splitter.addWidget(v_splitter2)
        h_splitter.setStretchFactor(1, 1)

        # THIRD COLUMN of h_splittier holds control table + buttons
        # ##########################
        if self.table:
            frame = QFrame(self)
            layout = QVBoxLayout(frame)
            frame.setLayout(layout)
            layout.addWidget(self.table_widget)

            button_row_layout = QHBoxLayout(frame)
            button_row_layout.addWidget(self.select_all_peaks)
            button_row_layout.addWidget(self.unselect_all_peaks)
            button_row_layout.addWidget(self.done_button)

            layout.addLayout(button_row_layout)
            h_splitter.addWidget(frame)
            h_splitter.setStretchFactor(2, 2)

        outer_layout.addWidget(h_splitter)
        self.setLayout(outer_layout)
        outer_layout.setStretch(1, 99)

    def connect_signals_and_slots(self):
        self.image_scaling_widget.USE_LOG_SCALE.connect(self.use_logscale)
        self.image_scaling_widget.GAMMA_CHANGED.connect(self.gamma_changed)

        self.image_scaling_widget.IMIN_CHANGED.connect(self.set_image_min)
        self.image_scaling_widget.IMAX_CHANGED.connect(self.set_image_max)

        self.spectra_selector_widget.MS_LEVEL_CHOSEN.connect(self.ms_level_chosen)
        self.spectra_selector_widget.PRECURSOR_RANGE_CHANGED.connect(
            self.set_precursor_range
        )

        self.view_range_widget.RANGE_CHANGED.connect(self.update_all_plots)

        self.history_list.activated.connect(self.history_item_selected)

        self.peakmap_plotter.VIEW_RANGE_CHANGED.connect(self.peakmap_view_range_changed)
        self.eic_plotter.VIEW_RANGE_CHANGED.connect(self.eic_view_range_changed)
        self.mz_plotter.VIEW_RANGE_CHANGED.connect(self.mz_view_range_changed)

        self.peakmap_plotter.KEY_LEFT.connect(self.user_pressed_left_key_in_plot)
        self.peakmap_plotter.KEY_RIGHT.connect(self.user_pressed_right_key_in_plot)
        self.peakmap_plotter.KEY_BACKSPACE.connect(
            self.user_pressed_backspace_key_in_plot
        )
        self.peakmap_plotter.KEY_END.connect(self.user_pressed_end_key_in_plot)
        self.peakmap_plotter.CURSOR_MOVED.connect(self.cursor_moved_in_plot)
        self.eic_plotter.CURSOR_MOVED.connect(self.eic_cursor_moved)
        self.mz_plotter.CURSOR_MOVED.connect(self.mz_cursor_moved)

        if self.table is not None:
            self.table_widget.verticalHeader().sectionClicked.connect(self.row_selected)
            self.table_widget.itemClicked.connect(self.cell_clicked)

            self.select_all_peaks.pressed.connect(self.select_all_peaks_button_pressed)
            self.unselect_all_peaks.pressed.connect(
                self.unselect_all_peaks_button_pressed
            )

            self.done_button.pressed.connect(self.done_button_pressed)

            def key_release_handler(evt):
                tw = self.table_widget
                active_rows = set(
                    ix.row() for ix in tw.selectionModel().selection().indexes()
                )
                if active_rows:
                    row = active_rows.pop()
                    if evt.key() in (Qt.Key_Up, Qt.Key_Down):
                        tw.selectRow(row)
                        tw.verticalHeader().sectionClicked.emit(row)
                        return
                return QTableWidget.keyPressEvent(tw, evt)

            self.table_widget.keyReleaseEvent = key_release_handler

    def cursor_moved_in_plot(self, rt, mz):
        self.eic_plotter.set_cursor_pos(rt)
        self.mz_plotter.set_cursor_pos(mz)

    def eic_cursor_moved(self, rt):
        self.peakmap_plotter.set_cursor_rt(rt)

    def eic_view_range_changed(self, rtmin, rtmax):
        """
        we want to avoid the loop   EIC_RANGE_CHANGED -> VIEW_RANGE_CHANGED ->
        EIC_RANGE_CHANGED and we do not want to fully block emitting of
        VIEW_RANGE_CHANGED.  so self.peakmap_plotter.blockSignals() does not work here,
        instead we "cut" the last connection here:
        """
        mzmin, mzmax, *_ = self.mz_plotter.get_limits()
        self.update_all_plots(rtmin, rtmax, mzmin, mzmax)

    def mz_view_range_changed(self, mzmin, mzmax):
        """
        and we do not want to fully block emitting of VIEW_RANGE_CHANGED.
        we want to avoid the loop  MZ_RANGE_CHANGED -> VIEW_RANGE_CHANGED ->
        MZ_RANGE_CHANGED so self.peakmap_plotter.blockSignals() does not work here,
        instead we "cut" the last connection here:
        """
        rtmin, rtmax, *_ = self.eic_plotter.get_limits()
        self.update_all_plots(rtmin, rtmax, mzmin, mzmax)

    def mz_cursor_moved(self, mz):
        self.peakmap_plotter.set_cursor_mz(mz)

    def peakmap_view_range_changed(self, rtmin, rtmax, mzmin, mzmax):
        self.update_all_plots(rtmin, rtmax, mzmin, mzmax)
        self.history.new_head((rtmin, rtmax, mzmin, mzmax))
        self.update_history_entries()

    def set_image_min(self, value):
        self.peakmap_plotter.set_imin(value)
        self.peakmap_plotter.replot()

    def set_image_max(self, value):
        self.peakmap_plotter.set_imax(value)
        self.peakmap_plotter.replot()

    def _prepare_plotting_data(self, rtmin, rtmax, mzmin, mzmax):
        data = [
            (
                0,
                self.peakmap,
                rtmin,
                rtmax,
                mzmin,
                mzmax,
                "1" if self.dual_mode else None,
            )
        ]
        if self.dual_mode:
            data.append((0, self.peakmap2, rtmin, rtmax, mzmin, mzmax, "2"))

        return data

    def update_eic_plotter(self, rtmin, rtmax, mzmin, mzmax):
        data = self._prepare_plotting_data(rtmin, rtmax, mzmin, mzmax)
        for _ in self.eic_plotter.plot_eics_iter(data, [], [], [], background=False):
            pass

        self.eic_plotter.reset_rt_limits()
        self.eic_plotter.replot()
        self.view_range_widget.set_view_range(rtmin, rtmax, mzmin, mzmax)

    def update_mz_plotter(self, rtmin, rtmax, mzmin, mzmax):
        data = self._prepare_plotting_data(rtmin, rtmax, mzmin, mzmax)
        for _ in self.mz_plotter.plot_peaks_iter(data, background=False):
            pass
        self.mz_plotter.set_mz_limits(mzmin=mzmin, mzmax=mzmax)
        self.mz_plotter.replot()
        self.view_range_widget.set_view_range(rtmin, rtmax, mzmin, mzmax)

    def _handle_history_action(self, action):
        window = action()
        if window is not None:
            rtmin, rtmax, mzmin, mzmax = window
            self.update_all_plots(rtmin, rtmax, mzmin, mzmax)
            self.update_history_entries()

    def update_all_plots(self, rtmin, rtmax, mzmin, mzmax):
        if rtmin < self.rtmin:
            rtmin = self.rtmin
        if rtmax > self.rtmax:
            rtmax = self.rtmax
        if mzmin < self.mzmin:
            mzmin = self.mzmin
        if mzmax > self.mzmax:
            mzmax = self.mzmax
        rtmin, rtmax = sorted((rtmin, rtmax))
        mzmin, mzmax = sorted((mzmin, mzmax))
        self.update_eic_plotter(rtmin, rtmax, mzmin, mzmax)
        self.update_mz_plotter(rtmin, rtmax, mzmin, mzmax)
        self.peakmap_plotter.set_limits(rtmin, rtmax, mzmin, mzmax)

    def user_pressed_left_key_in_plot(self):
        self._handle_history_action(self.history.go_back)

    def user_pressed_right_key_in_plot(self):
        self._handle_history_action(self.history.go_forward)

    def user_pressed_backspace_key_in_plot(self):
        self._handle_history_action(self.history.go_to_beginning)

    def user_pressed_end_key_in_plot(self):
        self._handle_history_action(self.history.go_to_end)

    def history_item_selected(self, index):
        self._handle_history_action(
            lambda index=index: self.history.set_position(index)
        )

    @protect_signal_handler
    def do_save(self, *_):
        pix = self.peakmap_plotter.paint_pixmap()
        while True:
            path = ask_for_save(
                self.last_used_directory_for_save,
                caption="Save Image",
                extensions=("png", "PNG"),
            )
            if path is None:
                break
            __, ext = os.path.splitext(path)
            if ext not in (".png", ".PNG"):
                QMessageBox.warning(self, "Warning", "wrong/missing extension '.png'")
            else:
                self.last_used_directory_for_save = os.path.dirname(path)
                pix.save(path)
                break
        return

    def _do_load(self, title):
        path = ask_for_single_file(
            self.last_used_directory_for_load,
            caption=title,
            extensions=("mzML", "mzData", "mzXML"),
        )
        if path is not None:
            self.last_used_directory_for_load = os.path.dirname(path)
            return PeakMap.load(path)

    @protect_signal_handler
    def do_load(self, *_):
        pm = self._do_load("Load Peakmap")
        if pm is not None:
            self.setup_data(pm)

    @protect_signal_handler
    def do_load_yellow(self, *_):
        pm = self._do_load("Load Yellow Peakmap")
        if pm is not None:
            self.setup_data(pm)

    @protect_signal_handler
    def do_load_blue(self, *_):
        pm2 = self._do_load("Load Blue Peakmap")
        if pm2 is not None:
            self.setup_data(self.full_pm, pm2)

    @protect_signal_handler
    def select_all_peaks_button_pressed(self):
        for row in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row, 0)
            item.setCheckState(Qt.Checked)

    @protect_signal_handler
    def unselect_all_peaks_button_pressed(self):
        for row in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row, 0)
            item.setCheckState(Qt.Unchecked)

    @protect_signal_handler
    def done_button_pressed(self):
        self.ok_rows[:] = [
            i
            for i in range(len(self.table))
            if self.table_widget.item(i, 0).checkState() == Qt.Checked
        ]
        self.accept()

    @protect_signal_handler
    def row_selected(self, row_idx):
        row = self.table.getValues(self.table.rows[row_idx])
        needed = ["rtmin", "rtmax", "mzmin", "mzmax"]
        if all(n in row for n in needed):
            rtmin, rtmax, mzmin, mzmax = [row.get(ni) for ni in needed]
            self.peakmap_plotter.set_limits(rtmin, rtmax, mzmin, mzmax)
        else:
            needed = ["mzmin", "mzmax"]
            if all(n in row for n in needed):
                mzmin, mzmax = [row.get(ni) for ni in needed]
                self.peakmap_plotter.set_limits(self.rtmin, self.rtmax, mzmin, mzmax)

    @protect_signal_handler
    def cell_clicked(self, item):
        row = item.row()
        self.table_widget.selectRow(row)
        self.table_widget.verticalHeader().sectionClicked.emit(row)

    def update_history_entries(self):
        self.history_list.clear()
        for item in self.history.items:
            rtmin, rtmax, mzmin, mzmax = item
            str_item = "%10.5f .. %10.5f %6.2fm...%6.2fm " % (
                mzmin,
                mzmax,
                rtmin / 60.0,
                rtmax / 60.0,
            )
            self.history_list.addItem(str_item)

        self.history_list.setCurrentIndex(self.history.position)

    @protect_signal_handler
    def use_logscale(self, is_log):
        self.peakmap_plotter.set_logarithmic_scale(is_log)
        self.peakmap_plotter.replot()

    @protect_signal_handler
    def ms_level_chosen(self, previous_ms_level, new_ms_level):
        if new_ms_level != previous_ms_level:
            self.current_ms_level = new_ms_level
            self.process_peakmap(new_ms_level)
            self.peakmap_plotter.set_peakmaps(self.peakmap, self.peakmap2)
            self.peakmap_plotter.replot()
            self.plot_peakmap()
            self.update_all_plots(self.rtmin, self.rtmax, self.mzmin, self.mzmax)

    @protect_signal_handler
    def set_precursor_range(self, pre_mz_min, pre_mz_max):
        self.process_peakmap(self.current_ms_level, pre_mz_min, pre_mz_max)
        self.peakmap_plotter.set_peakmaps(self.peakmap, self.peakmap2)
        self.peakmap_plotter.replot()
        self.plot_peakmap()
        self.update_all_plots(self.rtmin, self.rtmax, self.mzmin, self.mzmax)

    @protect_signal_handler
    def gamma_changed(self, value):
        self.peakmap_plotter.set_gamma(value)
        self.peakmap_plotter.replot()

    def plot_peakmap(self):
        self.peakmap_plotter.set_limits(self.rtmin, self.rtmax, self.mzmin, self.mzmax)


def inspect(peakmap, peakmap2=None, table=None, modal=True, parent=None, window=None):
    """
    allows the visual inspection of a peakmap
    """

    if len(peakmap) == 0:
        raise Exception("empty peakmap")

    from emzed_gui import qapplication

    app = qapplication()
    win = PeakMapExplorer(parent=parent)
    win.setup(peakmap, peakmap2, table, window)

    if modal:
        win.setWindowModality(Qt.WindowModal)
        win.show()
        win.raise_()
        win.activateWindow()
        win.exec_()
        return win.ok_rows
    else:
        win.setWindowModality(Qt.NonModal)
        win.show()
        win.raise_()

    del app
