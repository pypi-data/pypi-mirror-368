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


import datetime

from guiqwt.builder import make
from guiqwt.curve import CurveItem, CurvePlot
from guiqwt.events import EventMatch, PanHandler, ZoomHandler
from PyQt5.QtCore import QEvent, QObject, Qt, pyqtSignal

from emzed_gui.helpers import protect_signal_handler


def patch_inner_plot_object(widget, plot_clz):
    # we overwrite some methods of the given object:
    widget.plot.__class__ = plot_clz
    plot_clz._init_patched_object(widget.plot)

    # we attach a signal (pyqtSignal is only usable for subclasses of QObject, and
    # deriving from QObject does not work with multiple inheritance, so we have to apply
    # some trickery):
    class _Q(QObject):
        CURSOR_MOVED = pyqtSignal(float)
        VIEW_RANGE_CHANGED = pyqtSignal(float, float)

    widget._q = _Q()
    widget.CURSOR_MOVED = widget.plot.CURSOR_MOVED = widget._q.CURSOR_MOVED
    widget.VIEW_RANGE_CHANGED = (
        widget.plot.VIEW_RANGE_CHANGED
    ) = widget._q.VIEW_RANGE_CHANGED


def make_unselectable_curve(*a, **kw):
    curve = make.curve(*a, **kw)
    curve.__class__ = UnselectableCurveItem
    return curve


class UnselectableCurveItem(CurveItem):
    """modification(s):
    selection (which plots a square at each (x,y) ) is turned off
    """

    def can_select(self):
        return False


class ImprovedPanHandler(PanHandler):
    def __init__(
        self,
        filter,
        btn,
        mods=Qt.NoModifier,
        start_state=0,
        call_stop_moving_handler=False,
    ):
        super(ImprovedPanHandler, self).__init__(filter, btn, mods, start_state)
        # additionally we reset state machine if mouse is release anyhow !
        filter.add_event(
            self.state0, filter.mouse_release(btn), self.stop_notmoving, start_state
        )
        filter.add_event(
            self.state1, filter.mouse_release(btn), self.stop_moving, start_state
        )
        self._call_stop_moving_handler = call_stop_moving_handler

    def stop_moving(self, filter_, event):
        result = super().stop_notmoving(filter_, event)
        if self._call_stop_moving_handler:
            x_state, y_state = self.get_move_state(filter_, event.pos())
            filter_.plot.do_finish_pan_view(x_state, y_state)
        return result


class ImprovedZoomHandler(ZoomHandler):
    def __init__(
        self,
        filter,
        btn,
        mods=Qt.NoModifier,
        start_state=0,
        call_stop_moving_handler=False,
    ):
        super(ImprovedZoomHandler, self).__init__(filter, btn, mods, start_state)
        # additionally we reset state machine if mouse is release anyhow !
        filter.add_event(
            self.state0, filter.mouse_release(btn), self.stop_notmoving, start_state
        )
        filter.add_event(
            self.state1, filter.mouse_release(btn), self.stop_moving, start_state
        )
        self._call_stop_moving_handler = call_stop_moving_handler

    def stop_moving(self, filter_, event):
        result = super().stop_notmoving(filter_, event)
        if self._call_stop_moving_handler:
            x_state, y_state = self.get_move_state(filter_, event.pos())
            filter_.plot.do_finish_zoom_view(x_state, y_state)
        return result


