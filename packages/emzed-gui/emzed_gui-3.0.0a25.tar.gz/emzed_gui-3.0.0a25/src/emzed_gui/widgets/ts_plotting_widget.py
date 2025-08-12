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


from datetime import datetime

from emzed_gui.helpers import set_datetime_formating_on_x_axis

from .eic_plotting_widget import EicPlottingWidget, ObjectInfo, getColor
from .modified_guiqwt import make_unselectable_curve


class DateTimeCursorInfo(ObjectInfo):
    def __init__(self, marker):
        ObjectInfo.__init__(self)
        self.marker = marker

    def get_text(self):
        ordinal = int(self.marker.xValue())
        if ordinal > 0:
            txt = "<pre>%s</pre>" % datetime.fromordinal(ordinal)
            return txt
        else:
            return ""


class TimeSeriesPlottingWidget(EicPlottingWidget):
    def __init__(self, parent=None):
        super(TimeSeriesPlottingWidget, self).__init__(parent, with_range=False)

    def _setup_axes(self):
        set_datetime_formating_on_x_axis(self.plot)
        self.plot.set_axis_title("bottom", "date/time")

    def _setup_cursor_info(self, marker):
        self.cursor_info = DateTimeCursorInfo(marker)

    def add_time_series(self, time_series, configs=None):
        seen = set()
        x_values = []
        labels = []
        items_with_label = []
        for i, ts in enumerate(time_series):
            # we do not plot duplicates, which might happen if multiple lines in the
            # table explorer are sellected !
            if ts.uniqueId() in seen:
                continue
            seen.add(ts.uniqueId())
            config = None
            if configs is not None:
                config = configs[i]
            if config is None:
                config = dict(color=getColor(i))
            title = ts.label
            for j, item in enumerate(ts.for_plotting()):
                lconfig = config.copy()
                if len(item) == 2:
                    x, y = item
                else:
                    x, y, special_config = item
                    lconfig.update(special_config)
                x = [xi.toordinal() if isinstance(xi, datetime) else xi for xi in x]
                x_values.extend(x)
                curve = make_unselectable_curve(
                    x, y, title="<pre>%s</pre>" % title, **lconfig
                )
                self.plot.add_item(curve)
                if j == 0:
                    labels.append(title)
                    items_with_label.append(curve)

        x_values = sorted(set(x_values))
        self.plot.set_x_values(x_values)
        self.plot.add_item(self.marker)
        self.plot.add_item(self.label)

        unique_labels = set(labels)
        self._add_legend(unique_labels, items_with_label)
