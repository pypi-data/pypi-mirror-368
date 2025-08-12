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


import numpy as np
from guiqwt.builder import make
from guiqwt.curve import CurveItem
from guiqwt.events import KeyEventMatch, MoveHandler, ObjectHandler
from guiqwt.label import ObjectInfo
from guiqwt.plot import CurveWidget, PlotManager
from guiqwt.shapes import Marker, PolygonShape, XRangeSelection
from guiqwt.tools import InteractiveTool
from PyQt5.QtCore import QObject, Qt, pyqtSignal

from emzed_gui.configs import (
    add_alpha,
    change_lightness,
    config_for_background_eic,
    config_for_eic,
    config_for_fitted_peakshape_model,
    get_color,
)
from emzed_gui.helpers import (
    formatSeconds,
    protect_signal_handler,
    set_rt_formatting_on_x_axis,
    timethis,
)

from .modified_guiqwt import (
    ExtendedCurvePlot,
    ImprovedPanHandler,
    ImprovedZoomHandler,
    LeaveHandler,
    PositiveValuedCurvePlot,
    make_unselectable_curve,
    patch_inner_plot_object,
)


def create_borderless_polygon(points, config):
    shape = PolygonShape(points, closed=True)
    shape.set_selectable(False)
    shape.set_movable(False)
    shape.set_resizable(False)
    shape.set_rotatable(False)
    setup_shape_param(shape, config)
    # setup_shape_param(shape, {"fill.alpha": 0.3, "fill.color": color,
    #'shade': .75, 'linewidth': 3})
    # paint no border:
    # shape.pen = QPen(Qt.NoPen)
    return shape


def create_closed_shape(rts, iis, config):
    rts = np.array(rts)
    iis = np.array(iis)
    perm = np.argsort(rts)
    rts = rts[perm][:, None]  # column vector
    iis = iis[perm][:, None]
    points = np.hstack((rts, iis))  # we need two columns not two rows
    if not len(points):
        return None
    rt0 = points[0][0]
    rt1 = points[-1][0]
    # close polygon:
    points = np.vstack(((rt0, 0), points, (rt1, 0)))
    shape = create_borderless_polygon(points, config)
    return shape


def _setup_item(param_item, settings):
    for name, value in list(settings.items()):
        sub_item = param_item
        sub_names = name.split(".")
        for field in sub_names[:-1]:
            sub_item = getattr(sub_item, field)
        setattr(sub_item, sub_names[-1], value)


def setup_label_param(item, settings):
    _setup_item(item.labelparam, settings)
    item.labelparam.update_label(item)


def setup_marker_param(item, settings):
    _setup_item(item.markerparam, settings)
    item.markerparam.update_marker(item)


def setup_shape_param(item, settings):
    _setup_item(item.shapeparam, settings)
    item.shapeparam.update_shape(item)


def getColor(i):
    colors = "bgrkm"
    return colors[i % len(colors)]


class RangeSelectionInfo(ObjectInfo):
    def __init__(self, range_):
        ObjectInfo.__init__(self)
        self.range_ = range_

    def get_text(self):
        rtmin, rtmax = sorted(self.range_.get_range())
        if rtmin != rtmax:
            return "<pre>rt: %s ... %s</pre>" % (
                formatSeconds(rtmin),
                formatSeconds(rtmax),
            )
        else:
            return "<pre>rt: %s</pre>" % formatSeconds(rtmin)


class RtCursorInfo(ObjectInfo):
    def __init__(self, marker):
        ObjectInfo.__init__(self)
        self.marker = marker

    def get_text(self):
        rt = self.marker.xValue()
        txt = "<pre>%.2fm</pre>" % (rt / 60.0)
        return txt


