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


from functools import lru_cache

import numpy as np
import scipy.ndimage.morphology
from guiqwt.builder import make
from guiqwt.config import CONF
from guiqwt.events import KeyEventMatch, MoveHandler, QtDragHandler
from guiqwt.image import ImagePlot, RawImageItem, RGBImageItem
from guiqwt.label import ObjectInfo
from guiqwt.plot import ImageWidget
from guiqwt.shapes import RectangleShape
from guiqwt.tools import InteractiveTool, SelectTool
from PyQt5.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPixmap
from qwt import QwtScaleDraw

from emzed_gui.configs import get_color
from emzed_gui.helpers import protect_signal_handler, set_rt_formatting_on_x_axis
from emzed_gui.optimized import sample_image

from .modified_guiqwt import ImprovedPanHandler, ImprovedZoomHandler


def get_range(peakmap, peakmap2):
    rtmin, rtmax = peakmap.rt_range()
    mzmin, mzmax = peakmap.mz_range()
    if peakmap2 is not None:
        rtmin2, rtmax2 = peakmap2.rt_range()
        mzmin2, mzmax2 = peakmap2.mz_range()
        rtmin = min(rtmin, rtmin2)
        rtmax = max(rtmax, rtmax2)
        mzmin = min(mzmin, mzmin2)
        mzmax = max(mzmax, mzmax2)
    return rtmin, rtmax, mzmin, mzmax


def set_y_axis_scale_draw(widget):
    """sets minimum extent for aligning chromatogram and peakmap plot"""
    drawer = QwtScaleDraw()
    drawer.setMinimumExtent(50)
    widget.plot.setAxisScaleDraw(widget.plot.yLeft, drawer)


def dilate(data, mzmax, mzmin):
    """dilate image (here this means: paint big pixels) depending on the given mz range"""
    dmz = mzmax - mzmin
    # above dmz > 100.0 we will have n == 2, for dmz < .0 we have n == 4, inbetween
    # we do linear inerpolation:
    dmz_max = 200.0
    dmz_min = 0.001
    smax = 4.0
    smin = 2.0
    n = round(smax - (dmz - dmz_min) / (dmz_max - dmz_min) * (smax - smin))
    n = max(smin, min(smax, n))
    # we use moving max here, no moving sum, because this lead to strong local peaks
    # which dominate the final imager after rescaling from max intensity to 1.0:
    dilated = scipy.ndimage.morphology.grey_dilation(data, int(n))
    return dilated


def dominant_ms_level(peakmaps):
    levels = [level for peakmap in peakmaps for level in peakmap.ms_levels()]
    if not levels:
        return None
    return min(levels)


