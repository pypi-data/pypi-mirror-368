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

import time
import os

import numpy as np
from pandas import DataFrame
from osgeo import gdal, gdal_array

from ...dtypes.conversion import dTypeDic_NumPy2GDALcompatible


def get_GDAL_ds_inmem(array: np.ndarray,
                      gt: (float, float, float, float, float, float) = None,
                      prj: str = None,
                      nodata: int = None
                      ) -> gdal.Dataset:
    """Convert a numpy array into a GDAL dataset.

    NOTE: Possibly the data type has to be automatically changed in order ensure GDAL compatibility!

    :param array:   in the shape (rows, columns, bands)
    :param gt:
    :param prj:
    :param nodata:  nodata value to be set (GDAL seems to have issues with non-int nodata values.)
    :return:
    """
    # FIXME does not respect different nodata values for each band

    if len(array.shape) == 3:
        array = np.rollaxis(array, 2)  # rows,cols,bands => bands,rows,cols

    # convert data type to GDAL compatible data type
    if gdal_array.NumericTypeCodeToGDALTypeCode(array.dtype) is None:
        array = array.astype(dTypeDic_NumPy2GDALcompatible[str(np.dtype(array.dtype))])

    ds = gdal_array.OpenArray(array)  # uses interleave='band' by default
    if ds is None:
        raise Exception(gdal.GetLastErrorMsg())
    if gt:
        ds.SetGeoTransform(gt)
    if prj:
        ds.SetProjection(prj)

    if nodata is not None:
        for i in range(ds.RasterCount):
            band = ds.GetRasterBand(i + 1)
            try:
                # band.SetNoDataValue does not support numpy data types
                if isinstance(nodata, np.bool_):
                    nodata = bool(nodata)
                elif isinstance(nodata, np.integer):
                    nodata = int(nodata)
                elif isinstance(nodata, np.floating):
                    nodata = float(nodata)
                elif isinstance(nodata, np.ndarray):
                    raise TypeError(nodata, 'A np.ndarray instance is not supported to be set as no-data value.')

                band.SetNoDataValue(nodata)
            except TypeError:
                raise TypeError(type(nodata), 'TypeError while trying to set NoDataValue to %s. ' % nodata)
            del band

    ds.FlushCache()  # Write to disk.
    return ds


def get_GDAL_driverList() -> DataFrame:
    count = gdal.GetDriverCount()
    df = DataFrame(np.full((count, 5), np.nan),
                   columns=['drvCode', 'drvLongName', 'ext1', 'ext2', 'ext3']).astype(object)
    for i in range(count):
        drv = gdal.GetDriver(i)
        if drv.GetMetadataItem(gdal.DCAP_RASTER):
            meta = drv.GetMetadataItem(gdal.DMD_EXTENSIONS)
            extensions = meta.split() if meta else []
            df.loc[i] = [drv.GetDescription(),
                         drv.GetMetadataItem(gdal.DMD_LONGNAME),
                         extensions[0] if len(extensions) > 0 else np.nan,
                         extensions[1] if len(extensions) > 1 else np.nan,
                         extensions[2] if len(extensions) > 2 else np.nan]
    df = df.dropna(how='all')
    return df


def wait_if_used(path_file: str, lockfile: str, timeout: int = 100, try_kill: bool = False):
    globs = globals()
    same_gdalRefs = [k for k, v in globs.items() if
                     isinstance(globs[k], gdal.Dataset) and globs[k].GetDescription() == path_file]
    t0 = time.time()

    def update_same_gdalRefs(sRs):
        return [sR for sR in sRs if sR in globals() and globals()[sR] is not None]

    while same_gdalRefs != [] or os.path.exists(lockfile):
        if os.path.exists(lockfile):
            continue

        if time.time() - t0 > timeout:
            if try_kill:
                for sR in same_gdalRefs:
                    globals()[sR] = None
                    print('had to kill %s' % sR)
            else:
                if os.path.exists(lockfile):
                    os.remove(lockfile)

                raise TimeoutError('The file %s is permanently used by another variable.' % path_file)

        same_gdalRefs = update_same_gdalRefs(same_gdalRefs)
