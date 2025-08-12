#!/usr/bin/env python

from ._ask_value_dialog import QtCore, QtGui, QtWidgets, Ui_AskValueDialog


class AskValueDialogBase(QtWidgets.QDialog):
    def __init__(self, col_name, parent=None):
        super().__init__(parent=parent)

        self.canceled = True
        self.value = None

        self.setup_ui(col_name)
        self.connect_signals()
        self.setup_buttons()

    def setup_ui(self, col_name):
        self.ui = Ui_AskValueDialog()
        self.ui.setupUi(self)
        self.ui.label.setText(f"set value for {col_name}")

    def connect_signals(self):
        self.ui.set_to_input.toggled.connect(lambda t: self.ui.input.setEnabled(t))
        self.ui.set_to_input.toggled.connect(lambda t: self.check_value())

        self.ui.set_to_none.toggled.connect(lambda t: self.ui.input.setEnabled(not t))
        self.ui.set_to_none.toggled.connect(lambda t: self.ok_button.setEnabled(True))

        self.accepted.connect(self.accept)
        self._extra_connect()

    def _extra_connect(self):
        self.ui.input.textEdited.connect(self.check_value)

    def setup_buttons(self):
        ok_button, cancel_button = self.ui.buttonBox.buttons()
        ok_button.setAutoDefault(False)
        ok_button.setDefault(False)
        cancel_button.setAutoDefault(False)
        cancel_button.setDefault(True)
        self.ok_button = ok_button
        self.check_value()

    def accept(self):
        self.canceled = False
        if self.ui.set_to_none.isChecked():
            self.value = None
        else:
            self.value = self.determine_value()
        self.close()

    def check_value(self, *_):
        self.ok_button.setEnabled(self.valid_input(self.ui.input.text()))

    def valid_input(self, value):
        raise NotImplementedError

    def determine_value(self):
        raise NotImplementedError


class AskBoolValue(AskValueDialogBase):
    def setup_ui(self, col_name):
        super().setup_ui(col_name)
        input_ = QtWidgets.QComboBox(self.ui.widget)
        input_.addItem("True")
        input_.addItem("False")
        self.ui.horizontalLayout.replaceWidget(self.ui.input, input_)
        self.ui.input.setVisible(False)
        self.ui.input = input_

    def _extra_connect(self):
        pass

    def check_value(self, *_):
        self.ok_button.setEnabled(True)

    def determine_value(self):
        return self.ui.input.currentIndex() == 0


class AskRtValue(AskValueDialogBase):
    def valid_input(self, value):
        value = value.strip().rstrip("m")
        try:
            float(value)
        except ValueError:
            return False
        else:
            return True

    def determine_value(self):
        text = self.ui.input.text().strip()
        if text.endswith("m"):
            return float(text[:-1]) * 60
        return float(text)


class AskIntValue(AskValueDialogBase):
    def valid_input(self, value):
        value = value.strip()
        try:
            value = int(value)
        except ValueError:
            return False
        else:
            return True

    def determine_value(self):
        return float(self.ui.input.text().strip())


class AskFloatValue(AskValueDialogBase):
    def valid_input(self, value):
        value = value.strip()
        try:
            value = float(value)
        except ValueError:
            return False
        else:
            return True

    def determine_value(self):
        return float(self.ui.input.text().strip())


class AskMzValue(AskFloatValue):
    def valid_input(self, value):
        value = value.strip()
        try:
            value = float(value)
        except ValueError:
            return False
        else:
            return value > 0


class AskStrValue(AskValueDialogBase):
    def valid_input(self, value):
        return True

    def determine_value(self):
        return self.ui.input.text().strip()