class EicPlottingWidget(CurveWidget):
    SELECTED_RANGE_CHANGED = pyqtSignal(float, float)

    def __init__(self, parent=None, with_range=True):
        super(EicPlottingWidget, self).__init__(parent, ylabel="I")
        patch_inner_plot_object(self, EicPlot)
        self._with_range = with_range
        self._setup_plot()

        # autoreplot makes updates slower, instead we call .replot when needed
        self.plot.setAutoReplot(False)

    def enable_range(self, flag):
        self._with_range = flag

    def _setup_plot(self):
        self.pm = PlotManager(self)
        self.pm.add_plot(self.plot)

        t = self.pm.add_tool(RtSelectionTool)
        t.activate()
        self.pm.set_default_tool(t)

        self._setup_cursor()
        self._setup_range_selector()
        self._setup_label()
        self._setup_axes()

    def _setup_cursor(self):
        marker = Marker(label_cb=self.plot.label_info, constraint_cb=self.plot.on_plot)
        marker.set_selectable(False)
        marker.rts = [0]
        setup_marker_param(
            marker,
            {
                "symbol.size": 0,
                "symbol.alpha": 0.0,
                "sel_symbol.size": 0,
                "sel_symbol.alpha": 0.0,
                "line.color": "#909090",
                "line.width": 1.0,
                "line.style": "SolidLine",
                "sel_line.color": "#909090",
                "sel_line.width": 1.0,
                "sel_line.style": "SolidLine",
                "markerstyle": "VLine",
            },
        )
        marker.attach(self.plot)
        self.marker = marker

        self._setup_cursor_info(marker)

    def _setup_cursor_info(self, marker):
        self.cursor_info = RtCursorInfo(marker)

    def _setup_range_selector(self):
        if not self._with_range:
            self.range_ = None
            self.legend_ = None
            self.info_box_ = None
            return

        self.range_ = SnappingRangeSelection(0, 0)

        # you have to register item to plot before you can register
        # _range_selection_handler:
        self.plot.add_item(self.range_)
        self.range_.SELECTED_RANGE_CHANGED.connect(self._range_selection_handler)

        self.legend_ = make.info_label(
            "TR", [RangeSelectionInfo(self.range_)], title=None
        )
        setup_label_param(self.legend_, {"label": "", "font.size": 12})
        self.plot.add_item(self.legend_)

    def _setup_label(self):
        label = make.info_label("T", [self.cursor_info], title=None)
        setup_label_param(
            label, {"label": "", "font.size": 12, "border.color": "#ffffff"}
        )
        self.label = label

    def _setup_axes(self):
        # render tic labels in modfied format:
        set_rt_formatting_on_x_axis(self.plot)
        self.plot.set_axis_title("bottom", "rt")

    def set_cursor_pos(self, rt):
        self.plot.set_rt(rt)

    def set_zoom_limits(self, rtmin, rtmax):
        self.plot.overall_x_min = rtmin
        self.plot.overall_x_max = rtmax

    def plot_eics_iter(
        self,
        peak_data,
        chromatograms,
        peak_shape_models,
        chromatogram_models,
        background=True,
    ):
        self.clear()
        self.plot.add_item(self.marker)
        if self.range_ is not None:
            self.plot.add_item(self.range_)
        if self.legend_ is not None:
            self.plot.add_item(self.legend_)

        rtmins, rtmaxs, iimaxs = [], [], []
        last_i = -1
        if peak_data:
            for last_i, rtmin, rtmax, iimax in self.plot.plot_eics(
                peak_data, peak_shape_models, background
            ):
                rtmins.append(rtmin)
                rtmaxs.append(rtmax)
                iimaxs.append(iimax)
                yield

        for rtmin, rtmax, iimax in self.plot.plot_ms_chromatograms(
            chromatograms, chromatogram_models, color_offset=last_i + 1
        ):
            rtmins.append(rtmin)
            rtmaxs.append(rtmax)
            iimaxs.append(iimax)
            yield

        self.plot._current_rtmin = min(rtmins)
        self.plot._current_rtmax = max(rtmaxs)
        self.plot._current_iimax = max(iimaxs)

        if self.range_ is not None:
            self.range_.set_range(
                self.plot._current_rtmin, self.plot._current_rtmax, block_signals=True
            )

        self.plot.replot()

    def clear(self):
        self.plot.del_all_items()

    def set_visible(self, visible):
        self.plot.setVisible(visible)

    def get_range_selection_limits(self):
        if self.range_ is None:
            return None, None
        return sorted((self.range_._min, self.range_._max))

    def set_range_selection_limits(self, xleft, xright, block_signals=False):
        if self.range_ is None:
            return
        timethis(self.range_.set_range)(xleft, xright, block_signals)

    def reset_intensity_limits(
        self, imin=None, imax=None, fac=1.1, rtmin=None, rtmax=None
    ):
        self.plot.reset_y_limits(imin, imax, fac, rtmin, rtmax)

    @protect_signal_handler
    def _range_selection_handler(self, left, right):
        min_, max_ = sorted((left, right))
        self.SELECTED_RANGE_CHANGED.emit(min_, max_)

    def set_rt_axis_limits(self, xmin, xmax):
        self.plot.update_plot_xlimits(xmin, xmax)

    def get_limits(self):
        return self.plot.get_plot_limits()

    def updateAxes(self):
        self.plot.updateAxes()

    def set_intensity_axis_limits(self, ymin, ymax):
        self.plot.update_plot_ylimits(ymin, ymax)

    def reset_rt_limits(self, fac=0):
        self.plot.reset_x_limits(fac)

    def reset_intensitiy_limits(
        self, i_min=None, i_max=None, fac=1.1, rt_min=None, rt_max=None
    ):
        self.plot.reset_y_limits(i_min, i_max, fac, rt_min, rt_max)

    def set_limit(self, ix, value):
        self.plot.set_limit(ix, value)

    def replot(self):
        rtmin, rtmax, __, __ = self.plot.get_plot_limits()
        self.plot.update_background_curves(rtmin, rtmax)
        self.plot.replot()

    def del_all_items(self):
        self.plot.del_all_items()

    def reset(self):
        """empties plot"""
        self.del_all_items()
        self.replot()

    def shrink_and_replot(self, rtmin, rtmax):
        self.set_rt_axis_limits(rtmin, rtmax)
        self.plot.reset_y_limits()
        self.plot.replot()


