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


import types

import numpy as np
from guiqwt.builder import make
from guiqwt.events import KeyEventMatch, MoveHandler, QtDragHandler
from guiqwt.label import ObjectInfo
from guiqwt.plot import CurveWidget, PlotManager
from guiqwt.shapes import Marker, SegmentShape
from guiqwt.tools import InteractiveTool
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from qwt import QwtScaleDraw, QwtText

from emzed_gui.configs import (
    add_alpha,
    change_lightness,
    config_for_spectrum,
    get_color,
)
from emzed_gui.optimized import sample_peaks

from .config import setupCommonStyle
from .modified_guiqwt import (
    ExtendedCurvePlot,
    ImprovedPanHandler,
    ImprovedZoomHandler,
    LeaveHandler,
    PositiveValuedCurvePlot,
    make_unselectable_curve,
    patch_inner_plot_object,
    protect_signal_handler,
)


class MzCursorInfo(ObjectInfo):
    def __init__(self, marker, line):
        ObjectInfo.__init__(self)
        self.marker = marker
        self.line = line

    def get_text(self):
        mz, ii = self.marker.xValue(), self.marker.yValue()
        txt = "mz=%.6f<br/>I=%.1e" % (mz, ii)
        if self.line.isVisible():
            _, _, mz2, ii2 = self.line.get_rect()
            mean = (mz + mz2) / 2.0
            # to avoid zero division:
            if ii == 0:
                ii == 1
            txt += "<br/><br/>dmz=%.6f<br/>rI=%.3e<br/>mean=%.6f" % (
                mz2 - mz,
                ii2 / ii,
                mean,
            )

        return "<pre>%s</pre>" % txt


class MzPlottingWidget(CurveWidget):
    def __init__(self, parent=None, show_legend=True):
        super(MzPlottingWidget, self).__init__(parent, xlabel="m/z", ylabel="I")

        patch_inner_plot_object(self, MzPlot)

        # autoreplot makes updates slower, instead we call .replot when needed
        self.plot.setAutoReplot(False)

        def label(self, x):
            # label with full precision:
            return QwtText(str(round(x, 10)))

        a = QwtScaleDraw()
        a.label = types.MethodType(label, self.plot)
        self.plot.setAxisScaleDraw(self.plot.xBottom, a)

        self.pm = PlotManager(self)
        self.pm.add_plot(self.plot)

        t = self.pm.add_tool(MzSelectionTool)
        self.pm.set_default_tool(t)
        t.activate()

        # setting z values below later makes add_item a bit faster

        marker = Marker(label_cb=self.plot.label_info, constraint_cb=self.plot.on_plot)
        marker.setZ(0)
        marker.attach(self.plot)

        if show_legend:
            legend = make.legend("TL")
            legend.setZ(1)

        else:
            legend = None

        line = make_measurement_line()
        line.setVisible(0)
        line.setZ(2)

        setupCommonStyle(line, marker)
        line.shapeparam.line.color = "#555555"
        line.shapeparam.update_shape(line)

        label = make.info_label("TR", [MzCursorInfo(marker, line)], title=None)
        label.labelparam.label = ""
        label.labelparam.font.size = 12
        label.labelparam.update_label(label)
        label.setZ(3)

        self.marker = marker
        self.legend = legend
        self.label = label
        self.line = line

    def set_zoom_limits(self, mzmin, mzmax):
        self.plot.overall_x_min = mzmin
        self.plot.overall_x_max = mzmax

    def get_limits(self):
        return self.plot.get_plot_limits()

    def plot_peaks_iter(self, peak_data, background=True):
        if not peak_data:
            return

        self.clear()
        self.plot.add_item(self.marker)
        if self.legend:
            self.plot.add_item(self.legend)
        self.plot.add_item(self.label)
        self.plot.add_item(self.line)

        for _ in self.plot.plot_peaks(peak_data, background):
            yield

    def plot_spectra(self, collected_peaks, labels):
        assert len(collected_peaks) == len(labels), (collected_peaks, labels)
        if not collected_peaks:
            return

        self.clear()
        self.plot.add_item(self.marker)
        if self.legend:
            self.plot.add_item(self.legend)
        self.plot.add_item(self.label)
        self.plot.add_item(self.line)
        self.plot.plot_spectra(collected_peaks, labels)

    def set_cursor_pos(self, mz):
        self.plot.set_mz(mz)

    def resetAxes(self):
        self.plot.reset_x_limits()

    def reset_mz_limits(self, fac=0):
        self.plot.reset_x_limits(fac)

    def set_mz_limits(self, mzmin, mzmax):
        self.plot.set_x_limits(mzmin, mzmax)

    def reset(self):
        self.clear()
        self.replot()

    def clear(self):
        self.plot.del_all_items()

    def replot(self):
        mzmin, mzmax, __, __ = self.plot.get_plot_limits()
        self.plot.update_background_curves(mzmin, mzmax)
        self.plot.replot()

    def set_visible(self, visible):
        self.plot.setVisible(visible)

    def updateAxes(self):
        self.plot.updateAxes()

    def shrink_and_replot(self, mzmin, mzmax):
        self.plot.update_plot_xlimits(mzmin, mzmax)
        self.plot.reset_y_limits()
        self.plot.replot()


