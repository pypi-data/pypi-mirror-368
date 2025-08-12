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


import colorsys

import matplotlib

colors = matplotlib.colormaps.get_cmap("tab10").colors


def get_color(i, brightened=False):
    c = colors[i % len(colors)]
    color = "#" + "".join("%02x" % round(255 * v) for v in c)
    if brightened:
        color = brighten(color)
    return color


def change_saturation(color, factor):
    rgb_hex = color.lstrip("#")
    r, g, b = [int(rgb_hex[i : i + 2], base=16) / 256 for i in (0, 2, 4)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    s = min(1.0, l * factor)
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return "#" + hex(int(r * 256))[2:] + hex(int(g * 256))[2:] + hex(int(b * 256))[2:]


def change_lightness(color, factor):
    rgb_hex = color.lstrip("#")
    r, g, b = [int(rgb_hex[i : i + 2], base=16) / 256 for i in (0, 2, 4)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = min(1.0, l * factor)
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return "#" + hex(int(r * 256))[2:] + hex(int(g * 256))[2:] + hex(int(b * 256))[2:]


def brighten(color):
    rgb = [int(color[i : i + 2], 16) for i in range(1, 6, 2)]
    rgb_light = [min(ii + 50, 255) for ii in rgb]
    return "#" + "".join("%02x" % v for v in rgb_light)


def config_for_eic(color):
    return dict(linewidth=3, color=color)


def config_for_ms_chromatogram(color):
    return dict(linewidth=3, linestyle="DashLine", color=color)


def config_for_background_eic(color):
    return dict(linewidth=2, color=color, linestyle="DotLine")


def config_for_spectrum(color):
    return dict(linewidth=2, color=color, curvestyle="Sticks")


def add_alpha(color, alpha):
    return "#" + hex(alpha)[2:] + color[1:]


def config_for_fitted_peakshape_model(color):
    return {
        "fill.alpha": 0.3,
        "fill.color": brighten(color),
        "line.width": 0,
        "line.style": "NoPen",
    }