class EicPlot(PositiveValuedCurvePlot, ExtendedCurvePlot):
    """modified behavior:
    - space zooms to selected rt range
    - enter puts range marker to middle of currenct rt plot view
    - right crsr + left csrs + shift and alt modifiers move
      boundaries of selection tool
    """

    def _init_patched_object(self):
        self.x_values = None
        self.current_peak_data = []
        self.background_curves = []
        self._current_rtmin = self._current_rtmax = self._current_iimax = None

    @protect_signal_handler
    def do_space_pressed(self, filter, evt):
        """zoom to limits of snapping selection tool"""

        item = self.get_unique_item(SnappingRangeSelection)
        if item is None:
            return
        if item._min != item._max:
            min_neu = min(item._min, item._max)
            max_neu = max(item._min, item._max)
            range_ = max_neu - min_neu
            if range_ == 0.0:  # look strange in this case, so we zoom a little bit:
                mm = max_neu
                max_neu = mm * 1.1
                min_neu = mm * 0.9
            else:
                max_neu += 0.1 * range_
                min_neu -= 0.1 * range_
            self.update_plot_xlimits(min_neu, max_neu)

            yvals = self.seen_yvals(min_neu, max_neu)
            if yvals:
                ymax = max(yvals)
                if ymax > 0:
                    self.update_plot_ylimits(0, ymax * 1.1)

    @protect_signal_handler
    def do_enter_pressed(self, filter, evt):
        """set snapping selection tool to center of actual x-range"""

        xmin, xmax, _, _ = self.get_plot_limits()
        mid = (xmin + xmax) / 2.0

        item = self.get_unique_item(SnappingRangeSelection)
        if item is None:
            return

        # move_point_to always emits both limits, so we block the first signalling:
        item.set_range(mid, mid)
        filter.plot.replot()

    @protect_signal_handler
    def do_move_marker(self, evt):
        marker = self.get_unique_item(Marker)
        if marker is not None:
            marker.move_local_point_to(0, evt.pos())
            marker.setVisible(True)
            self.replot()

    def cursor_leaves(self):
        marker = self.get_unique_item(Marker)
        if marker is not None:
            marker.setVisible(False)
            self.replot()

    def move_selection_bounds(self, evt, filter_, selector):
        shift_pressed = evt.modifiers() & Qt.ShiftModifier
        alt_pressed = evt.modifiers() & Qt.AltModifier
        ctrl_pressed = evt.modifiers() & Qt.ControlModifier

        item = self.get_unique_item(SnappingRangeSelection)
        if item is None:
            return

        n_steps = 5 if ctrl_pressed else 1

        new_max = item._max
        new_min = item._min
        for _ in range(n_steps):
            if not alt_pressed:
                new_max = selector(item.get_neighbour_xvals(new_max))
                if new_max is None:
                    break
            if not shift_pressed:
                new_min = selector(item.get_neighbour_xvals(new_min))
                if new_min is None:
                    break

        if new_min is not None and new_max is not None:
            # move_point_to always emits both limits, so we block the first signalling:
            item.set_range(new_min, new_max)

        filter_.plot.replot()

    @protect_signal_handler
    def do_left_pressed(self, filter_, evt):
        self.move_selection_bounds(
            evt,
            filter_,
            lambda left_neighbour_right_neighbour: left_neighbour_right_neighbour[0],
        )

    @protect_signal_handler
    def do_right_pressed(self, filter_, evt):
        self.move_selection_bounds(
            evt,
            filter_,
            lambda left_neighbour_right_neighbour: left_neighbour_right_neighbour[1],
        )

    def label_info(self, x, y):
        # label next to cursor turned off:
        return None

    def set_x_values(self, x_values):
        self.x_values = np.array(x_values)

    def set_rt(self, rt):
        # sets cursor
        marker = self.get_unique_item(Marker)
        if marker is None:
            return
        marker.setXValue(rt)
        self.replot()

    @protect_signal_handler
    def on_plot(self, x, y):
        """callback for marker: determine marked point based on cursors coordinates"""
        x_values = self.x_values
        if x_values is None or len(x_values) == 0:
            self.CURSOR_MOVED.emit(x)
            return x, y
        distances = np.abs(x - x_values)
        imin = np.argmin(distances)
        self.current_peak = x_values[imin], 0
        self.CURSOR_MOVED.emit(x_values[imin])
        return self.current_peak

    def plot_ms_chromatograms(self, chromatograms, models, color_offset=0):
        if not chromatograms:
            return

        if not models:
            models = [None] * len(chromatograms)

        ms_chromatograms_grouped = {}
        for idx, rtmin, rtmax, ms_chromatogram, label in chromatograms:
            ms_chromatograms_grouped.setdefault(idx, []).append(
                (rtmin, rtmax, ms_chromatogram, label)
            )

        j = -1
        for i, (idx, chromatograms_in_group) in enumerate(
            ms_chromatograms_grouped.items()
        ):
            color = get_color(i + color_offset)
            for rtmin, rtmax, ms_chromatogram, label in chromatograms_in_group:
                j += 1
                rts = ms_chromatogram.rts
                iis = ms_chromatogram.intensities
                if not len(rts):
                    continue

                iimax = max(iis)

                title = label or ""
                config = dict(
                    linewidth=3, linestyle="DashLine", color=add_alpha(color, 120)
                )
                curve = make_unselectable_curve(rts, iis, title=title, **config)

                model = models[j]
                if model is not None:
                    config = config_for_fitted_peakshape_model(color)

                    rts, iis = model.graph()
                    shape = create_closed_shape(rts, iis, config)
                    if shape is not None:
                        self.add_item(shape)
                    rtmin, rtmax = model.rtmin, model.rtmax
                color = change_lightness(color, 1.3)
                self.add_item(curve)
                yield rtmin, rtmax, iimax

    def plot_eics(self, peak_data, models, background=True):
        background_curves = [None] * len(peak_data)

        if not models:
            models = [None] * len(peak_data)

        assert len(models) == len(peak_data)

        # group eics on same row -> same color
        eics_grouped = {}
        for idx, *data in peak_data:
            eics_grouped.setdefault(idx, []).append(data)

        j = -1
        for i, (idx, eics_grouped) in enumerate(eics_grouped.items()):
            color = get_color(i)
            for pm, rtmin, rtmax, mzmin, mzmax, label in eics_grouped:
                j += 1
                if not pm.ms_levels():
                    continue
                ms_level = min(pm.ms_levels())
                rts, iis = pm.chromatogram(mzmin, mzmax, rtmin, rtmax, ms_level)

                if not len(iis):
                    continue
                iimax = max(iis)

                if background:
                    config = config_for_background_eic(color)
                    background_curve = make_unselectable_curve(
                        np.array([]), np.array([]), **config
                    )
                    background_curves[i] = background_curve
                    self.add_item(background_curve)

                title = label or ""
                config = config_for_eic(add_alpha(color, 150))
                curve = make_unselectable_curve(rts, iis, title=title, **config)
                self.add_item(curve)
                yield i, rtmin, rtmax, iimax

                model = models[j]
                if model is not None:
                    config = config_for_fitted_peakshape_model(color)

                    rts, iis = model.graph()
                    shape = create_closed_shape(rts, iis, config)
                    if shape is not None:
                        self.add_item(shape)

                color = change_lightness(color, 1.3)

        self.set_current_peak_data(peak_data)
        self.background_curves = background_curves

    def set_current_peak_data(self, peak_data):
        self.current_peak_data = peak_data

    def reset_x_limits(self, fac=0):
        if self._current_rtmin is None or self._current_rtmax is None:
            return

        rtmin = self._current_rtmin
        rtmax = self._current_rtmax

        w = max(rtmax - rtmin, 1)

        rtmin = max(0, rtmin - fac * w)
        rtmax += fac * w

        self.update_plot_xlimits(rtmin, rtmax)
        self.update_plot_ylimits(0, 1.1 * self._current_iimax)

    def update_background_curves(self, rtmin, rtmax):
        if not self.current_peak_data or not self.background_curves:
            return

        for i, (_, pm, _, _, mzmin, mzmax, _) in enumerate(self.current_peak_data):
            ms_level = min(pm.ms_levels())
            rts, iis = pm.chromatogram(mzmin, mzmax, rtmin, rtmax, ms_level)
            if self.background_curves[i] is not None:
                self.background_curves[i].set_data(rts, iis)