class MzPlot(PositiveValuedCurvePlot, ExtendedCurvePlot):
    """modifications:
    - showing marker at peak next to mouse cursor
    - mouse drag handling for measuring distances between peaks
    - showing information about current peak and distances if in drag mode
    """

    def _init_patched_object(self):
        self.peakmap_ranges = ()
        self.image_plot = None
        self.visible_peaks = ()
        self.current_peak_data = ()

    def label_info(self, x, y):
        # label next to cursor turned off:
        return None

    @protect_signal_handler
    def do_space_pressed(self, filter, evt):
        marker = self.get_unique_item(Marker)
        if marker is None:
            return
        mz = marker.xValue()

        self.update_plot_xlimits(mz - 0.1, mz + 0.1)

    @protect_signal_handler
    def on_plot(self, x, y):
        """callback for marker: determine marked point based on cursors coordinates"""
        self.current_peak = self.next_peak_to(x, y)

        self.CURSOR_MOVED.emit(float(self.current_peak[0]))
        return self.current_peak

    def set_mz(self, mz):
        # set cursor position
        mz, ii = self.next_peak_to(mz)
        if mz is not None and ii is not None:
            marker = self.get_unique_item(Marker)
            if marker is None:
                return
            marker.setValue(mz, ii)  # avoids sending signal
            self.replot()

    def set_visible_peaks(self, peaks):
        if peaks is None or len(peaks) == 0:
            peaks = np.zeros((0, 2))
        self.visible_peaks = peaks

    def set_current_peak_data(self, peak_data):
        self.current_peak_data = peak_data

    def reset_x_limits(self, fac=0):
        if self.visible_peaks is None or not len(self.visible_peaks):
            return

        mzmin = np.min(self.visible_peaks[:, 0])
        mzmax = np.max(self.visible_peaks[:, 0])

        iimax = np.max(self.visible_peaks[:, 1])

        w = mzmax - mzmin
        mzmin = max(0, mzmin - fac * w)
        mzmax += fac * w

        self.update_plot_xlimits(mzmin, mzmax)
        self.update_plot_ylimits(0, iimax * 1.1)

    def set_x_limits(self, mzmin, mzmax, fac=0):
        w = mzmax - mzmin
        mzmin = max(0, mzmin - fac * w)
        mzmax += fac * w

        self.update_plot_xlimits(mzmin, mzmax)

        if self.visible_peaks is not None and len(self.visible_peaks):
            iimax = np.max(self.visible_peaks[:, 1])
            self.update_plot_ylimits(0, iimax * 1.1)

    def next_peak_to(self, mz, ii=None):
        visible_peaks = self.visible_peaks.copy()
        if self.background_peaks is not None:
            visible_peaks = np.vstack((visible_peaks, self.background_peaks))
        if len(visible_peaks) == 0:
            return mz, ii
        if ii is None:
            distances = (visible_peaks[:, 0] - mz) ** 2
            imin = np.argmin(distances)
        else:
            peaks = visible_peaks - np.array((mz, ii))

            # scale according to zooms axis proportions:
            mzmin, mzmax, iimin, iimax = self.get_plot_limits()

            # avoid division by zeros:
            if mzmax == mzmin or iimax == iimin:
                return mz, ii
            peaks /= np.array((mzmax - mzmin, iimax - iimin))
            # find minimal distance
            distances = peaks[:, 0] ** 2 + peaks[:, 1] ** 2
            imin = np.argmin(distances)
        return visible_peaks[imin]

    @protect_signal_handler
    def do_move_marker(self, evt):
        marker = self.get_unique_item(Marker)
        if marker is not None:
            marker.move_local_point_to(0, evt.pos())
            marker.setVisible(True)
            self.replot()

    @protect_signal_handler
    def start_drag_mode(self, filter_, evt):
        mz = self.invTransform(self.xBottom, evt.x())
        ii = self.invTransform(self.yLeft, evt.y())
        self.start_coord = self.next_peak_to(mz, ii)

    @protect_signal_handler
    def move_in_drag_mode(self, filter_, evt):
        mz = self.invTransform(self.xBottom, evt.x())
        ii = self.invTransform(self.yLeft, evt.y())
        current_coord = self.next_peak_to(mz, ii)

        line = self.get_unique_item(SegmentShape)
        if line is None:
            return
        line.set_rect(
            self.start_coord[0], self.start_coord[1], current_coord[0], current_coord[1]
        )
        line.setVisible(1)

        self.replot()

    def cursor_leaves(self):
        marker = self.get_unique_item(Marker)
        if marker is not None:
            marker.setVisible(False)
            self.replot()

    @protect_signal_handler
    def stop_drag_mode(self, filter_, evt):
        line = self.get_unique_item(SegmentShape)
        if line is not None:
            line.setVisible(0)
            self.replot()

    def plot_spectra(self, spectra_collection, labels):
        spectra_grouped = {}
        for (idx, spectrum), label in zip(spectra_collection, labels):
            spectra_grouped.setdefault(idx, []).append((spectrum.peaks, label))

        self.sticks = []
        collected_peaks = []
        for i, (idx, spectra) in enumerate(spectra_grouped.items()):
            color = get_color(i)
            for peaks, label in spectra:
                curve = make_unselectable_curve(
                    [], [], title=label, **config_for_spectrum(add_alpha(color, 120))
                )
                collected_peaks.append(peaks)
                curve.set_data(peaks[:, 0], peaks[:, 1])
                self.add_item(curve)
                self.sticks.append(curve)
                color = change_lightness(color, 0.7)

        self.set_visible_peaks(np.vstack(collected_peaks))
        self.set_current_peak_data([])
        self.reset_x_limits(fac=0.1)

    def plot_peaks(self, peak_data, show_background_peaks):
        visible_peaks = []
        self.sticks = []
        self.background_peaks_curve = None
        self.background_peaks = None

        # "dataless" background sticks for zooming
        if show_background_peaks:
            curve = make_unselectable_curve(
                np.array([]),
                np.array([]),
                curvestyle="Sticks",
                title="other",
                linewidth=1,
                color="#909090",
            )

            self.add_item(curve)
            self.background_peaks_curve = curve

        peaks_grouped = {}
        for idx, *peaks in peak_data:
            peaks_grouped.setdefault(idx, []).append(peaks)

        for i, (idx, peaks) in enumerate(peaks_grouped.items()):
            color = get_color(i)
            for pm, rtmin, rtmax, mzmin, mzmax, label in peaks:
                ms_level = min(pm.ms_levels())
                peaks = sample_peaks(pm, rtmin, rtmax, mzmin, mzmax, 1000, ms_level)
                visible_peaks.append(peaks)

                config = config_for_spectrum(add_alpha(color, 120))
                curve = make_unselectable_curve(
                    np.array([]), np.array([]), title=label, **config
                )

                curve.set_data(peaks[:, 0], peaks[:, 1])
                visible_peaks.append(peaks)
                self.add_item(curve)
                self.sticks.append(curve)

                color = change_lightness(color, 1.3)
                yield

        if visible_peaks:
            self.set_visible_peaks(np.vstack(visible_peaks))
        self.set_current_peak_data(peak_data)

    def update_background_curves(self, mzmin, mzmax):
        if not self.current_peak_data or self.background_peaks_curve is None:
            return

        peaks = np.vstack(
            [
                sample_peaks(pm, rtmin, rtmax, mzmin, mzmax, 1000, min(pm.ms_levels()))
                for (_, pm, rtmin, rtmax, _, _, _) in self.current_peak_data
            ]
        )

        curve = self.background_peaks_curve
        curve.set_data(peaks[:, 0], peaks[:, 1])
        self.background_peaks = peaks


