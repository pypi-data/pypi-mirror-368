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


class Ui_SpectraSelectorWidget(object):
    def setupUi(self, _SpectraSelectorWidget):
        _SpectraSelectorWidget.setObjectName("_SpectraSelectorWidget")
        _SpectraSelectorWidget.setGeometry(QtCore.QRect(0, 0, 275, 118))
        self._horizontalLayout = QtWidgets.QHBoxLayout(_SpectraSelectorWidget)
        self._horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self._horizontalLayout.setObjectName("_horizontalLayout")
        self._frame = QtWidgets.QFrame(_SpectraSelectorWidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._frame.sizePolicy().hasHeightForWidth())
        self._frame.setSizePolicy(sizePolicy)
        self._frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self._frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self._frame.setObjectName("_frame")
        self._gridLayout = QtWidgets.QGridLayout(self._frame)
        self._gridLayout.setHorizontalSpacing(10)
        self._gridLayout.setVerticalSpacing(3)
        self._gridLayout.setObjectName("_gridLayout")
        self._label_2 = QtWidgets.QLabel(self._frame)
        self._label_2.setObjectName("_label_2")
        self._gridLayout.addWidget(self._label_2, 1, 0, 1, 1)
        self._precursor = QtWidgets.QComboBox(self._frame)
        self._precursor.setObjectName("_precursor")
        self._gridLayout.addWidget(self._precursor, 1, 1, 1, 1)
        self._ms_level = QtWidgets.QComboBox(self._frame)
        self._ms_level.setObjectName("_ms_level")
        self._gridLayout.addWidget(self._ms_level, 0, 1, 1, 1)
        self._label = QtWidgets.QLabel(self._frame)
        self._label.setObjectName("_label")
        self._gridLayout.addWidget(self._label, 0, 0, 1, 1)
        self._label_3 = QtWidgets.QLabel(self._frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._label_3.sizePolicy().hasHeightForWidth())
        self._label_3.setSizePolicy(sizePolicy)
        self._label_3.setObjectName("_label_3")
        self._gridLayout.addWidget(self._label_3, 2, 0, 1, 1)
        self._precursor_max = QtWidgets.QLineEdit(self._frame)
        self._precursor_max.setObjectName("_precursor_max")
        self._gridLayout.addWidget(self._precursor_max, 3, 1, 1, 1)
        self._precursor_min = QtWidgets.QLineEdit(self._frame)
        self._precursor_min.setObjectName("_precursor_min")
        self._gridLayout.addWidget(self._precursor_min, 3, 0, 1, 1)
        self._horizontalLayout.addWidget(self._frame)

        self.retranslateUi(_SpectraSelectorWidget)
        QtCore.QMetaObject.connectSlotsByName(_SpectraSelectorWidget)

    def retranslateUi(self, _SpectraSelectorWidget):
        _translate = QtCore.QCoreApplication.translate
        _SpectraSelectorWidget.setWindowTitle(
            _translate("SpectraSelectorWidget", "Form")
        )
        self._label_2.setText(_translate("SpectraSelectorWidget", "Choose Precursor"))
        self._label.setText(_translate("SpectraSelectorWidget", "Choose MS Level"))
        self._label_3.setText(
            _translate("SpectraSelectorWidget", "m/z Range Precursor")
        )