class SnappingRangeSelection(XRangeSelection):
    """modification:
    - only limit bars can be moved
    - snaps to given rt-values which are in general not equally spaced
    """

    class _X(QObject):
        SELECTED_RANGE_CHANGED = pyqtSignal(float, float)

    def __init__(self, min_, max_):
        XRangeSelection.__init__(self, min_, max_)
        self._can_move = (
            False  # moving entire shape disabled, but handles are still movable
        )

        # we have to trick a bit because pyqtSignal must be attributes of a derived
        # class of QObject and adding QObject as an additional base class does not work
        # somehow:
        self._x = SnappingRangeSelection._X()
        self.SELECTED_RANGE_CHANGED = self._x.SELECTED_RANGE_CHANGED

        p = self.shapeparam
        p.fill = "#aaaaaa"
        p.line.color = "#888888"
        p.sel_line.color = "#888888"
        p.symbol.color = "gray"
        p.symbol.facecolor = "gray"
        p.symbol.alpha = 0.5
        p.sel_symbol.color = "gray"
        p.sel_symbol.facecolor = "gray"
        p.sel_symbol.alpha = 0.5
        p.sel_symbol.size = 8
        p.symbol.size = 8
        p.update_range(self)

    def get_xvals(self):
        xvals = []
        for item in self.plot().get_items():
            if isinstance(item, CurveItem):
                xvals.extend(np.array(item.get_data()[0]))
        return np.sort(np.unique(xvals))

    def set_range(self, xmin, xmax, block_signals=False):
        self.move_point_to(0, (xmin, 0), True)
        self.move_point_to(1, (xmax, 0), block_signals)

    def move_point_to(self, hnd, pos, block_signals=False):
        xvals = self.get_xvals()
        x, y = pos

        # modify pos to the next x-value
        # fast enough

        if len(xvals):
            imin = np.argmin(np.fabs(x - xvals))
            x = xvals[imin]

        if hnd == 0:
            # avoid signal handling:
            if self._min == x:
                return
            self._min = x
        elif hnd == 1:
            # avoid signal handling:
            if self._max == x:
                return
            self._max = x

        elif hnd == 2:
            move = x - (self._max + self._min) / 2
            new_min = self._min + move
            new_max = self._max + move
            if len(xvals):
                imin = np.argmin(np.fabs(new_min - xvals))
                new_min = xvals[imin]

                imin = np.argmin(np.fabs(new_max - xvals))
                new_max = xvals[imin]

            if self._min == new_min and self._max == new_max:
                # avoid signal handling
                return

            self._min = new_min
            self._max = new_max

        if not block_signals:
            self.SELECTED_RANGE_CHANGED.emit(self._min, self._max)

    def get_neighbour_xvals(self, x):
        """used for moving boundaries"""

        xvals = self.get_xvals()
        if not len(xvals):
            return x, None
        imin = np.argmin(np.fabs(x - xvals))
        if imin == 0:
            return None, xvals[1]
        if imin == len(xvals) - 1:
            return xvals[imin - 1], None
        return xvals[imin - 1], xvals[imin + 1]