class PeakMapImageBase(object):
    def __init__(self, peakmaps):
        self.peakmaps = peakmaps
        ms_level = dominant_ms_level(peakmaps)
        if ms_level is not None:
            rtmins, rtmaxs = list(zip(*[pm.rt_range(ms_level) for pm in peakmaps]))
            mzmins, mzmaxs = list(zip(*[pm.mz_range(ms_level) for pm in peakmaps]))
            self.rtmin = min(rtmins)
            self.rtmax = max(rtmaxs)
            self.mzmin = min(mzmins)
            self.mzmax = max(mzmaxs)
        else:
            self.rtmin = self.rtmax = self.mzmin = self.mzmax = 0.0

        self.bounds = QRectF(
            QPointF(self.rtmin, self.mzmin), QPointF(self.rtmax, self.mzmax)
        )

        self.total_imin = 0.0
        maxi = [
            np.max(s.peaks[:, 1]) for pm in peakmaps for s in pm.spectra if len(s.peaks)
        ]
        if maxi:
            self.total_imax = max(maxi)
        else:
            self.total_imax = 1.0

        self.imin = self.total_imin
        self.imax = self.total_imax

        self.gamma = 1.0
        self.is_log = 1

    def get_peakmap_bounds(self):
        return self.rtmin, self.rtmax, self.mzmin, self.mzmax

    def get_gamma(self):
        return self.gamma

    def get_total_imax(self):
        return self.total_imax

    def _set(self, field, value):
        if getattr(self, field) != value:
            self.compute_image.cache_clear()
        setattr(self, field, value)

    def set_imin(self, v):
        self._set("imin", v)

    def set_imax(self, v):
        self._set("imax", v)

    def set_gamma(self, v):
        self._set("gamma", v)

    def set_logarithmic_scale(self, v):
        self._set("is_log", v)

    @lru_cache(maxsize=100)
    def compute_image(self, idx, NX, NY, rtmin, rtmax, mzmin, mzmax):
        if rtmin >= rtmax or mzmin >= mzmax:
            dilated = np.zeros((1, 1))
        else:
            # optimized:
            # one additional row / col as we loose one row and col during smoothing:

            pm = self.peakmaps[idx]
            ms_levels = pm.ms_levels()
            if ms_levels:
                ms_level = min(ms_levels)
            else:
                ms_level = 1  # empty peakmap. next line will create empty image then!
            data = sample_image(
                pm, rtmin, rtmax, mzmin, mzmax, NX + 1, NY + 1, ms_level
            )

            imin = self.imin
            imax = self.imax

            if self.is_log:
                data = np.log(1.0 + data)
                imin = np.log(1.0 + imin)
                imax = np.log(1.0 + imax)

            # set values out of range to black:
            overall_max = np.max(data)
            data[data < imin] = 0
            data[data > imax] = 0

            if overall_max != 0:
                data /= overall_max

            # enlarge peak pixels depending on the mz range in the image:
            dilated = dilate(data, mzmax, mzmin)

        # turn upside down:
        dilated = dilated[::-1, :]

        # apply gamma
        dilated = dilated ** (self.gamma) * 255
        return dilated.astype(np.uint8)


class PeakMapImageItem(PeakMapImageBase, RawImageItem):

    """draws peakmap 2d view dynamically based on given limits"""

    def __init__(self, peakmap):
        RawImageItem.__init__(self, data=np.zeros((1, 1), np.uint8))
        PeakMapImageBase.__init__(self, [peakmap])

        self.update_border()
        self.IMAX = 255
        self.set_lut_range([0, self.IMAX])
        self.set_color_map("hot")

        self.last_canvas_rect = None
        self.last_src_rect = None
        self.last_dst_rect = None
        self.last_xmap = None
        self.last_ymap = None

    def paint_pixmap(self, widget):
        assert self.last_canvas_rect is not None
        x1, y1 = self.last_canvas_rect.left(), self.last_canvas_rect.top()
        x2, y2 = self.last_canvas_rect.right(), self.last_canvas_rect.bottom()

        NX = x2 - x1
        NY = y2 - y1
        pix = QPixmap(NX, NY)
        try:
            painter = QPainter(pix)
            self.draw_border(
                painter, self.last_xmap, self.last_ymap, self.last_canvas_rect
            )
            self.draw_image(
                painter,
                self.last_canvas_rect,
                self.last_src_rect,
                self.last_dst_rect,
                self.last_xmap,
                self.last_xmap,
            )
            # somehow guiqwt paints a distorted border at left/top, so we remove it:
            return pix.copy(2, 2, NX - 2, NY - 2)
        finally:
            painter.end()

    #  ---- QwtPlotItem API ------------------------------------------------------
    def draw_image(self, painter, canvasRect, srcRect, dstRect, xMap, yMap):
        # normally we use this method indirectly from quiqwt which takes the burden of
        # constructing the right parameters. if we want to call this method manually, eg
        # for painting on on a QPixmap for saving the image, we just use the last set of
        # parmeters passed to this method, this is much easier than constructing the
        # params seperatly, and so we get the exact same result as we see on screen:
        self.last_canvas_rect = canvasRect
        self.last_src_rect = srcRect
        self.last_dst_rect = dstRect
        self.last_xmap = xMap
        self.last_ymap = yMap

        x1, y1, x2, y2 = canvasRect.getCoords()
        NX = x2 - x1
        NY = y2 - y1
        rtmin, mzmax, rtmax, mzmin = srcRect
        self.data = self.compute_image(0, NX, NY, rtmin, rtmax, mzmin, mzmax)

        # draw
        srcRect = (0, 0, NX, NY)
        # x1, y1, x2, y2 = canvasRect.getCoords()
        RawImageItem.draw_image(
            self, painter, canvasRect, srcRect, (x1, y1, x2, y2), xMap, yMap
        )


