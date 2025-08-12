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


from PyQt5 import QtCore, QtWidgets


class Ui_ChooseSpectraWidget(object):
    def setupUi(self, _ChooseSpectraWidget):
        _ChooseSpectraWidget.setObjectName("_ChooseSpectraWidget")
        _ChooseSpectraWidget.setGeometry(QtCore.QRect(0, 0, 238, 307))
        _ChooseSpectraWidget.setMaximumSize(QtCore.QSize(250, 16777215))
        self.verticalLayout = QtWidgets.QVBoxLayout(_ChooseSpectraWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(_ChooseSpectraWidget)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self._label = QtWidgets.QLabel(self.frame)
        self._label.setObjectName("_label")
        self.verticalLayout_2.addWidget(self._label)
        self._spectra = QtWidgets.QListWidget(self.frame)
        self._spectra.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self._spectra.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self._spectra.setObjectName("_spectra")
        self.verticalLayout_2.addWidget(self._spectra)
        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(_ChooseSpectraWidget)
        QtCore.QMetaObject.connectSlotsByName(_ChooseSpectraWidget)

    def retranslateUi(self, _ChooseSpectraWidget):
        _translate = QtCore.QCoreApplication.translate
        _ChooseSpectraWidget.setWindowTitle(_translate("ChooseSpectraWidget", "Form"))
        self._label.setText(_translate("ChooseSpectraWidget", "Spectra:"))
