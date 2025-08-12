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


from emzed import Table
from emzed.ms_data import ImmutablePeakMap


def inspect(what, *args, **kwargs):
    if isinstance(what, (list, tuple)):
        from .table_explorer import inspect

        if all(isinstance(item, Table) for item in what):
            return inspect(what)
        else:
            raise ValueError("not all elements are tables")

    elif isinstance(what, Table):
        from .table_explorer import inspect

        inspect(what, *args, **kwargs)
    elif isinstance(what, ImmutablePeakMap):
        from .peakmap_explorer import inspect

        return inspect(what, *args, **kwargs)
    else:
        raise ValueError(f"don't know how to inspect object of type {type(what)}")
