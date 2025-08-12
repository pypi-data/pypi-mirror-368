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


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
)


class TableExplorerLayout:
    def setupLayout(self):
        vlayout = QVBoxLayout()
        self.setLayout(vlayout)

        vsplitter = QSplitter()
        vsplitter.setOrientation(Qt.Vertical)
        vsplitter.setOpaqueResize(False)

        vsplitter.addWidget(self.menubar)  # 0
        vsplitter.addWidget(self.layoutPlottingAndIntegrationWidgets())  # 1

        self.table_view_container = QStackedWidget(self)
        for view in self.tableViews:
            self.table_view_container.addWidget(view)

        vsplitter.addWidget(self.table_view_container)  # 2

        vsplitter.addWidget(self.layoutToolWidgets())  # 3

        # self.filter_widgets_box = QScrollArea(self)
        self.filter_widgets_container = QStackedWidget(self)
        sizePolicy = QSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding
        )
        self.filter_widgets_container.setSizePolicy(sizePolicy)
        for w in self.filterWidgets:
            self.filter_widgets_container.addWidget(w)

        self.filter_widgets_container.setVisible(False)
        self.filter_widgets_container.setFrameStyle(QFrame.Plain)
        vsplitter.addWidget(self.filter_widgets_container)

        di = 0

        vsplitter.setStretchFactor(0, 1)  # menubar
        vsplitter.setStretchFactor(1, 3)  # plots + integration
        vsplitter.setStretchFactor(2 + di, 5)  # table
        vsplitter.setStretchFactor(3 + di, 1)  # tools
        vsplitter.setStretchFactor(4 + di, 2)  # filters

        vlayout.addWidget(vsplitter)

        if self.offerAbortOption:
            vlayout.addLayout(self.layoutButtons())

    def layoutButtons(self):
        hbox = QHBoxLayout()
        hbox.addWidget(self.abort_button)
        hbox.setAlignment(self.abort_button, Qt.AlignVCenter)
        hbox.addWidget(self.ok_button)
        hbox.setAlignment(self.ok_button, Qt.AlignVCenter)
        return hbox

    def layoutPlottingAndIntegrationWidgets(self):
        hsplitter = QSplitter()
        hsplitter.setOpaqueResize(False)

        middleLayout = QVBoxLayout()
        middleLayout.setSpacing(5)
        middleLayout.setContentsMargins(5, 5, 5, 5)
        middleLayout.addWidget(self.integration_widget)
        middleLayout.addStretch()

        middleLayout.addWidget(self.spec_label)
        middleLayout.addWidget(self.choose_spec)
        middleLayout.addStretch()
        middleLayout.addStretch()

        self.middleFrame = QFrame()
        self.middleFrame.setLayout(middleLayout)
        self.middleFrame.setMaximumWidth(250)

        for widget in (self.eic_plotter, self.middleFrame, self.mz_plotter):
            hsplitter.addWidget(widget)
        return hsplitter

    def layoutToolWidgets(self):
        frame = QFrame(parent=self)
        layout = QGridLayout()
        row = 0
        column = 0
        layout.addWidget(self.chooseGroubLabel, row, column, alignment=Qt.AlignLeft)
        column += 1
        layout.addWidget(self.chooseGroupColumn, row, column, alignment=Qt.AlignLeft)
        column += 1
        layout.addWidget(
            self.choose_visible_columns_button, row, column, alignment=Qt.AlignLeft
        )

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.sort_label)

        for sort_field_w, sort_order_w in zip(
            self.sort_fields_widgets, self.sort_order_widgets
        ):
            h_layout.addWidget(sort_field_w)
            h_layout.addWidget(sort_order_w)

        column += 1
        # rowspan:1 colspan:9, 9 shoud be enough for a reasonable number of custom
        # buttons
        layout.addLayout(h_layout, row, column, 1, 9, alignment=Qt.AlignLeft)

        row = 1
        column = 0
        layout.addWidget(self.filter_on_button, row, column, alignment=Qt.AlignLeft)
        column += 1
        layout.addWidget(
            self.restrict_to_filtered_button, row, column, alignment=Qt.AlignLeft
        )
        column += 1
        layout.addWidget(
            self.remove_filtered_button, row, column, alignment=Qt.AlignLeft
        )
        column += 1
        layout.addWidget(self.export_table_button, row, column, alignment=Qt.AlignLeft)
        column += 1

        if self.extra_buttons:
            layout.addWidget(
                QLabel("Custom actions:"), row, column, alignment=Qt.AlignRight
            )
            column += 1

        for button in self.extra_buttons:
            layout.addWidget(button, row, column, alignment=Qt.AlignLeft)
            column += 1

        layout.setColumnStretch(column, 1)
        layout.setVerticalSpacing(2)

        frame.setLayout(layout)
        return frame
