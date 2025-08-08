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

import numpy as np
from typing import Union
from packaging.version import Version

# custom
from shapely.geometry import shape, mapping, box
from shapely.geometry import Point, Polygon
from shapely import wkt
from osgeo import gdal, ogr, osr

from ..coord_trafo import imYX2mapYX, mapYX2imYX, pixelToMapYX
from ...dtypes.conversion import get_dtypeStr, dTypeDic_NumPy2GDAL

__author__ = "Daniel Scheffler"


def shapelyImPoly_to_shapelyMapPoly_withPRJ(shapelyImPoly, gt, prj):
    # ACTUALLY PRJ IS NOT NEEDED BUT THIS FUNCTION RETURNS OTHER VALUES THAN shapelyImPoly_to_shapelyMapPoly
    geojson = mapping(shapelyImPoly)
    coords = list(geojson['coordinates'][0])
    coordsYX = pixelToMapYX(coords, geotransform=gt, projection=prj)
    coordsXY = tuple([(i[1], i[0]) for i in coordsYX])
    geojson['coordinates'] = (coordsXY,)
    return shape(geojson)


def shapelyImPoly_to_shapelyMapPoly(shapelyBox, gt):
    xmin, ymin, xmax, ymax = shapelyBox.bounds
    ymax, xmin = imYX2mapYX((ymax, xmin), gt)
    ymin, xmax = imYX2mapYX((ymin, xmax), gt)
    return box(xmin, ymin, xmax, ymax)


def shapelyBox2BoxYX(shapelyBox, coord_type='image'):
    xmin, ymin, xmax, ymax = shapelyBox.bounds
    assert coord_type in ['image', 'map']

    if coord_type == 'image':
        UL_YX = ymin, xmin
        UR_YX = ymin, xmax
        LR_YX = ymax, xmax
        LL_YX = ymax, xmin
    else:
        UL_YX = ymax, xmin
        UR_YX = ymax, xmax
        LR_YX = ymin, xmax
        LL_YX = ymin, xmin

    return UL_YX, UR_YX, LR_YX, LL_YX


def get_boxImXY_from_shapelyPoly(shapelyPoly: Polygon,
                                 im_gt: (float, float, float, float, float, float)
                                 ) -> list:
    """Convert each vertex coordinate of a shapely polygon into image coordinates corresponding to the given
    geotransform without respect to invalid image coordinates. Those must be filtered later.

    :param shapelyPoly:     shapely polygon
    :param im_gt:           the GDAL geotransform of the target image
    """
    def get_coordsArr(shpPoly): return np.swapaxes(np.array(shpPoly.exterior.coords.xy), 0, 1)
    coordsArr = get_coordsArr(shapelyPoly)
    boxImXY = [mapYX2imYX((Y, X), im_gt) for X, Y in coordsArr.tolist()]  # FIXME incompatible to GMS version
    boxImXY = [(i[1], i[0]) for i in boxImXY]
    return boxImXY


def round_shapelyPoly_coords(shapelyPoly: Polygon, precision: int = 10):
    """Round the coordinates of the given shapely polygon.

    :param shapelyPoly:     the shapely polygon
    :param precision:       number of decimals
    :return:
    """
    return wkt.loads(wkt.dumps(shapelyPoly, rounding_precision=precision))


def points_to_raster(points: Union[list[Point], np.ndarray[Point]],
                     values: Union[list, np.ndarray],
                     tgt_res: float,
                     prj: str = None,
                     fillVal: float = None
                     ) -> (np.ndarray, list, str):
    """
    Convert a set of point geometries with associated values into a raster array.

    :param points: list or 1D numpy.ndarray containing shapely.geometry.Point geometries
    :param values: list or 1D numpy.ndarray containing int or float values
    :param tgt_res: target resolution in projection units
    :param prj: WKT projection string
    :param fillVal: fill value used to fill in where no point geometry is available
    """
    drv = 'MEM' if Version(gdal.__version__) >= Version('3.11.0') else 'Memory'

    with ogr.GetDriverByName(drv).CreateDataSource('wrk') as ds:
        if prj is not None:
            srs = osr.SpatialReference()
            srs.ImportFromWkt(prj)
        else:
            srs = None

        layer = ds.CreateLayer('', srs, ogr.wkbPoint)

        # create field
        DTypeStr = get_dtypeStr(values if isinstance(values, np.ndarray) else values[0])
        FieldType = ogr.OFTInteger if DTypeStr.startswith('int') else ogr.OFTReal
        FieldDefn = ogr.FieldDefn('VAL', FieldType)
        if DTypeStr.startswith('float'):
            FieldDefn.SetPrecision(6)
        layer.CreateField(FieldDefn)  # Add one attribute

        for i in range(len(points)):
            # Create a new feature (attribute and geometry)
            feat = ogr.Feature(layer.GetLayerDefn())
            feat.SetGeometry(ogr.CreateGeometryFromWkb(points[i].wkb))  # Make a geometry, from Shapely object
            feat.SetField('VAL', values[i])

            layer.CreateFeature(feat)
            feat.Destroy()

        x_min, x_max, y_min, y_max = layer.GetExtent()

        # Create the destination data source
        cols = int((x_max - x_min) / tgt_res)
        rows = int((y_max - y_min) / tgt_res)
        with gdal.GetDriverByName('MEM').Create('raster', cols, rows, 1, dTypeDic_NumPy2GDAL[DTypeStr]) as target_ds:
            target_ds.SetGeoTransform((x_min, tgt_res, 0, y_max, 0, -tgt_res))
            target_ds.SetProjection(prj if prj else '')
            band = target_ds.GetRasterBand(1)
            if fillVal is not None:
                band.Fill(fillVal)
            band.FlushCache()

            # Rasterize
            gdal.RasterizeLayer(target_ds, [1], layer, options=["ATTRIBUTE=VAL"])

            out_arr = target_ds.GetRasterBand(1).ReadAsArray()
            out_gt = target_ds.GetGeoTransform()
            out_prj = target_ds.GetProjection()

            del layer, band

    return out_arr, out_gt, out_prj