class PositiveValuedCurvePlot(CurvePlot):

    """modifications:
    - zooming preserves x axis at bottom of plot
    - panning is only in x direction
    - handler for backspace, called by RtSelectionTool and MzSelectionTool
    """

    @property
    def overall_x_min(self):
        if not hasattr(self, "_overall_x_min"):
            self._overall_x_min = None
        return self._overall_x_min

    @overall_x_min.setter
    def overall_x_min(self, xmin):
        self._overall_x_min = xmin

    @property
    def overall_x_max(self):
        if not hasattr(self, "_overall_x_max"):
            self._overall_x_max = None
        return self._overall_x_max

    @overall_x_max.setter
    def overall_x_max(self, xmax):
        self._overall_x_max = xmax

    @protect_signal_handler
    def do_zoom_view(self, dx, dy, lock_aspect_ratio=False):
        """
        copied and modified version of do_zoom_view from base class, we restrict zooming
        and panning to positive y-values

        Change the scale of the active axes (zoom/dezoom) according to dx, dy
        dx, dy are tuples composed of (initial pos, dest pos)
        We try to keep initial pos fixed on the canvas as the scale changes
        """
        # See guiqwt/events.py where dx and dy are defined like this:
        #   dx = (pos.x(), self.last.x(), self.start.x(), rct.width())
        #   dy = (pos.y(), self.last.y(), self.start.y(), rct.height())
        # where:
        #   * self.last is the mouse position seen during last event
        #   * self.start is the first mouse position (here, this is the
        #     coordinate of the point which is at the center of the zoomed area)
        #   * rct is the plot rect contents
        #   * pos is the current mouse cursor position
        auto = self.autoReplot()
        self.setAutoReplot(False)
        dx = (-1,) + dx  # adding direction to tuple dx
        dy = (1,) + dy  # adding direction to tuple dy
        if lock_aspect_ratio:
            direction, x1, x0, start, width = dx
            F = 1 + 3 * direction * float(x1 - x0) / width
        axes_to_update = self.get_axes_to_update(dx, dy)

        axis_ids_vertical = (self.get_axis_id("left"), self.get_axis_id("right"))

        final_xmin = final_xmax = None

        for (direction, x1, x0, start, width), axis_id in axes_to_update:
            lbound, hbound = self.get_axis_limits(axis_id)
            if not lock_aspect_ratio:
                F = 1 + 3 * direction * float(x1 - x0) / width
            if F * (hbound - lbound) == 0:
                continue
            if self.get_axis_scale(axis_id) == "lin":
                orig = self.invTransform(axis_id, start)
                vmin = orig - F * (orig - lbound)
                vmax = orig + F * (hbound - orig)
            else:  # log scale
                i_lbound = self.transform(axis_id, lbound)
                i_hbound = self.transform(axis_id, hbound)
                imin = start - F * (start - i_lbound)
                imax = start + F * (i_hbound - start)
                vmin = self.invTransform(axis_id, imin)
                vmax = self.invTransform(axis_id, imax)

            # our modification for not zooming into "negative space" ;) :
            if axis_id in axis_ids_vertical:
                vmin = 0
                vmax = abs(vmax)
            else:
                # not zooming "out of known data":
                if self.overall_x_min is not None:
                    if vmin < self.overall_x_min:
                        vmin = self.overall_x_min
                        vmax = self.overall_x_max
                if self.overall_x_max is not None:
                    if vmax > self.overall_x_max:
                        vmin = self.overall_x_min
                        vmax = self.overall_x_max
                final_xmin = vmin
                final_xmax = vmax
            self.set_axis_limits(axis_id, vmin, vmax)

        self.setAutoReplot(auto)
        # the signal MUST be emitted after replot, otherwise
        # the receiver won't see the new bounds (don't know why?)
        self.replot()
        if final_xmin is not None and final_xmax is not None:
            self.VIEW_RANGE_CHANGED.emit(final_xmin, final_xmax)

    @protect_signal_handler
    def do_pan_view(self, dx, dy):
        """
        modified version of do_pan_view from base class,
        we restrict zooming and panning to ranges of peakmap.

        Translate the active axes by dx, dy
        dx, dy are tuples composed of (initial pos, dest pos)
        """
        auto = self.autoReplot()
        self.setAutoReplot(False)
        axes_to_update = self.get_axes_to_update(dx, dy)
        axis_ids_vertical = (self.get_axis_id("left"), self.get_axis_id("right"))

        # tofix: compute range of overall spectrum, not range of shown peaks:
        for (x1, x0, _start, _width), axis_id in axes_to_update:
            lbound, hbound = self.get_axis_limits(axis_id)
            i_lbound = self.transform(axis_id, lbound)
            i_hbound = self.transform(axis_id, hbound)
            delta = x1 - x0
            vmin = self.invTransform(axis_id, i_lbound - delta)
            vmax = self.invTransform(axis_id, i_hbound - delta)
            # patch for not zooming into "negative space" ;) :
            if axis_id in axis_ids_vertical:
                vmin = 0
                if vmax < 0:
                    vmax = -vmax
            if axis_id not in axis_ids_vertical:
                if self.overall_x_min is not None:
                    if vmin < self.overall_x_min:
                        self.setAutoReplot(auto)
                        return
                if self.overall_x_max is not None:
                    if vmax > self.overall_x_max:
                        self.setAutoReplot(auto)
                        return
                final_xmin = vmin
                final_xmax = vmax
            self.set_axis_limits(axis_id, vmin, vmax)

        self.setAutoReplot(auto)
        # the signal MUST be emitted after replot, otherwise
        # we receiver won't see the new bounds (don't know why?)
        self.replot()
        self.VIEW_RANGE_CHANGED.emit(final_xmin, final_xmax)


