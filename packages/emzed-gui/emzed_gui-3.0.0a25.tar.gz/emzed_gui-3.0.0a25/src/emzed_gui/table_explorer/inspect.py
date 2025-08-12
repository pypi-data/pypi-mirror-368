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
from PyQt5.QtCore import Qt

from .table_explorer import TableExplorer


def inspect(
    what,
    offerAbortOption=False,
    modal=True,
    parent=None,
    close_callback=None,
    custom_buttons_config=None,
):
    """
    allows the inspection and editing of simple or multiple
    tables.

    """
    from emzed_gui import qapplication

    if isinstance(what, Table):
        what = [what]
    app = qapplication()  # noqa: F841
    explorer = TableExplorer(
        what,
        offerAbortOption,
        parent=parent,
        close_callback=close_callback,
        custom_buttons_config=custom_buttons_config,
    )
    if modal:
        explorer.setWindowModality(Qt.WindowModal)
        explorer.raise_()
        explorer.exec_()
        # partial cleanup
        modified = len(explorer.models[0].actions) > 0
        del explorer.models
        if offerAbortOption:
            if explorer.result == 1:
                raise Exception("Dialog aborted by user")
        return modified
    else:
        explorer.setWindowModality(Qt.NonModal)
        explorer.show()
        explorer.raise_()
    return explorer
