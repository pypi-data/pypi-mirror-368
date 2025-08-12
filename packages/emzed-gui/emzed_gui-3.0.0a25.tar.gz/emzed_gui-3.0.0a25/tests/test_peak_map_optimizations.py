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


import time

import numpy as np
import pytest
from emzed import PeakMap

from emzed_gui.optimized import sample_image, sample_peaks


@pytest.fixture
def pm(data_path):
    return PeakMap.load(data_path("test_smaller.mzXML"))


def test_sample_peaks(pm, regtest):
    s = time.time()
    peaks = sample_peaks(pm, 0, 2, 500, 510, 5, 1)
    print(time.time() - s)
    with np.printoptions(precision=4):
        print(peaks, file=regtest)


def test_sample_image(pm, regtest):
    rtmin, rtmax = pm.rt_range()
    mzmin, mzmax = pm.mz_range()

    s = time.time()
    image = sample_image(pm, rtmin, rtmax, mzmin, mzmax, width=4, height=3, ms_level=1)
    print(time.time() - s)
    with np.printoptions(precision=4):
        print(image, file=regtest)
