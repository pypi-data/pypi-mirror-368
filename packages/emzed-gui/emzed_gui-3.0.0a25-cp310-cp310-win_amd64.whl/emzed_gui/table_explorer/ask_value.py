#!/usr/bin/env python
from emzed import MzType, RtType

from emzed_gui.widgets import (
    AskBoolValue,
    AskFloatValue,
    AskIntValue,
    AskMzValue,
    AskRtValue,
    AskStrValue,
)


def ask_value(col_name, col_type, parent=None):
    dlg_class = {
        float: AskFloatValue,
        int: AskIntValue,
        bool: AskBoolValue,
        str: AskStrValue,
        RtType: AskRtValue,
        MzType: AskMzValue,
    }.get(col_type)

    if dlg_class is None:
        raise RuntimeError(f"type {col_type} not supported")

    dlg = dlg_class(col_name, parent)
    dlg.adjustSize()
    dlg.exec_()

    return dlg.canceled, dlg.value
