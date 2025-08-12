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


class Ui_ChooseValue(object):
    def setupUi(self, ChooseValue):
        ChooseValue.setObjectName("ChooseValue")
        ChooseValue.resize(260, 45)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ChooseValue.sizePolicy().hasHeightForWidth())
        ChooseValue.setSizePolicy(sizePolicy)
        ChooseValue.setMaximumSize(QtCore.QSize(300, 16777215))
        self.verticalLayout = QtWidgets.QVBoxLayout(ChooseValue)
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout.setSpacing(1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.column_name = QtWidgets.QLabel(ChooseValue)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.column_name.sizePolicy().hasHeightForWidth())
        self.column_name.setSizePolicy(sizePolicy)
        self.column_name.setAlignment(QtCore.Qt.AlignCenter)
        self.column_name.setObjectName("column_name")
        self.verticalLayout.addWidget(self.column_name)
        self.values = QtWidgets.QComboBox(ChooseValue)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.values.sizePolicy().hasHeightForWidth())
        self.values.setSizePolicy(sizePolicy)
        self.values.setObjectName("values")
        self.verticalLayout.addWidget(self.values)

        self.retranslateUi(ChooseValue)
        QtCore.QMetaObject.connectSlotsByName(ChooseValue)

    def retranslateUi(self, ChooseValue):
        _translate = QtCore.QCoreApplication.translate
        ChooseValue.setWindowTitle(_translate("ChooseValue", "Form"))
        self.column_name.setText(
            _translate("ChooseValue", "sadfsdfadsfasdfasdfasdfdsafadsfadsfdsf")
        )