class RGBPeakMapImageItem(PeakMapImageBase, RGBImageItem):

    """draws peakmap 2d view dynamically based on given limits"""

    def __init__(self, peakmap, peakmap2):
        PeakMapImageBase.__init__(self, [peakmap, peakmap2])
        self.xmin = self.rtmin
        self.xmax = self.rtmax
        self.ymin = self.mzmin
        self.ymax = self.mzmax
        RawImageItem.__init__(self, data=np.zeros((1, 1, 3), np.uint32))
        self.update_border()

    def paint_pixmap(self, widget):
        assert self.last_canvas_rect is not None
        x1, y1 = self.last_canvas_rect.left(), self.last_canvas_rect.top()
        x2, y2 = self.last_canvas_rect.right(), self.last_canvas_rect.bottom()

        NX = x2 - x1
        NY = y2 - y1
        pix = QPixmap(NX, NY)
        painter = QPainter(pix)
        try:
            self.draw_border(
                painter, self.last_xmap, self.last_ymap, self.last_canvas_rect
            )
            self.draw_image(
                painter,
                self.last_canvas_rect,
                self.last_src_rect,
                self.last_dst_rect,
                self.last_xmap,
                self.last_xmap,
            )
            # somehow guiqwt paints a distorted border at left/top, so we remove it:
            return pix.copy(2, 2, NX - 2, NY - 2)
        finally:
            painter.end()

    #  ---- QwtPlotItem API ------------------------------------------------------
    def draw_image(self, painter, canvasRect, srcRect, dstRect, xMap, yMap):
        # normally we use this method indirectly from quiqwt which takes the burden of
        # constructing the right parameters. if we want to call this method manually, eg
        # for painting on on a QPixmap for saving the image, we just use the last set of
        # parmeters passed to this method, this is much easier than constructing the
        # params seperatly, and so we get the exact same result as we see on screen:
        self.last_canvas_rect = canvasRect
        self.last_src_rect = srcRect
        self.last_dst_rect = dstRect
        self.last_xmap = xMap
        self.last_ymap = yMap

        rtmin, mzmax, rtmax, mzmin = srcRect

        x1, y1 = canvasRect.left(), canvasRect.top()
        x2, y2 = canvasRect.right(), canvasRect.bottom()
        NX = x2 - x1
        NY = y2 - y1
        rtmin, mzmax, rtmax, mzmin = srcRect

        image0 = self.compute_image(0, NX, NY, rtmin, rtmax, mzmin, mzmax)[::-1, :]
        image1 = self.compute_image(1, NX, NY, rtmin, rtmax, mzmin, mzmax)[::-1, :]

        dilated0 = dilate(image0.astype(np.uint32), mzmax, mzmin)
        dilated1 = dilate(image1.astype(np.uint32), mzmax, mzmin)

        def paint(values, color):
            color = color.lstrip("#")
            rc = int(color[:2], base=16)
            gc = int(color[2:4], base=16)
            bc = int(color[4:], base=16)

            R = values * rc // 256
            G = values * gc // 256
            B = values * bc // 256

            return R, G, B

        c0 = get_color(0)
        c1 = get_color(1)

        r0, g0, b0 = paint(dilated0, c0)
        r1, g1, b1 = paint(dilated1, c1)

        # https://stackoverflow.com/questions/726549#answer-726564
        alpha = 255
        r = np.clip(r0 + r1, 0, 255)
        g = np.clip(g0 + g1, 0, 255)
        b = np.clip(b0 + b1, 0, 255)

        self.data = alpha << 24 | r << 16 | g << 8 | b

        self.bounds = QRectF(rtmin, mzmin, rtmax - rtmin, mzmax - mzmin)
        RGBImageItem.draw_image(self, painter, canvasRect, srcRect, dstRect, xMap, yMap)


