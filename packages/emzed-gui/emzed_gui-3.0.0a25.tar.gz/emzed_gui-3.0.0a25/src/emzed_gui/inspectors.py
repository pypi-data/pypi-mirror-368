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

from emzed import PeakMap, Table


def has_inspector(clz):
    return clz in (PeakMap, Table)


def inspector(obj, *a, **kw):
    if isinstance(obj, PeakMap):
        from .peakmap_explorer import inspectPeakMap

        return lambda: inspectPeakMap(obj, *a, **kw)
    elif isinstance(obj, (Table)):
        from .table_explorer import inspect

        return lambda: inspect(obj, *a, **kw)
    elif isinstance(obj, (list, tuple)) and all(isinstance(t, Table) for t in obj):
        from .table_explorer import inspect

        return lambda: inspect(obj, *a, **kw)
    return None


def inspect(obj, *a, **kw):
    insp = inspector(obj, *a, **kw)
    if insp is not None:
        return insp()
    else:
        raise Exception("no inspector for %r" % obj)
