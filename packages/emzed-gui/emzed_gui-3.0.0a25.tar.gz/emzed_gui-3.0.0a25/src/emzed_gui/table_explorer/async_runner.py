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


import random
import time
from contextlib import contextmanager
from functools import partial

from PyQt5.Qt import QApplication
from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal


class Worker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    message = pyqtSignal(str)
    result = pyqtSignal(object)

    def __init__(self, f, args):
        super(Worker, self).__init__()
        self.f = f
        self.args = args
        self.setObjectName("%s_%s" % (str(time.time()), random.random()))

    def run(self):
        try:
            self.message.emit("run %s %s" % (self.f.__name__, self.args))
            result = self.f(*self.args)
            self.result.emit(result)
            self.message.emit("emitted %s" % result)
        except Exception:
            import traceback

            e = traceback.format_exc()
            self.error.emit(e)
        finally:
            self.finished.emit()


class AsyncRunner(object):
    def __init__(self, parent=None, reporter=None):
        self.workers = {}
        self.parent = parent
        self.reporter = reporter

    def run_async_chained(self, functions, first_args):
        def start(i, args):
            if i >= len(functions):
                return None
            f = functions[i]

            def call_back(result):
                start(i + 1, (result,))

            self.run_async(f, args, call_back=call_back)

        start(0, first_args)

    def _setup_worker(self, function, args, call_back):
        worker = Worker(function, args)
        worker.error.connect(print)
        if self.reporter is not None:
            worker.message.connect(self.reporter)
        if call_back is not None:
            worker.result.connect(call_back)

        # we keep references, else the objects would get killed when the method
        # is finished, which crashs the application:
        key = str(worker.objectName())
        self.workers[key] = worker

        def remove_reference():
            worker = self.workers[key]
            while worker.isRunning():
                time.sleep(0.001)
            del self.workers[key]

        worker.finished.connect(remove_reference)
        return worker

    def _schedule_waiting_cursor(self, worker, blocked):
        # if the worker runs more than 500 msec we set the cursor to WaitCursor,
        def set_waiting_cursor(worker=worker, blocked=blocked, parent=self.parent):
            print("set cursor", worker)
            try:
                if worker is not None and worker.isRunning():
                    parent.setCursor(Qt.WaitCursor)
                    if blocked:
                        parent.setEnabled(False)
            except RuntimeError:
                # happens if underlying c++ object is already killed
                pass

        def reset_cursor(parent=self.parent):
            print("reset cursor + unblock gui")
            parent.setCursor(Qt.ArrowCursor)
            parent.setEnabled(True)

        worker.finished.connect(reset_cursor)
        QTimer.singleShot(100, set_waiting_cursor)

    def run_async(self, function, args, call_back=None, blocked=False):
        worker = self._setup_worker(function, args, call_back)
        if self.parent is not None:
            self._schedule_waiting_cursor(worker, blocked)

        worker.start()


def run_in_background(*functions):
    class Bg(QThread):
        def run(self):
            try:
                for function in functions:
                    function()
            except Exception:
                import traceback

                traceback.print_exc()

    t = Bg()
    t.start()
    while not t.isFinished():
        QApplication.processEvents()
        time.sleep(0.01)


def block_and_run_in_background(parent, *functions):
    parent.setEnabled(False)
    parent.blockSignals(True)
    QApplication.setOverrideCursor(Qt.WaitCursor)

    run_in_background(
        *functions,
        partial(parent.blockSignals, False),
        partial(parent.setEnabled, True),
        partial(QApplication.setOverrideCursor, Qt.ArrowCursor),
    )


@contextmanager
def ui_blocked(parent):
    parent.setEnabled(False)
    parent.blockSignals(True)
    QApplication.setOverrideCursor(Qt.WaitCursor)
    QApplication.processEvents()
    try:
        yield
    finally:
        parent.setEnabled(True)
        parent.blockSignals(False)
        QApplication.setOverrideCursor(Qt.ArrowCursor)