class PeakmapCursorRangeInfo(ObjectInfo):
    def __init__(self, marker):
        ObjectInfo.__init__(self)
        self.marker = marker

    def get_text(self):
        rtmin, mzmin, rtmax, mzmax = self.marker.get_rect()
        if not np.isnan(rtmax):
            rtmin, rtmax = sorted((rtmin, rtmax))
        if not np.isnan(mzmax):
            mzmin, mzmax = sorted((mzmin, mzmax))
        if not np.isnan(rtmax):
            delta_mz = mzmax - mzmin
            delta_rt = rtmax - rtmin
            line0 = "mz: %10.5f ..  %10.5f (delta=%5.5f)" % (mzmin, mzmax, delta_mz)
            line1 = "rt:  %6.2fm   ..   %6.2fm   (delta=%.1fs)" % (
                rtmin / 60.0,
                rtmax / 60.0,
                delta_rt,
            )
            return "<pre>%s</pre>" % "<br>".join((line0, line1))
        else:
            return """<pre>mz: %9.5f<br>rt: %6.2fm</pre>""" % (mzmin, rtmin / 60.0)


class PeakmapZoomTool(InteractiveTool):

    """selects rectangle from peakmap"""

    TITLE = "Selection"
    ICON = "selection.png"
    CURSOR = Qt.CrossCursor

    def setup_filter(self, baseplot):
        filter = baseplot.filter
        # Initialisation du filtre

        start_state = filter.new_state()

        def create_emitter(signal):
            def handler(*_):
                print("HANDLE", _)
                signal.emit()

            return handler

        key_left_handler = create_emitter(baseplot.KEY_LEFT)
        key_right_handler = create_emitter(baseplot.KEY_RIGHT)
        key_end_handler = create_emitter(baseplot.KEY_END)
        key_backspace_handler = create_emitter(baseplot.KEY_BACKSPACE)

        key_left_and_aliases = [(Qt.Key_Z, Qt.ControlModifier), Qt.Key_Left]
        filter.add_event(
            start_state,
            KeyEventMatch(key_left_and_aliases),
            key_left_handler,
            start_state,
        )

        key_right_and_aliases = [(Qt.Key_Y, Qt.ControlModifier), Qt.Key_Right]
        filter.add_event(
            start_state,
            KeyEventMatch(key_right_and_aliases),
            key_right_handler,
            start_state,
        )

        filter.add_event(
            start_state,
            KeyEventMatch((Qt.Key_Backspace, Qt.Key_Escape, Qt.Key_Home)),
            key_backspace_handler,
            start_state,
        )

        filter.add_event(
            start_state, KeyEventMatch((Qt.Key_End,)), key_end_handler, start_state
        )

        handler = QtDragHandler(filter, Qt.LeftButton, start_state=start_state)
        handler.SIG_MOVE.connect(baseplot.move_in_drag_mode)
        handler.SIG_START_TRACKING.connect(baseplot.start_drag_mode)
        handler.SIG_STOP_NOT_MOVING.connect(baseplot.stop_drag_mode)
        handler.SIG_STOP_MOVING.connect(baseplot.stop_drag_mode)

        handler = QtDragHandler(
            filter, Qt.LeftButton, start_state=start_state, mods=Qt.ShiftModifier
        )
        handler.SIG_MOVE.connect(baseplot.move_in_drag_mode)
        handler.SIG_START_TRACKING.connect(baseplot.start_drag_mode)
        handler.SIG_STOP_NOT_MOVING.connect(baseplot.stop_drag_mode)
        handler.SIG_STOP_MOVING.connect(baseplot.stop_drag_mode)

        # Bouton du milieu
        ImprovedPanHandler(filter, Qt.MidButton, start_state=start_state)
        ImprovedPanHandler(
            filter, Qt.LeftButton, mods=Qt.AltModifier, start_state=start_state
        )
        # AutoZoomHandler(filter, Qt.MidButton, start_state=start_state)

        # Bouton droit
        ImprovedZoomHandler(filter, Qt.RightButton, start_state=start_state)
        ImprovedZoomHandler(
            filter, Qt.LeftButton, mods=Qt.ControlModifier, start_state=start_state
        )
        # MenuHandler(filter, Qt.RightButton, start_state=start_state)

        # Autres (touches, move)
        MoveHandler(filter, start_state=start_state)
        MoveHandler(filter, start_state=start_state, mods=Qt.ShiftModifier)
        MoveHandler(filter, start_state=start_state, mods=Qt.AltModifier)

        return start_state


