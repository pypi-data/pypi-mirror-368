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


class Ui_StringFilter(object):
    def setupUi(self, StringFilter):
        StringFilter.setObjectName("StringFilter")
        StringFilter.resize(150, 44)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(StringFilter.sizePolicy().hasHeightForWidth())
        StringFilter.setSizePolicy(sizePolicy)
        StringFilter.setMaximumSize(QtCore.QSize(300, 16777215))
        self.verticalLayout = QtWidgets.QVBoxLayout(StringFilter)
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout.setSpacing(1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.column_name = QtWidgets.QLabel(StringFilter)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.column_name.sizePolicy().hasHeightForWidth())
        self.column_name.setSizePolicy(sizePolicy)
        self.column_name.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.column_name.setObjectName("column_name")
        self.verticalLayout.addWidget(self.column_name)
        self.pattern = QtWidgets.QLineEdit(StringFilter)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pattern.sizePolicy().hasHeightForWidth())
        self.pattern.setSizePolicy(sizePolicy)
        self.pattern.setMinimumSize(QtCore.QSize(100, 0))
        self.pattern.setObjectName("pattern")
        self.verticalLayout.addWidget(self.pattern)

        self.retranslateUi(StringFilter)
        QtCore.QMetaObject.connectSlotsByName(StringFilter)

    def retranslateUi(self, StringFilter):
        _translate = QtCore.QCoreApplication.translate
        StringFilter.setWindowTitle(_translate("StringFilter", "Form"))
        self.column_name.setText(_translate("StringFilter", "gtest"))
