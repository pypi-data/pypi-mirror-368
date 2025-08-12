#!/usr/bin/env python


from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QPen
from PyQt5.QtWidgets import QStyle, QStyledItemDelegate


class TextDelegate(QStyledItemDelegate):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.model = model

    def paint(self, painter, option, index):
        selected = option.state & QStyle.State_Selected

        color = self.model.get_color(index)
        if selected:
            if color is None:
                color = QColor(225, 225, 235)
            color = QColor.fromHsvF(
                color.hueF(), color.saturationF() * 0.5, color.valueF()
            )

        if color is not None:
            painter.setPen(QPen(Qt.NoPen))
            painter.setBrush(QBrush(color))
            painter.drawRect(option.rect)

        painter.setPen(QPen(Qt.black))
        value = index.data(Qt.DisplayRole)
        painter.drawText(option.rect, Qt.AlignVCenter, "  " + value)