class MzSelectionTool(InteractiveTool):
    """
    modified event handling:
        - space and backspac keys trigger handlers in baseplot
        - calling handlers for dragging with mouse
    """

    TITLE = "mZ Selection"
    ICON = "selection.png"
    CURSOR = Qt.CrossCursor

    def setup_filter(self, baseplot):
        filter = baseplot.filter
        # Initialisation du filtre
        start_state = filter.new_state()
        # Bouton gauche :

        # start_state = filter.new_state()
        handler = QtDragHandler(filter, Qt.LeftButton, start_state=start_state)

        filter.add_event(
            start_state,
            KeyEventMatch((Qt.Key_Space,)),
            baseplot.do_space_pressed,
            start_state,
        )
        filter.add_event(
            start_state,
            KeyEventMatch((Qt.Key_Backspace, Qt.Key_Escape)),
            baseplot.backspace_pressed,
            start_state,
        )

        handler.SIG_MOVE.connect(baseplot.move_in_drag_mode)
        handler.SIG_START_TRACKING.connect(baseplot.start_drag_mode)
        handler.SIG_STOP_NOT_MOVING.connect(baseplot.stop_drag_mode)
        handler.SIG_STOP_MOVING.connect(baseplot.stop_drag_mode)
        self.handler = handler

        # Bouton du milieu
        ImprovedPanHandler(
            filter, Qt.MidButton, start_state=start_state, call_stop_moving_handler=True
        )
        ImprovedPanHandler(
            filter,
            Qt.LeftButton,
            mods=Qt.AltModifier,
            start_state=start_state,
            call_stop_moving_handler=True,
        )

        # Bouton droit
        ImprovedZoomHandler(
            filter,
            Qt.RightButton,
            start_state=start_state,
            call_stop_moving_handler=True,
        )
        ImprovedZoomHandler(
            filter,
            Qt.LeftButton,
            mods=Qt.ControlModifier,
            start_state=start_state,
            call_stop_moving_handler=True,
        )

        # Autres (touches, move)
        MoveHandler(filter, start_state=start_state)
        MoveHandler(filter, start_state=start_state, mods=Qt.ShiftModifier)
        MoveHandler(filter, start_state=start_state, mods=Qt.AltModifier)

        LeaveHandler(filter, start_state=start_state)
        return start_state