class RtSelectionTool(InteractiveTool):
    """
    modified event handling:
    - enter, space, backspace, left crsr and right crsr keys trigger handlers in
    baseplot
    """

    TITLE = "Rt Selection"
    ICON = "selection.png"
    CURSOR = Qt.ArrowCursor

    def setup_filter(self, baseplot):
        filter = baseplot.filter
        # Initialisation du filtre
        start_state = filter.new_state()
        # Bouton gauche :
        ObjectHandler(filter, Qt.LeftButton, start_state=start_state)

        filter.add_event(
            start_state,
            KeyEventMatch((Qt.Key_Enter, Qt.Key_Return)),
            baseplot.do_enter_pressed,
            start_state,
        )

        filter.add_event(
            start_state,
            KeyEventMatch((Qt.Key_Space,)),
            baseplot.do_space_pressed,
            start_state,
        )

        filter.add_event(
            start_state,
            KeyEventMatch((Qt.Key_Right,)),
            baseplot.do_right_pressed,
            start_state,
        )

        filter.add_event(
            start_state,
            KeyEventMatch((Qt.Key_Left,)),
            baseplot.do_left_pressed,
            start_state,
        )

        filter.add_event(
            start_state,
            KeyEventMatch((Qt.Key_Backspace, Qt.Key_Escape)),
            baseplot.backspace_pressed,
            start_state,
        )

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
