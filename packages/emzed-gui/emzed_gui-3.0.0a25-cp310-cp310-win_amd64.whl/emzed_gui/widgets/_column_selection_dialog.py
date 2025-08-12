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


class Ui_ColumnMultiSelectDialog(object):
    def setupUi(self, ColumnMultiSelectDialog):
        ColumnMultiSelectDialog.setObjectName("ColumnMultiSelectDialog")
        ColumnMultiSelectDialog.resize(150, 110)
        ColumnMultiSelectDialog.setMinimumSize(QtCore.QSize(150, 110))
        ColumnMultiSelectDialog.setSizeGripEnabled(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(ColumnMultiSelectDialog)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.column_names = QtWidgets.QListView(ColumnMultiSelectDialog)
        self.column_names.setMinimumSize(QtCore.QSize(150, 0))
        self.column_names.setFocusPolicy(QtCore.Qt.NoFocus)
        self.column_names.setViewMode(QtWidgets.QListView.ListMode)
        self.column_names.setObjectName("column_names")
        self.verticalLayout.addWidget(self.column_names)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.apply_button = QtWidgets.QPushButton(ColumnMultiSelectDialog)
        self.apply_button.setAutoDefault(False)
        self.apply_button.setObjectName("apply_button")
        self.horizontalLayout.addWidget(self.apply_button)
        self.cancel_button = QtWidgets.QPushButton(ColumnMultiSelectDialog)
        self.cancel_button.setAutoDefault(False)
        self.cancel_button.setObjectName("cancel_button")
        self.horizontalLayout.addWidget(self.cancel_button)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ColumnMultiSelectDialog)
        QtCore.QMetaObject.connectSlotsByName(ColumnMultiSelectDialog)

    def retranslateUi(self, ColumnMultiSelectDialog):
        _translate = QtCore.QCoreApplication.translate
        ColumnMultiSelectDialog.setWindowTitle(
            _translate("ColumnMultiSelectDialog", "Select Columns")
        )
        self.apply_button.setText(_translate("ColumnMultiSelectDialog", "Apply"))
        self.cancel_button.setText(_translate("ColumnMultiSelectDialog", "Cancel"))
