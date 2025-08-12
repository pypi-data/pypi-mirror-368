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


from guiqwt.config import CONF


def setupCommonStyle(line, marker):
    markerSymbol = (
        "Ellipse"  # in this case a circle, because we give only one size parameter.
    )
    edgeColor = "#555555"
    faceColor = "#cc0000"
    alpha = 0.8
    size = 6
    params = {
        "marker/cross/symbol/marker": markerSymbol,
        "marker/cross/symbol/edgecolor": edgeColor,
        "marker/cross/symbol/facecolor": faceColor,
        "marker/cross/symbol/alpha": alpha,
        "marker/cross/symbol/size": size,
        "marker/cross/line/color": "#000000",
        # "marker/cross/line/width": 0.0,
        "marker/cross/line/style": "NoPen",
    }
    CONF.update_defaults(dict(plot=params))
    marker.markerparam.read_config(CONF, "plot", "marker/cross")
    marker.markerparam.update_marker(marker)
    params = {
        "shape/drag/symbol/marker": markerSymbol,
        "shape/drag/symbol/size": size,
        "shape/drag/symbol/edgecolor": edgeColor,
        "shape/drag/symbol/facecolor": faceColor,
        "shape/drag/symbol/alpha": alpha,
    }
    CONF.update_defaults(dict(plot=params))
    line.shapeparam.read_config(CONF, "plot", "shape/drag")
    line.shapeparam.update_shape(line)


def setupStyleRtMarker(marker):
    linecolor = "#909090"
    edgeColor = "#005500"
    faceColor = "#005500"
    params = {
        "marker/cross/symbol/marker": "Rect",
        "marker/cross/symbol/size": 0,
        "marker/cross/symbol/edgecolor": edgeColor,
        "marker/cross/symbol/facecolor": faceColor,
        "marker/cross/line/color": linecolor,
        "marker/cross/line/width": 1.0,
        "marker/cross/line/style": "SolidLine",
        "marker/cross/sel_symbol/size": 0,
        "marker/cross/sel_line/color": linecolor,
        "marker/cross/sel_line/width": 1.0,
        "marker/cross/sel_line/style": "SolidLine",
    }
    CONF.update_defaults(dict(plot=params))
    marker.markerparam.read_config(CONF, "plot", "marker/cross")
    marker.markerparam.update_marker(marker)
