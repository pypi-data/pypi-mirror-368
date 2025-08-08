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

import datetime

import numpy as np
from osgeo import gdal

# dictionary to translate Numpy data types (strings) into corresponding GDAL data types,
#  e.g. dTypeDic_NumPy2GDAL(str(np.dtype(np.uint8)))
dTypeDic_NumPy2GDAL = {'bool': gdal.GDT_Byte,
                       'bool_': gdal.GDT_Int32,
                       'int': gdal.GDT_Int32,
                       'int8': gdal.GDT_Int16,
                       'uint8': gdal.GDT_Byte,
                       'uint16': gdal.GDT_UInt16,
                       'int16': gdal.GDT_Int16,
                       'uint32': gdal.GDT_UInt32,
                       'int32': gdal.GDT_Int32,
                       'int64': gdal.GDT_Float64,
                       'float': gdal.GDT_Float32,
                       'float16': gdal.GDT_Float32,
                       'float32': gdal.GDT_Float32,
                       'float64': gdal.GDT_Float64
                       }

# dictionary to translate GDAL data types (strings) into corresponding numpy data types
dTypeDic_GDAL2Numpy = {gdal.GDT_Byte: np.uint8,
                       gdal.GDT_UInt16: np.uint16,
                       gdal.GDT_Int16: np.int16,
                       gdal.GDT_UInt32: np.uint32,
                       gdal.GDT_Int32: np.int32,
                       gdal.GDT_Float32: np.float32,
                       gdal.GDT_Float64: np.float64,
                       }

# dictionary to translate Numpy data types into GDAL compatible Numpy data types
dTypeDic_NumPy2GDALcompatible = \
    dict(zip(dTypeDic_NumPy2GDAL.keys(),
             [dTypeDic_GDAL2Numpy[dTypeDic_NumPy2GDAL[str(np.dtype(NDT))]] for NDT in dTypeDic_NumPy2GDAL.keys()]))


def get_dtypeStr(val):
    is_numpy = 'numpy' in str(type(val))
    DType = str(np.dtype(val)) if is_numpy else \
        'int' if isinstance(val, int) else \
        'float' if isinstance(val, float) else \
        'str' if isinstance(val, str) else \
        'complex' if isinstance(val, complex) else \
        'date' if isinstance(val, datetime.datetime) else None
    assert DType, 'data type not understood'
    return DType


def convertGdalNumpyDataType(dType):
    """convertGdalNumpyDataType
    :param dType: GDALdataType string or numpy dataType
    :return: corresponding dataType
    """
    # dictionary to translate GDAL data types (strings) in corresponding numpy data types
    dTypeDic = {"Byte": np.uint8, "UInt16": np.uint16, "Int16": np.int16, "UInt32": np.uint32, "Int32": np.int32,
                "Float32": np.float32, "Float64": np.float64, "GDT_UInt32": np.uint32}
    outdType = None

    if dType in dTypeDic:
        outdType = dTypeDic[dType]
    elif dType in dTypeDic.values():
        for i in dTypeDic.items():
            if dType == i[1]:
                outdType = i[0]
    elif dType in [np.int8, np.int64, int]:
        outdType = "Int32"
        print(">>>  Warning: %s is converted to GDAL_Type 'Int_32'\n" % dType)
    elif dType in [bool, np.bool_]:
        outdType = "Byte"
        print(">>>  Warning: %s is converted to GDAL_Type 'Byte'\n" % dType)
    elif dType in [float]:
        outdType = "Float32"
        print(">>>  Warning: %s is converted to GDAL_Type 'Float32'\n" % dType)
    elif dType in [np.float16]:
        outdType = "Float32"
        print(">>>  Warning: %s is converted to GDAL_Type 'Float32'\n" % dType)
    else:
        raise Exception('GEOP.convertGdalNumpyDataType: Unexpected input data type %s.' % dType)
    return outdType
