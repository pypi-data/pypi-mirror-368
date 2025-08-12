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


from PyQt5.QtWidgets import QMessageBox


def show_warning(message, title="Warning"):
    """
    shows a warning dialog with given message
    """
    from emzed_gui import qapplication

    app = qapplication()
    QMessageBox.warning(None, title, message)


def show_information(message, title="Information"):
    """
    shows a information dialog with given message
    """
    from emzed_gui import qapplication

    app = qapplication()
    QMessageBox.information(None, title, message)


def ask_yes_no(message, allow_cancel=False, title="Question"):
    """shows message and asks for "yes" or "no" (or "cancel" if allow_cancel is True).
    returns True, False (or None).
    """
    from emzed_gui import qapplication

    app = qapplication()

    flags = QMessageBox.Yes | QMessageBox.No
    if allow_cancel:
        flags |= QMessageBox.Cancel

    reply = QMessageBox.question(None, title, message, flags)

    if reply == QMessageBox.Cancel:
        return None
    else:
        return reply == QMessageBox.Yes
