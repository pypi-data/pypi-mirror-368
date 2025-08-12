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


class Ui_ViewRangeWidget(object):
    def setupUi(self, _ViewRangeWidget):
        _ViewRangeWidget.setObjectName("_ViewRangeWidget")
        _ViewRangeWidget.setGeometry(QtCore.QRect(0, 0, 387, 138))
        self._gridLayout = QtWidgets.QGridLayout(_ViewRangeWidget)
        self._gridLayout.setContentsMargins(0, 0, 0, 0)
        self._gridLayout.setObjectName("_gridLayout")
        self._frame = QtWidgets.QFrame(_ViewRangeWidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._frame.sizePolicy().hasHeightForWidth())
        self._frame.setSizePolicy(sizePolicy)
        self._frame.setMinimumSize(QtCore.QSize(387, 0))
        self._frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self._frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self._frame.setObjectName("_frame")
        self._gridLayout_2 = QtWidgets.QGridLayout(self._frame)
        self._gridLayout_2.setContentsMargins(5, 5, 5, 5)
        self._gridLayout_2.setVerticalSpacing(3)
        self._gridLayout_2.setObjectName("_gridLayout_2")
        self._label = QtWidgets.QLabel(self._frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._label.sizePolicy().hasHeightForWidth())
        self._label.setSizePolicy(sizePolicy)
        self._label.setMinimumSize(QtCore.QSize(371, 0))
        self._label.setBaseSize(QtCore.QSize(0, 0))
        self._label.setObjectName("_label")
        self._gridLayout_2.addWidget(self._label, 0, 0, 1, 2)
        self._rt_min = QtWidgets.QLineEdit(self._frame)
        self._rt_min.setMinimumSize(QtCore.QSize(181, 0))
        self._rt_min.setText("")
        self._rt_min.setObjectName("_rt_min")
        self._gridLayout_2.addWidget(self._rt_min, 1, 0, 1, 1)
        self._rt_max = QtWidgets.QLineEdit(self._frame)
        self._rt_max.setMinimumSize(QtCore.QSize(180, 0))
        self._rt_max.setText("")
        self._rt_max.setObjectName("_rt_max")
        self._gridLayout_2.addWidget(self._rt_max, 1, 1, 1, 1)
        self._label_2 = QtWidgets.QLabel(self._frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._label_2.sizePolicy().hasHeightForWidth())
        self._label_2.setSizePolicy(sizePolicy)
        self._label_2.setMinimumSize(QtCore.QSize(181, 0))
        self._label_2.setObjectName("_label_2")
        self._gridLayout_2.addWidget(self._label_2, 2, 0, 1, 1)
        self._use_ppm = QtWidgets.QCheckBox(self._frame)
        self._use_ppm.setMinimumSize(QtCore.QSize(191, 0))
        self._use_ppm.setObjectName("_use_ppm")
        self._gridLayout_2.addWidget(self._use_ppm, 2, 1, 1, 1)
        self._mz_center = QtWidgets.QLineEdit(self._frame)
        self._mz_center.setMinimumSize(QtCore.QSize(181, 0))
        self._mz_center.setText("")
        self._mz_center.setObjectName("_mz_center")
        self._gridLayout_2.addWidget(self._mz_center, 3, 0, 1, 1)
        self._mz_width = QtWidgets.QLineEdit(self._frame)
        self._mz_width.setMinimumSize(QtCore.QSize(180, 0))
        self._mz_width.setText("")
        self._mz_width.setObjectName("_mz_width")
        self._gridLayout_2.addWidget(self._mz_width, 3, 1, 1, 1)
        self._label_4 = QtWidgets.QLabel(self._frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._label_4.sizePolicy().hasHeightForWidth())
        self._label_4.setSizePolicy(sizePolicy)
        self._label_4.setMinimumSize(QtCore.QSize(181, 0))
        self._label_4.setObjectName("_label_4")
        self._gridLayout_2.addWidget(self._label_4, 4, 0, 1, 1)
        self._mz_min = QtWidgets.QLineEdit(self._frame)
        self._mz_min.setMinimumSize(QtCore.QSize(181, 0))
        self._mz_min.setText("")
        self._mz_min.setObjectName("_mz_min")
        self._gridLayout_2.addWidget(self._mz_min, 5, 0, 1, 1)
        self._mz_max = QtWidgets.QLineEdit(self._frame)
        self._mz_max.setMinimumSize(QtCore.QSize(180, 0))
        self._mz_max.setText("")
        self._mz_max.setObjectName("_mz_max")
        self._gridLayout_2.addWidget(self._mz_max, 5, 1, 1, 1)
        self._gridLayout.addWidget(self._frame, 3, 1, 1, 1)

        self.retranslateUi(_ViewRangeWidget)
        QtCore.QMetaObject.connectSlotsByName(_ViewRangeWidget)

    def retranslateUi(self, _ViewRangeWidget):
        _translate = QtCore.QCoreApplication.translate
        _ViewRangeWidget.setWindowTitle(_translate("ViewRangeWidget", "Form"))
        self._label.setText(
            _translate("ViewRangeWidget", "Retention time range [minutes]")
        )
        self._label_2.setText(
            _translate("ViewRangeWidget", "m/z center and half width")
        )
        self._use_ppm.setText(_translate("ViewRangeWidget", "use ppm ?"))
        self._label_4.setText(_translate("ViewRangeWidget", "m/z range"))
