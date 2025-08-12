# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ask_value_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AskValueDialog(object):
    def setupUi(self, AskValueDialog):
        AskValueDialog.setObjectName("AskValueDialog")
        # AskValueDialog.resize(190, 140)
        AskValueDialog.setWindowFlags(QtCore.Qt.Window)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(AskValueDialog.sizePolicy().hasHeightForWidth())
        AskValueDialog.setSizePolicy(sizePolicy)
        AskValueDialog.setSizeGripEnabled(False)
        self.widget = QtWidgets.QWidget(AskValueDialog)
        self.widget.setGeometry(QtCore.QRect(6, 12, 151, 91))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        AskValueDialog.setLayout(self.verticalLayout)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)
        # self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        # self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setEnabled(True)
        self.label.setText("please set")
        self.verticalLayout.addWidget(self.label)

        self.set_to_input = QtWidgets.QRadioButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.set_to_input.sizePolicy().hasHeightForWidth())
        self.set_to_input.setSizePolicy(sizePolicy)
        self.set_to_input.setText("")
        self.set_to_input.setChecked(True)
        self.set_to_input.setObjectName("set_to_input")
        self.horizontalLayout.addWidget(self.set_to_input)
        self.input = QtWidgets.QLineEdit(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.input.sizePolicy().hasHeightForWidth())
        self.input.setSizePolicy(sizePolicy)
        self.input.setMinimumSize(QtCore.QSize(0, 25))
        self.input.setObjectName("input")
        self.horizontalLayout.addWidget(self.input)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.set_to_none = QtWidgets.QRadioButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.set_to_none.sizePolicy().hasHeightForWidth())
        self.set_to_none.setSizePolicy(sizePolicy)
        self.set_to_none.setText("")
        self.set_to_none.setObjectName("set_to_none")
        self.horizontalLayout_2.addWidget(self.set_to_none)
        self.label_none = QtWidgets.QLabel(self.widget)
        self.label_none.setEnabled(True)
        self.label_none.setMinimumSize(QtCore.QSize(0, 0))
        self.label_none.setIndent(2)
        self.label_none.setObjectName("label_none")
        self.horizontalLayout_2.addWidget(self.label_none)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.widget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(AskValueDialog)
        self.buttonBox.rejected.connect(AskValueDialog.reject)
        self.buttonBox.accepted.connect(AskValueDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(AskValueDialog)

    def retranslateUi(self, AskValueDialog):
        _translate = QtCore.QCoreApplication.translate
        AskValueDialog.setWindowTitle(_translate("AskValueDialog", "Set Value"))
        self.label_none.setText(_translate("AskValueDialog", "None"))
