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


class Ui_FilterCriteriaWidget:
    def setupUi(self, _FilterCriteriaWidget):
        _FilterCriteriaWidget.setObjectName("_FilterCriteriaWidget")
        _FilterCriteriaWidget.setGeometry(QtCore.QRect(0, 0, 291, 200))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(
            _FilterCriteriaWidget.sizePolicy().hasHeightForWidth()
        )
        _FilterCriteriaWidget.setSizePolicy(sizePolicy)
        _FilterCriteriaWidget.setMinimumSize(QtCore.QSize(100, 0))
        self._verticalLayout = QtWidgets.QVBoxLayout(_FilterCriteriaWidget)
        self._verticalLayout.setContentsMargins(3, 3, 3, 3)
        self._verticalLayout.setSpacing(1)
        self._verticalLayout.setObjectName("_verticalLayout")
        self._scrollArea = QtWidgets.QScrollArea(_FilterCriteriaWidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._scrollArea.sizePolicy().hasHeightForWidth())
        self._scrollArea.setSizePolicy(sizePolicy)
        self._scrollArea.setMinimumSize(QtCore.QSize(0, 90))
        self._scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self._scrollArea.setFrameShadow(QtWidgets.QFrame.Plain)
        self._scrollArea.setLineWidth(0)
        self._scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._scrollArea.setWidgetResizable(True)
        self._scrollArea.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop
        )
        self._scrollArea.setObjectName("_scrollArea")
        self._widgets = QtWidgets.QWidget()
        self._widgets.setGeometry(QtCore.QRect(0, 0, 285, 194))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._widgets.sizePolicy().hasHeightForWidth())
        self._widgets.setSizePolicy(sizePolicy)
        self._widgets.setObjectName("_widgets")
        self._hlayout = QtWidgets.QHBoxLayout(self._widgets)
        self._hlayout.setContentsMargins(0, 0, 0, 0)
        self._hlayout.setObjectName("_hlayout")
        self._scrollArea.setWidget(self._widgets)
        self._verticalLayout.addWidget(self._scrollArea)

        self.retranslateUi(_FilterCriteriaWidget)
        QtCore.QMetaObject.connectSlotsByName(_FilterCriteriaWidget)

    def retranslateUi(self, _FilterCriteriaWidget):
        _translate = QtCore.QCoreApplication.translate
        _FilterCriteriaWidget.setWindowTitle(_translate("FilterCriteriaWidget", "Form"))
