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


class Ui_ChooseRange(object):
    def setupUi(self, ChooseRange):
        ChooseRange.setObjectName("ChooseRange")
        ChooseRange.resize(141, 70)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ChooseRange.sizePolicy().hasHeightForWidth())
        ChooseRange.setSizePolicy(sizePolicy)
        ChooseRange.setMaximumSize(QtCore.QSize(400, 16777215))
        self.gridLayout = QtWidgets.QGridLayout(ChooseRange)
        self.gridLayout.setContentsMargins(3, 3, 3, 3)
        self.gridLayout.setHorizontalSpacing(1)
        self.gridLayout.setVerticalSpacing(3)
        self.gridLayout.setObjectName("gridLayout")
        self.column_name = QtWidgets.QLabel(ChooseRange)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.column_name.sizePolicy().hasHeightForWidth())
        self.column_name.setSizePolicy(sizePolicy)
        self.column_name.setAlignment(QtCore.Qt.AlignCenter)
        self.column_name.setObjectName("column_name")
        self.gridLayout.addWidget(self.column_name, 0, 2, 1, 1)
        self.lower_bound = QtWidgets.QLineEdit(ChooseRange)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lower_bound.sizePolicy().hasHeightForWidth())
        self.lower_bound.setSizePolicy(sizePolicy)
        self.lower_bound.setMinimumSize(QtCore.QSize(100, 0))
        self.lower_bound.setObjectName("lower_bound")
        self.gridLayout.addWidget(self.lower_bound, 1, 2, 1, 3)
        self.label_lower_bound = QtWidgets.QLabel(ChooseRange)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Ignored
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_lower_bound.sizePolicy().hasHeightForWidth()
        )
        self.label_lower_bound.setSizePolicy(sizePolicy)
        self.label_lower_bound.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        self.label_lower_bound.setObjectName("label_lower_bound")
        self.gridLayout.addWidget(self.label_lower_bound, 1, 0, 1, 1)
        self.label_upper_bound = QtWidgets.QLabel(ChooseRange)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Ignored
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_upper_bound.sizePolicy().hasHeightForWidth()
        )
        self.label_upper_bound.setSizePolicy(sizePolicy)
        self.label_upper_bound.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        self.label_upper_bound.setObjectName("label_upper_bound")
        self.gridLayout.addWidget(self.label_upper_bound, 2, 0, 1, 1)
        self.upper_bound = QtWidgets.QLineEdit(ChooseRange)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.upper_bound.sizePolicy().hasHeightForWidth())
        self.upper_bound.setSizePolicy(sizePolicy)
        self.upper_bound.setMinimumSize(QtCore.QSize(100, 0))
        self.upper_bound.setObjectName("upper_bound")
        self.gridLayout.addWidget(self.upper_bound, 2, 2, 1, 3)

        self.retranslateUi(ChooseRange)
        QtCore.QMetaObject.connectSlotsByName(ChooseRange)
        ChooseRange.setTabOrder(self.lower_bound, self.upper_bound)

    def retranslateUi(self, ChooseRange):
        _translate = QtCore.QCoreApplication.translate
        ChooseRange.setWindowTitle(_translate("ChooseRange", "Form"))
        self.column_name.setText(_translate("ChooseRange", "dsffdsf"))
        self.label_lower_bound.setText(_translate("ChooseRange", "min:"))
        self.label_upper_bound.setText(_translate("ChooseRange", "max:"))
