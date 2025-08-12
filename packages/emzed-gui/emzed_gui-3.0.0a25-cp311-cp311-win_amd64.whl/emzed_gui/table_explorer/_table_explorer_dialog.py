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


#
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets

from .eic_plotting_widget import EicPlottingWidget
from .mz_plotting_widget import MzPlottingWidget
from .widgets.choose_spectra_widget import ChooseSpectraWidget
from .widgets.integration_widget import IntegrationWidget


class Ui__TableExporerDialog(object):
    def setupUi(self, _TableExporerDialog):
        _TableExporerDialog.setObjectName("_TableExporerDialog")
        _TableExporerDialog.resize(777, 531)
        self.gridLayout = QtWidgets.QGridLayout(_TableExporerDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.mz_plotter = MzPlottingWidget(_TableExporerDialog)
        self.mz_plotter.setObjectName("mz_plotter")
        self.gridLayout.addWidget(self.mz_plotter, 0, 2, 3, 1)
        self.eic_plotter = EicPlottingWidget(_TableExporerDialog)
        self.eic_plotter.setObjectName("eic_plotter")
        self.gridLayout.addWidget(self.eic_plotter, 0, 0, 3, 1)
        self.choose_spectra_widget = ChooseSpectraWidget(_TableExporerDialog)
        self.choose_spectra_widget.setObjectName("choose_spectra_widget")
        self.gridLayout.addWidget(self.choose_spectra_widget, 1, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.gridLayout.addItem(spacerItem, 2, 1, 1, 1)
        self.integration_widget = IntegrationWidget(_TableExporerDialog)
        self.integration_widget.setObjectName("integration_widget")
        self.gridLayout.addWidget(self.integration_widget, 0, 1, 1, 1)
        self.tableView = QtWidgets.QTableView(_TableExporerDialog)
        self.tableView.setObjectName("tableView")
        self.gridLayout.addWidget(self.tableView, 3, 0, 1, 3)

        self.retranslateUi(_TableExporerDialog)
        QtCore.QMetaObject.connectSlotsByName(_TableExporerDialog)

    def retranslateUi(self, _TableExporerDialog):
        _translate = QtCore.QCoreApplication.translate
        _TableExporerDialog.setWindowTitle(_translate("_TableExporerDialog", "Dialog"))