class ExtendedCurvePlot(CurvePlot):
    @protect_signal_handler
    def backspace_pressed(self, filter, evt):
        """reset axes of plot"""
        self.reset_x_limits()

    def get_items_of_class(self, clz):
        for item in self.items:
            if isinstance(item, clz):
                yield item

    def get_unique_item(self, clz):
        items = set(self.get_items_of_class(clz))
        if len(items) == 0:
            return None
        if len(items) != 1:
            raise Exception(
                "%d instance(s) of %s among CurvePlots items !" % (len(items), clz)
            )
        return items.pop()

    def set_limit(self, ix, value):
        limits = list(self.get_plot_limits())
        limits[ix] = value
        self.set_plot_limits(*limits)

    def seen_yvals(self, xmin, xmax):
        yvals = []
        if isinstance(xmin, datetime.datetime):
            xmin = xmin.toordinal()
        if isinstance(xmax, datetime.datetime):
            xmax = xmax.toordinal()
        for item in self.items:
            if isinstance(item, CurveItem):
                x, y = item.get_data()
                xy = list(zip(x, y))
                xy = [(xi, yi) for (xi, yi) in xy if xmin is None or xi >= xmin]
                xy = [(xi, yi) for (xi, yi) in xy if xmax is None or xi <= xmax]
                if xy:
                    x, y = list(zip(*xy))  # unzip
                    yvals.extend(y)
        return yvals

    def reset_y_limits(self, ymin=None, ymax=None, fac=1.1, xmin=None, xmax=None):
        yvals = self.seen_yvals(xmin, xmax)

        if ymin is None:
            if len(yvals) > 0:
                ymin = min(yvals) / fac
            else:
                ymin = 0
        if ymax is None:
            if len(yvals) > 0:
                ymax = max(yvals) * fac
            else:
                ymax = 1.0
        self.update_plot_ylimits(ymin, ymax)

    def update_plot_xlimits(self, xmin, xmax, rescale_y=False):
        _, _, ymin, ymax = self.get_plot_limits()
        self.set_plot_limits(xmin, xmax, ymin, ymax)
        self.update_background_curves(xmin, xmax)
        if rescale_y:
            self.setAxisAutoScale(self.yLeft)  # y-achse
        # self.VIEW_RANGE_CHANGED.emit(xmin, xmax)
        self.updateAxes()
        self.replot()

    def update_plot_ylimits(self, ymin, ymax):
        xmin, xmax, _, _ = self.get_plot_limits()
        self.update_background_curves(xmin, xmax)
        self.set_plot_limits(xmin, xmax, ymin, ymax)
        self.updateAxes()
        self.replot()

    def do_finish_pan_view(self, dx, dy):
        self.resample(dx, dy)

    def do_finish_zoom_view(self, dx, dy):
        self.resample(dx, dy)

    def resample(self, dx, dy):
        dx = (-1,) + dx  # adding direction to tuple dx
        dy = (1,) + dy  # adding direction to tuple dy
        axes_to_update = self.get_axes_to_update(dx, dy)

        xmins = []
        xmaxs = []

        axis_ids_horizontal = (self.get_axis_id("bottom"), self.get_axis_id("top"))
        for __, id_ in axes_to_update:
            if id_ in axis_ids_horizontal:
                xmin, xmax = self.get_axis_limits(id_)
                xmins.append(xmin)
                xmaxs.append(xmax)

        xmin = min(xmins)
        xmax = max(xmaxs)
        self.update_plot_xlimits(xmin, xmax, rescale_y=False)
        self.replot()


class LeaveHandler(object):
    def __init__(self, filter, btn=Qt.NoButton, mods=Qt.NoModifier, start_state=0):
        leave_event_matcher = filter.events.setdefault(
            ("leave", Qt.NoButton, Qt.NoModifier), LeaveEventMatch()
        )

        filter.add_event(start_state, leave_event_matcher, self.leave, start_state)

    def leave(self, filter, event):
        filter.plot.cursor_leaves()


class LeaveEventMatch(EventMatch):
    def __init__(self):
        super(LeaveEventMatch, self).__init__()
        self.evt_type = QEvent.Leave

    def get_event_types(self):
        return frozenset((self.evt_type,))

    def __call__(self, event):
        return event.type() == self.evt_type

    def __repr__(self):
        return "<LeaveEventMatch>"