def make_measurement_line():
    line = make.segment(0, 0, 0, 0)
    line.__class__ = MesaurementLine
    return line


class MesaurementLine(SegmentShape):
    """
    This is plottet as a line
    modifications are:
        - no point int the middle of the line
    """

    def draw(self, painter, xMap, yMap, canvasRect):
        # code copied and rearanged such that line has antialiasing,
        # but symbols have not.
        pen, brush, symbol = self.get_pen_brush(xMap, yMap)

        painter.setPen(pen)
        painter.setBrush(brush)
        painter.setRenderHint(QPainter.Antialiasing)

        points = self.transform_points(xMap, yMap)
        if self.ADDITIONNAL_POINTS:
            shape_points = points[: -self.ADDITIONNAL_POINTS]
            other_points = points[-self.ADDITIONNAL_POINTS :]
        else:
            shape_points = points
            other_points = []

        # skip painting middle point which is last in the points list:
        for point in points[:2]:
            symbol.drawSymbol(painter, point.toPoint())

        if self.closed:
            painter.drawPolygon(shape_points)
        else:
            painter.drawPolyline(shape_points)

        if self.LINK_ADDITIONNAL_POINTS and other_points:
            pen2 = painter.pen()
            pen2.setStyle(Qt.DotLine)
            painter.setPen(pen2)
            painter.drawPolyline(other_points)
