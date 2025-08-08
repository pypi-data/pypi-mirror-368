# -*- coding: utf-8 -*-

# py_tools_ds - A collection of geospatial data analysis tools that simplify standard
# operations when handling geospatial raster and vector data as well as projections.
#
# Copyright (C) 2016-2024
# - Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz.de)
# - GFZ Helmholtz Centre for Geosciences, Potsdam, Germany (https://www.gfz.de/)
#
# This software was developed within the context of the GeoMultiSens project funded
# by the German Federal Ministry of Education and Research
# (project grant code: 01 IS 14 010 A-C).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import collections
import numpy as np
import bisect
from typing import Union

__author__ = "Daniel Scheffler"


def find_nearest(array: Union[list, np.ndarray],
                 value: float,
                 roundAlg: str = 'auto',
                 extrapolate: bool = False,
                 exclude_val: bool = False,
                 tolerance: float = 0
                 ) -> float:
    """Find the value of an array nearest to another single value.

    NOTE: In case of extrapolation an EQUALLY INCREMENTED array (like a coordinate grid) is assumed!

    :param array:       array or list of numbers
    :param value:       a number
    :param roundAlg:    rounding algorithm: 'auto', 'on', 'off'
    :param extrapolate: extrapolate the given array if the given value is outside the array
    :param exclude_val: exclude the given value from possible return values
    :param tolerance:   tolerance (with array = [10, 20, 30] and value=19.9 and roundAlg='off' and tolerance=0.1, 20
                                   is returned)
    """
    if roundAlg not in ['auto', 'on', 'off']:
        raise ValueError(roundAlg)
    if not isinstance(array, (list, np.ndarray)):
        raise TypeError(array)

    def is_sorted(a):
        if a[0] < a[-1]:
            return np.all(a[:-1] <= a[1:])
        else:
            return np.all(a[:-1] >= a[1:])

    if isinstance(array, list):
        array = np.array(array)
    if array.ndim > 1:
        array = array.flatten()
    if is_sorted(array):
        # flip decending array
        if array[0] > array[1]:
            array = array[::-1]
    else:
        array = np.sort(array)

    minimum, maximum = array[0], array[-1]  # faster than np.min/np.max

    if exclude_val and value in array:
        array = array[array != value]

    if extrapolate:
        increment = abs(array[1] - array[0])
        if value > maximum:  # expand array until value
            array = np.arange(minimum, value + 2 * increment, increment)  # 2 * inc to make array_sub work below
        if value < minimum:  # negatively expand array until value
            array = (np.arange(maximum, value - 2 * increment, -increment))[::-1]
    elif value < minimum or value > maximum:
        raise ValueError('Value %s is outside of the given array.' % value)

    if roundAlg == 'auto':
        diffs = np.abs(np.array(array) - value)
        minDiff = diffs.min()
        minIdx = diffs.argmin()
        isMiddleVal = collections.Counter(diffs)[minDiff] > 1  # value exactly between its both neighbours
        idx = minIdx if not isMiddleVal else bisect.bisect_left(array, value)
        out = array[idx]
    elif roundAlg == 'off':
        idx = bisect.bisect_left(array, value)
        if array[idx] == value:
            out = value  # exact hit
        else:
            idx -= 1
            out = array[idx]  # round off
    else:  # roundAlg == 'on'
        idx = bisect.bisect_left(array, value)
        out = array[idx]

    if tolerance:
        array_sub = array[idx - 1: idx + 2]
        diffs = np.abs(np.array(array_sub) - value)
        inTol = diffs <= tolerance

        if True in inTol:
            out = array_sub[np.argwhere(inTol.astype(int) == 1)[0][0]]

    return out
