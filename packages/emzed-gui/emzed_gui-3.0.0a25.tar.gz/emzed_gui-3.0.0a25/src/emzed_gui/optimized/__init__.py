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


import numpy as np

from .optimized import _sample_image, _sample_peaks


def sample_peaks(pm, rtmin, rtmax, mzmin, mzmax, bins, ms_level):
    if mzmin >= mzmax or rtmin > rtmax:
        return np.zeros((0, 2), dtype=np.float64)
    cursor = pm._conn.execute(
        f"""SELECT mzs, intensities
        FROM   {pm._access_name}_spectra
        WHERE  ms_level = ?
        AND    rt >= ?
        AND    rt <= ?""",
        (ms_level, rtmin, rtmax),
    )

    return _sample_peaks(cursor, mzmin, mzmax, bins)


def sample_image(pm, rtmin, rtmax, mzmin, mzmax, width, height, ms_level):
    image = np.zeros((height, width), dtype=np.float32)
    if mzmin >= mzmax or rtmin >= rtmax:
        return image

    cursor = pm._conn.execute(
        f"""SELECT rt, mzs, intensities
        FROM   {pm._access_name}_spectra
        WHERE  ms_level = ?
        AND    rt >= ?
        AND    rt <= ?""",
        (ms_level, rtmin, rtmax),
    )

    _sample_image(cursor, rtmin, rtmax, mzmin, mzmax, ms_level, width, height, image)
    return image