class ModifiedImagePlot(ImagePlot):

    """special handlers for dragging selection, source is PeakmapZoomTool"""

    VIEW_RANGE_CHANGED = pyqtSignal(float, float, float, float)
    KEY_LEFT = pyqtSignal()
    KEY_RIGHT = pyqtSignal()
    KEY_BACKSPACE = pyqtSignal()
    KEY_END = pyqtSignal()
    CURSOR_MOVED = pyqtSignal(float, float)

    # as this class is used for patching, the __init__ is never called, so we set
    # default values as class atributes:

    rtmin = rtmax = mzmin = mzmax = None
    peakmap_range = (None, None, None, None)
    dragging = False

    def mouseDoubleClickEvent(self, evt):
        if evt.button() == Qt.RightButton:
            self.key_left()

    def set_limits(self, rtmin, rtmax, mzmin, mzmax):
        if self.peakmap_range[0] is not None:
            rtmin = max(rtmin, self.peakmap_range[0])
        self.rtmin = rtmin

        if self.peakmap_range[1] is not None:
            rtmax = min(rtmax, self.peakmap_range[1])
        self.rtmax = rtmax

        if self.peakmap_range[2] is not None and self.peakmap_range[3] is not None:
            mzmin = min(max(mzmin, self.peakmap_range[2]), self.peakmap_range[3])
            mzmax = max(min(mzmax, self.peakmap_range[3]), self.peakmap_range[2])

        self.mzmin = mzmin
        self.mzmax = mzmax

        if mzmin == mzmax:
            mzmin *= 1.0 - 1e-5  # - 10 ppm
            mzmax *= 1.0 + 1e-5  # + 10 ppm
        if rtmin == rtmax:
            rtmin += -0.1
            rtmax += 0.1
        self.set_plot_limits(rtmin, rtmax, mzmin, mzmax, "bottom", "right")
        self.set_plot_limits(rtmin, rtmax, mzmin, mzmax, "top", "left")

        # only rgb plot needs update of bounds:
        peakmap_item = self.get_unique_item(RGBPeakMapImageItem)
        if peakmap_item is not None:
            peakmap_item.bounds = QRectF(QPointF(rtmin, mzmin), QPointF(rtmax, mzmax))

        self.replot()

    def set_rt_limits(self, rtmin, rtmax):
        if self.mzmin is not None and self.mzmax is not None:
            self.set_limits(rtmin, rtmax, self.mzmin, self.mzmax)

    def set_mz_limits(self, mzmin, mzmax):
        if self.rtmin is not None and self.rtmax is not None:
            self.set_limits(self.rtmin, self.rtmax, mzmin, mzmax)

    def get_coords(self, evt):
        return (
            self.invTransform(self.xBottom, evt.x()),
            self.invTransform(self.yLeft, evt.y()),
        )

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

    @protect_signal_handler
    def do_move_marker(self, event):
        pos = event.pos()
        self.set_marker_axes()
        self.cross_marker.setZ(self.get_max_z() + 1)
        self.cross_marker.setVisible(True)
        self.cross_marker.move_local_point_to(0, pos)
        self.replot()
        rt = self.invTransform(self.xBottom, pos.x())
        mz = self.invTransform(self.yLeft, pos.y())
        self.CURSOR_MOVED.emit(rt, mz)

    def set_rt(self, rt):
        self.cross_marker.setValue(rt, self.cross_marker.yValue())
        self.replot()

    def set_mz(self, mz):
        self.cross_marker.setValue(self.cross_marker.xValue(), mz)
        self.replot()

    @protect_signal_handler
    def start_drag_mode(self, filter_, evt):
        self.start_at = self.get_coords(evt)
        self.moved = False
        self.dragging = True
        marker = self.get_unique_item(RectangleShape)
        marker.set_rect(
            self.start_at[0], self.start_at[1], self.start_at[0], self.start_at[1]
        )
        self.cross_marker.setVisible(False)  # no cross marker when dragging
        self.rect_label.setVisible(1)
        self.with_shift_key = evt.modifiers() == Qt.ShiftModifier
        self.replot()

    @protect_signal_handler
    def move_in_drag_mode(self, filter_, evt):
        now = self.get_coords(evt)
        rect_marker = self.get_unique_item(RectangleShape)
        rect_marker.setVisible(1)
        now_rt = max(self.rtmin, min(now[0], self.rtmax))
        now_mz = max(self.mzmin, min(now[1], self.mzmax))
        rect_marker.set_rect(self.start_at[0], self.start_at[1], now_rt, now_mz)
        self.moved = True
        self.replot()

    def mouseReleaseEvent(self, evt):
        # stop drag mode is not called immediatly when dragging and releasing shift
        # during dragging.
        if self.dragging:
            self.stop_drag_mode(None, evt)

    @protect_signal_handler
    def stop_drag_mode(self, filter_, evt):
        stop_at = self.get_coords(evt)
        rect_marker = self.get_unique_item(RectangleShape)
        rect_marker.setVisible(0)

        # reactivate cursor
        self.cross_marker.set_pos(stop_at[0], stop_at[1])
        self.cross_marker.setZ(self.get_max_z() + 1)

        # passing None here arives as np.nan if you call get_rect later, so we use
        # np.nan here:
        rect_marker.set_rect(stop_at[0], stop_at[1], np.nan, np.nan)

        self.dragging = False

        if self.moved and not self.with_shift_key:
            rtmin, rtmax = self.start_at[0], stop_at[0]
            # be sure that rtmin <= rtmax:
            rtmin, rtmax = min(rtmin, rtmax), max(rtmin, rtmax)

            mzmin, mzmax = self.start_at[1], stop_at[1]
            # be sure that mzmin <= mzmax:
            mzmin, mzmax = min(mzmin, mzmax), max(mzmin, mzmax)

            # keep coordinates in peakmap:
            rtmin = max(self.rtmin, min(self.rtmax, rtmin))
            rtmax = max(self.rtmin, min(self.rtmax, rtmax))
            mzmin = max(self.mzmin, min(self.mzmax, mzmin))
            mzmax = max(self.mzmin, min(self.mzmax, mzmax))

            self.set_limits(rtmin, rtmax, mzmin, mzmax)
            self.VIEW_RANGE_CHANGED.emit(rtmin, rtmax, mzmin, mzmax)
        else:
            self.replot()

    @protect_signal_handler
    def do_zoom_view(self, dx, dy, lock_aspect_ratio=False):
        """
        modified version of do_zoom_view from base class,
        we restrict zooming and panning to ranges of peakmap.

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

        axis_ids_horizontal = (self.get_axis_id("bottom"), self.get_axis_id("top"))
        axis_ids_vertical = (self.get_axis_id("left"), self.get_axis_id("right"))

        rtmin = rtmax = mzmin = mzmax = None

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

            # patch for not "zooming out"
            if axis_id in axis_ids_horizontal:
                vmin = max(vmin, self.peakmap_range[0])
                vmax = min(vmax, self.peakmap_range[1])
                rtmin = vmin
                rtmax = vmax
            elif axis_id in axis_ids_vertical:
                vmin = max(vmin, self.peakmap_range[2])
                vmax = min(vmax, self.peakmap_range[3])
                mzmin = vmin
                mzmax = vmax

            self.set_axis_limits(axis_id, vmin, vmax)

        self.setAutoReplot(auto)
        if None not in (rtmin, rtmax, mzmin, mzmax):
            self.VIEW_RANGE_CHANGED.emit(rtmin, rtmax, mzmin, mzmax)
        self.replot()

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
        axis_ids_horizontal = (self.get_axis_id("bottom"), self.get_axis_id("top"))
        axis_ids_vertical = (self.get_axis_id("left"), self.get_axis_id("right"))

        for (x1, x0, _start, _width), axis_id in axes_to_update:
            lbound, hbound = self.get_axis_limits(axis_id)
            i_lbound = self.transform(axis_id, lbound)
            i_hbound = self.transform(axis_id, hbound)
            delta = x1 - x0
            vmin = self.invTransform(axis_id, i_lbound - delta)
            vmax = self.invTransform(axis_id, i_hbound - delta)
            # patch for not "panning out"
            if axis_id in axis_ids_horizontal:
                vmin = max(vmin, self.peakmap_range[0])
                vmax = min(vmax, self.peakmap_range[1])
                rtmin = vmin
                rtmax = vmax
            elif axis_id in axis_ids_vertical:
                vmin = max(vmin, self.peakmap_range[2])
                vmax = min(vmax, self.peakmap_range[3])
                mzmin = vmin
                mzmax = vmax
            self.set_axis_limits(axis_id, vmin, vmax)

        self.setAutoReplot(auto)
        self.replot()
        self.VIEW_RANGE_CHANGED.emit(rtmin, rtmax, mzmin, mzmax)


def set_image_plot(widget, image_item, peakmap_range):
    widget.plot.peakmap_range = peakmap_range
    widget.plot.del_all_items()
    widget.plot.add_item(image_item)
    create_peakmap_labels(widget.plot)
    # for zooming and panning with mouse drag:
    t = widget.add_tool(SelectTool)
    widget.set_default_tool(t)
    t.activate()
    # for selecting zoom window
    t = widget.add_tool(PeakmapZoomTool)
    t.activate()


def create_peakmap_labels(plot):
    rect_marker = RectangleShape()
    rect_label = make.info_label(
        "TR", [PeakmapCursorRangeInfo(rect_marker)], title=None
    )
    rect_label.labelparam.label = ""
    rect_label.labelparam.font.size = 12
    rect_label.labelparam.update_label(rect_label)
    rect_label.setVisible(1)
    plot.rect_label = rect_label
    plot.add_item(rect_label)

    params = {
        "shape/drag/symbol/size": 0,
        "shape/drag/line/color": "#cccccc",
        "shape/drag/line/width": 1.5,
        "shape/drag/line/alpha": 0.4,
        "shape/drag/line/style": "SolidLine",
    }
    CONF.update_defaults(dict(plot=params))
    rect_marker.shapeparam.read_config(CONF, "plot", "shape/drag")
    rect_marker.shapeparam.update_shape(rect_marker)
    rect_marker.setVisible(0)
    rect_marker.set_rect(0, 0, np.nan, np.nan)
    plot.add_item(rect_marker)

    plot.canvas_pointer = True  # x-cross marker on
    # we hack label_cb for updating legend:

    def label_cb(rt, mz):
        # passing None here arives as np.nan if you call get_rect later, so we use
        # np.nan here:
        rect_marker.set_rect(rt, mz, np.nan, np.nan)
        return ""

    cross_marker = plot.cross_marker
    cross_marker.label_cb = label_cb
    params = {
        "marker/cross/line/color": "#cccccc",
        "marker/cross/line/width": 1.5,
        "marker/cross/line/alpha": 0.4,
        "marker/cross/line/style": "DashLine",
        "marker/cross/symbol/marker": "NoSymbol",
        "marker/cross/markerstyle": "Cross",
    }
    CONF.update_defaults(dict(plot=params))
    cross_marker.markerparam.read_config(CONF, "plot", "marker/cross")
    cross_marker.markerparam.update_marker(cross_marker)


class PeakMapPlottingWidget(ImageWidget):
    def __init__(self, parent=None):
        super(PeakMapPlottingWidget, self).__init__(
            parent=parent,
            title="",
            lock_aspect_ratio=False,
            xlabel="rt",
            ylabel="m/z",
        )
        self.peakmap_item = None
        # patch memeber's methods:
        self.plot.__class__ = ModifiedImagePlot

        # take over events:
        self.VIEW_RANGE_CHANGED = self.plot.VIEW_RANGE_CHANGED
        self.KEY_LEFT = self.plot.KEY_LEFT
        self.KEY_RIGHT = self.plot.KEY_RIGHT
        self.KEY_BACKSPACE = self.plot.KEY_BACKSPACE
        self.KEY_END = self.plot.KEY_END
        self.CURSOR_MOVED = self.plot.CURSOR_MOVED

        self.plot.set_axis_direction("left", False)
        self.plot.set_axis_direction("right", False)

        set_rt_formatting_on_x_axis(self.plot)
        set_y_axis_scale_draw(self)
        self.plot.enableAxis(self.plot.colormap_axis, False)

    def set_limits(self, *a, **kw):
        self.plot.set_limits(*a, **kw)

    def set_peakmaps(self, peakmap, peakmap2):
        self.peakmap = peakmap
        self.peakmap2 = peakmap2

        # only makes sense for gamma, after reload imin/imax and rt/mz bounds will not
        # be valid any more

        if self.peakmap_item is not None:
            gamma_before = self.peakmap_item.get_gamma()
        else:
            gamma_before = None
        if peakmap2 is not None:
            self.peakmap_item = RGBPeakMapImageItem(peakmap, peakmap2)
        else:
            self.peakmap_item = PeakMapImageItem(peakmap)
        set_image_plot(self, self.peakmap_item, get_range(peakmap, peakmap2))
        if gamma_before is not None:
            self.peakmap_item.set_gamma(gamma_before)

    def replot(self):
        self.plot.replot()

    def get_plot(self):
        return self.plot

    def paint_pixmap(self):
        return self.peakmap_item.paint_pixmap(self)

    def set_logarithmic_scale(self, flag):
        self.peakmap_item.set_logarithmic_scale(flag)

    def set_gamma(self, gamma):
        self.peakmap_item.set_gamma(gamma)

    def set_imin(self, imin):
        self.peakmap_item.set_imin(imin)

    def set_imax(self, imax):
        self.peakmap_item.set_imax(imax)

    def get_total_imax(self):
        return self.peakmap_item.get_total_imax()

    def set_cursor_rt(self, rt):
        self.plot.set_rt(rt)

    def set_cursor_mz(self, mz):
        self.plot.set_mz(mz)

    def blockSignals(self, flag):
        super(PeakMapPlottingWidget, self).blockSignals(flag)
        self.plot.blockSignals(flag)
