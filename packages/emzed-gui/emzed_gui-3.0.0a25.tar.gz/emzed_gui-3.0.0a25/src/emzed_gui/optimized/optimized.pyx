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

cimport cython
cimport numpy as np

import sys

import numpy as np

from cpython cimport Py_buffer
from cpython.buffer cimport PyBuffer_Release, PyObject_GetBuffer
from libc.stdlib cimport calloc, free, malloc


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def _sample_peaks(cursor, double mzmin, double mzmax, size_t n_bins):

    cdef np.float64_t[:, :] peaks
    cdef np.float64_t[:] mzs
    cdef np.float32_t[:] iis

    cdef double* mzp
    cdef float* iip
    cdef size_t i, j
    cdef Py_buffer mz_buffer
    cdef Py_buffer ii_buffer

    cdef double mz, ii

    cdef int mz_bin

    cdef double * i_sums = <double * > calloc(sizeof(double), n_bins)
    if i_sums == NULL:
        return None
    cdef double * mz_i_sums = <double * > calloc(sizeof(double), n_bins)
    if mz_i_sums == NULL:
        free(i_sums)
        return None
    cdef double * i_max = <double * > calloc(sizeof(double), n_bins)
    if i_max == NULL:
        free(i_sums)
        free(mz_i_sums)
        return None

    for spec in cursor:

        assert PyObject_GetBuffer(spec[0], &mz_buffer, 0) == 0, "get buffer failed"
        assert PyObject_GetBuffer(spec[1], &ii_buffer, 0) == 0, "get buffer failed"

        mzp = <double *> mz_buffer.buf
        iip = <float *> ii_buffer.buf

        for i in range(mz_buffer.len // sizeof(double)):
            mz = mzp[i]
            if mz < mzmin:
                continue
            if mz > mzmax:
                break
            ii = iip[i]

            mz_bin = int((mz - mzmin) / (mzmax - mzmin) * (n_bins - 1))

            i_sums[mz_bin] += ii
            mz_i_sums[mz_bin] += mz * ii
            i_max[mz_bin] = max(i_max[mz_bin], ii)

        PyBuffer_Release(&mz_buffer)
        PyBuffer_Release(&ii_buffer)

    result = np.zeros((n_bins, 2), dtype=np.float64)
    peaks = result  # create view

    j = 0

    for i in range(n_bins):
        ii = i_sums[i]
        if ii > 0:
            peaks[j, 0] = mz_i_sums[i] / ii
            peaks[j, 1] = i_max[i]
            j += 1

    free(i_max)
    free(mz_i_sums)
    free(i_sums)
    return result[:j, :]



@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def _sample_image(cursor, double rtmin, double rtmax, double mzmin, double mzmax,
                  int ms_level, size_t width, size_t height,
                  np.float32_t[:, :] img_view):

    # avoid zero division later
    assert mzmax > mzmin
    assert rtmax > rtmin

    cdef size_t rt_bin, mz_bin, i
    cdef double rt, mz, ii

    cdef Py_buffer mz_buffer, ii_buffer

    for spec in cursor:

        rt = spec[0]
        rt_bin = int((rt - rtmin) / (rtmax - rtmin) * (width - 1))

        assert PyObject_GetBuffer(spec[1], &mz_buffer, 0) == 0, "get buffer failed"
        assert PyObject_GetBuffer(spec[2], &ii_buffer, 0) == 0, "get buffer failed"

        mzp = <double *> mz_buffer.buf
        iip = <float *> ii_buffer.buf


        for i in range(mz_buffer.len // sizeof(double)):
            mz = mzp[i]
            if mz < mzmin:
                continue
            if mz > mzmax:
                break

            ii = iip[i]

            mz_bin = int((mz - mzmin) / (mzmax - mzmin) * (height - 1))

            img_view[mz_bin, rt_bin] += ii

        PyBuffer_Release(&mz_buffer)
        PyBuffer_Release(&ii_buffer)
