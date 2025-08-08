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

__author__ = "Daniel Scheffler"

import numpy as np
from typing import List, Iterable


def get_outFillZeroSaturated(dtype) -> tuple:
    """Return proper 'fill-', 'zero-' and 'saturated' values with respect to the given data type.

    :param dtype: data type
    """
    dtype = str(np.dtype(dtype))
    assert dtype in ['int8', 'uint8', 'int16', 'uint16', 'float32'], \
        "get_outFillZeroSaturated: Unknown dType: '%s'." % dtype
    dict_outFill = {'int8': -128, 'uint8': 0, 'int16': -9999, 'uint16': 9999, 'float32': -9999.}
    dict_outZero = {'int8': 0, 'uint8': 1, 'int16': 0, 'uint16': 1, 'float32': 0.}
    dict_outSaturated = {'int8': 127, 'uint8': 255, 'int16': 32767, 'uint16': 65535, 'float32': 65535.}

    return dict_outFill[dtype], dict_outZero[dtype], dict_outSaturated[dtype]


def get_array_tilebounds(array_shape: Iterable, tile_shape: Iterable) -> List[List[tuple]]:
    """Calculate row/col bounds for image tiles according to the given parameters.

    :param array_shape:    dimensions of array to be tiled: (rows, columns, bands) or (rows, columns)
    :param tile_shape:     dimensions of target tile: (rows, columns, bands) or (rows, columns)
    """
    rows, cols = array_shape[:2]
    tgt_rows, tgt_cols = tile_shape[:2]
    tgt_rows, tgt_cols = tgt_rows or rows, tgt_cols or cols  # return all rows/cols in case tile_shape contains None

    row_bounds = [0]
    while row_bounds[-1] + tgt_rows < rows:
        row_bounds.append(row_bounds[-1] + tgt_rows - 1)
        row_bounds.append(row_bounds[-2] + tgt_rows)
    else:
        row_bounds.append(rows - 1)

    col_bounds = [0]
    while col_bounds[-1] + tgt_cols < cols:
        col_bounds.append(col_bounds[-1] + tgt_cols - 1)
        col_bounds.append(col_bounds[-2] + tgt_cols)
    else:
        col_bounds.append(cols - 1)

    return [[tuple([row_bounds[r], row_bounds[r + 1]]), tuple([col_bounds[c], col_bounds[c + 1]])]
            for r in range(0, len(row_bounds), 2) for c in range(0, len(col_bounds), 2)]
