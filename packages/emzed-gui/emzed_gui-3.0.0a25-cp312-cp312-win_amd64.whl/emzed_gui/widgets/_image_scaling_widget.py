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


class Ui_ImageScalingWidget(object):
    def setupUi(self, _ImageScalingWidget):
        _ImageScalingWidget.setObjectName("_ImageScalingWidget")
        _ImageScalingWidget.setGeometry(QtCore.QRect(0, 0, 389, 92))
        self.gridLayout = QtWidgets.QGridLayout(_ImageScalingWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setVerticalSpacing(3)
        self.gridLayout.setObjectName("gridLayout")
        self._frame = QtWidgets.QFrame(_ImageScalingWidget)
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
        self._gridLayout_2 = QtWidgets.QGridLayout(self._frame)
        self._gridLayout_2.setVerticalSpacing(3)
        self._gridLayout_2.setObjectName("_gridLayout_2")
        self._label = QtWidgets.QLabel(self._frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._label.sizePolicy().hasHeightForWidth())
        self._label.setSizePolicy(sizePolicy)
        self._label.setObjectName("_label")
        self._gridLayout_2.addWidget(self._label, 0, 0, 1, 1)
        self._logarithmic_scale = QtWidgets.QCheckBox(self._frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self._logarithmic_scale.sizePolicy().hasHeightForWidth()
        )
        self._logarithmic_scale.setSizePolicy(sizePolicy)
        self._logarithmic_scale.setText("")
        self._logarithmic_scale.setObjectName("_logarithmic_scale")
        self._gridLayout_2.addWidget(self._logarithmic_scale, 0, 1, 1, 1)
        self._label_2 = QtWidgets.QLabel(self._frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._label_2.sizePolicy().hasHeightForWidth())
        self._label_2.setSizePolicy(sizePolicy)
        self._label_2.setObjectName("_label_2")
        self._gridLayout_2.addWidget(self._label_2, 0, 2, 1, 1)
        self._gamma_slider = QtWidgets.QSlider(self._frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self._gamma_slider.sizePolicy().hasHeightForWidth()
        )
        self._gamma_slider.setSizePolicy(sizePolicy)
        self._gamma_slider.setMinimumSize(QtCore.QSize(50, 0))
        self._gamma_slider.setOrientation(QtCore.Qt.Horizontal)
        self._gamma_slider.setObjectName("_gamma_slider")
        self._gridLayout_2.addWidget(self._gamma_slider, 0, 3, 1, 1)
        self._label_3 = QtWidgets.QLabel(self._frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._label_3.sizePolicy().hasHeightForWidth())
        self._label_3.setSizePolicy(sizePolicy)
        self._label_3.setObjectName("_label_3")
        self._gridLayout_2.addWidget(self._label_3, 1, 0, 1, 1)
        self._imin_input = QtWidgets.QLineEdit(self._frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._imin_input.sizePolicy().hasHeightForWidth())
        self._imin_input.setSizePolicy(sizePolicy)
        self._imin_input.setMinimumSize(QtCore.QSize(50, 0))
        self._imin_input.setObjectName("_imin_input")
        self._gridLayout_2.addWidget(self._imin_input, 2, 0, 1, 1)
        self._imin_slider = QtWidgets.QSlider(self._frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._imin_slider.sizePolicy().hasHeightForWidth())
        self._imin_slider.setSizePolicy(sizePolicy)
        self._imin_slider.setMinimumSize(QtCore.QSize(50, 0))
        self._imin_slider.setOrientation(QtCore.Qt.Horizontal)
        self._imin_slider.setObjectName("_imin_slider")
        self._gridLayout_2.addWidget(self._imin_slider, 2, 1, 1, 1)
        self._imax_slider = QtWidgets.QSlider(self._frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._imax_slider.sizePolicy().hasHeightForWidth())
        self._imax_slider.setSizePolicy(sizePolicy)
        self._imax_slider.setMinimumSize(QtCore.QSize(50, 0))
        self._imax_slider.setOrientation(QtCore.Qt.Horizontal)
        self._imax_slider.setObjectName("_imax_slider")
        self._gridLayout_2.addWidget(self._imax_slider, 2, 2, 1, 1)
        self._imax_input = QtWidgets.QLineEdit(self._frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._imax_input.sizePolicy().hasHeightForWidth())
        self._imax_input.setSizePolicy(sizePolicy)
        self._imax_input.setMinimumSize(QtCore.QSize(50, 0))
        self._imax_input.setObjectName("_imax_input")
        self._gridLayout_2.addWidget(self._imax_input, 2, 3, 1, 1)
        self.gridLayout.addWidget(self._frame, 0, 0, 1, 1)

        self.retranslateUi(_ImageScalingWidget)
        QtCore.QMetaObject.connectSlotsByName(_ImageScalingWidget)

    def retranslateUi(self, _ImageScalingWidget):
        _translate = QtCore.QCoreApplication.translate
        _ImageScalingWidget.setWindowTitle(_translate("ImageScalingWidget", "Form"))
        self._label.setText(_translate("ImageScalingWidget", "Logarithmic Scale"))
        self._label_2.setText(_translate("ImageScalingWidget", "Contrast"))
        self._label_3.setText(_translate("ImageScalingWidget", "Intensity:"))
