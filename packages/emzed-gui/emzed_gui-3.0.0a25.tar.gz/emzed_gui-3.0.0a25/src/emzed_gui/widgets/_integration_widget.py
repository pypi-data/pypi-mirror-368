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


class Ui_IntegrationWidget(object):
    def setupUi(self, _IntegrationWidget):
        _IntegrationWidget.setObjectName("_IntegrationWidget")
        _IntegrationWidget.setGeometry(QtCore.QRect(0, 0, 225, 154))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            _IntegrationWidget.sizePolicy().hasHeightForWidth()
        )
        _IntegrationWidget.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(_IntegrationWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self._frame = QtWidgets.QFrame(_IntegrationWidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._frame.sizePolicy().hasHeightForWidth())
        self._frame.setSizePolicy(sizePolicy)
        self._frame.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self._frame.setFrameShape(QtWidgets.QFrame.WinPanel)
        self._frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self._frame.setLineWidth(1)
        self._frame.setObjectName("_frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self._frame)
        self.verticalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self._label = QtWidgets.QLabel(self._frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._label.sizePolicy().hasHeightForWidth())
        self._label.setSizePolicy(sizePolicy)
        self._label.setMaximumSize(QtCore.QSize(250, 16777215))
        self._label.setFocusPolicy(QtCore.Qt.NoFocus)
        self._label.setObjectName("_label")
        self.verticalLayout_2.addWidget(self._label)
        self._methods = QtWidgets.QComboBox(self._frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._methods.sizePolicy().hasHeightForWidth())
        self._methods.setSizePolicy(sizePolicy)
        self._methods.setMaximumSize(QtCore.QSize(250, 16777215))
        self._methods.setFocusPolicy(QtCore.Qt.NoFocus)
        self._methods.setObjectName("_methods")
        self.verticalLayout_2.addWidget(self._methods)
        self._postfixes = QtWidgets.QComboBox(self._frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._postfixes.sizePolicy().hasHeightForWidth())
        self._postfixes.setSizePolicy(sizePolicy)
        self._postfixes.setMaximumSize(QtCore.QSize(250, 16777215))
        self._postfixes.setFocusPolicy(QtCore.Qt.NoFocus)
        self._postfixes.setObjectName("_postfixes")
        self.verticalLayout_2.addWidget(self._postfixes)
        self._compute_button = QtWidgets.QPushButton(self._frame)
        self._compute_button.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self._compute_button.sizePolicy().hasHeightForWidth()
        )
        self._compute_button.setSizePolicy(sizePolicy)
        self._compute_button.setMaximumSize(QtCore.QSize(250, 16777215))
        self._compute_button.setMouseTracking(False)
        self._compute_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self._compute_button.setObjectName("_compute_button")
        self.verticalLayout_2.addWidget(self._compute_button)
        self.gridLayout.addWidget(self._frame, 0, 0, 1, 1)

        self.retranslateUi(_IntegrationWidget)
        QtCore.QMetaObject.connectSlotsByName(_IntegrationWidget)

    def retranslateUi(self, _IntegrationWidget):
        _translate = QtCore.QCoreApplication.translate
        _IntegrationWidget.setWindowTitle(_translate("IntegrationWidget", "Form"))
        self._label.setText(_translate("IntegrationWidget", "Peak area computation"))
        self._compute_button.setText(_translate("IntegrationWidget", "Update area"))
