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


import contextlib
import datetime
import functools
import os
import time
import types

from qwt import QwtScaleDraw, QwtText


def widthOfTableWidget(tw):
    width = 0
    for i in range(tw.columnCount()):
        width += tw.columnWidth(i)

    width += tw.verticalHeader().sizeHint().width()
    width += tw.verticalScrollBar().sizeHint().width()
    width += tw.frameWidth() * 2
    return width


def block_other_calls_during_execution(fun):
    in_process = False

    @functools.wraps(fun)
    def wrapped(*a, **kw):
        nonlocal in_process
        if in_process:
            return
        in_process = True
        try:
            return fun(*a, **kw)
        finally:
            in_process = False

    return wrapped


def protect_signal_handler(fun):
    @functools.wraps(fun)
    def wrapped(*a, **kw):
        try:
            return fun(*a, **kw)
        except Exception:
            import traceback

            traceback.print_exc()

    return wrapped


def formatSeconds(seconds):
    return "%.2fm" % (seconds / 60.0)


def set_rt_formatting_on_x_axis(plot):
    def label(self, v):
        return QwtText(formatSeconds(v))

    a = QwtScaleDraw()
    a.label = types.MethodType(label, plot)
    plot.setAxisScaleDraw(plot.xBottom, a)


def set_datetime_formating_on_x_axis(plot):
    def label(self, float_val):
        if float_val < 1.0:
            return QwtText("")
        dt = datetime.datetime.fromordinal(int(float_val))
        txt = str(dt).split(" ")[0]
        return QwtText(txt)

    a = QwtScaleDraw()
    a.label = types.MethodType(label, plot)
    plot.setAxisScaleDraw(plot.xBottom, a)


debug_mode = os.environ.get("DEBUG", 0)


@contextlib.contextmanager
def timer(name="", debug_mode=debug_mode):
    started = time.time()
    yield
    needed = time.time() - started
    if debug_mode:
        print(name, "needed %.5fs" % needed)


def timethis(function):
    @functools.wraps(function)
    def inner(*a, **kw):
        with timer(function.__name__):
            return function(*a, **kw)

    return inner
