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

import multiprocessing
import ctypes
import numpy as np
from osgeo import gdal

from ...numeric.array import get_array_tilebounds

__author__ = "Daniel Scheffler"


shared_array = None


def init_SharedArray_in_globals(dims: (int, int)) -> None:
    rows, cols = dims
    global shared_array
    shared_array_base = multiprocessing.Array(ctypes.c_double, rows * cols)
    shared_array = np.ctypeslib.as_array(shared_array_base.get_obj())
    shared_array = shared_array.reshape(rows, cols)


def fill_arr(argDict, def_param=shared_array):
    pos = argDict.get('pos')
    func = argDict.get('func2call')
    args = argDict.get('func_args', [])
    kwargs = argDict.get('func_kwargs', {})

    (rS, rE), (cS, cE) = pos
    shared_array[rS:rE + 1, cS:cE + 1] = func(*args, **kwargs)


def gdal_read_subset(fPath, pos, bandNr):
    (rS, rE), (cS, cE) = pos
    with gdal.Open(fPath) as ds:
        data = ds.GetRasterBand(bandNr).ReadAsArray(cS, rS, cE - cS + 1, rE - rS + 1)
    return data


def gdal_ReadAsArray_mp(fPath, bandNr, tilesize=1500):
    with gdal.Open(fPath) as ds:
        rows, cols = ds.RasterYSize, ds.RasterXSize

    init_SharedArray_in_globals((rows, cols))

    tilepos = get_array_tilebounds(array_shape=(rows, cols), tile_shape=[tilesize, tilesize])
    fill_arr_argDicts = [{'pos': pos, 'func2call': gdal_read_subset, 'func_args': (fPath, pos, bandNr)} for pos in
                         tilepos]

    with multiprocessing.Pool() as pool:
        pool.map(fill_arr, fill_arr_argDicts)
        pool.close()
        pool.join()

    return shared_array
