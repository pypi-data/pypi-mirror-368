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

from shapely.geometry import Polygon, box
import numpy as np

from .conversion import shapelyImPoly_to_shapelyMapPoly, get_boxImXY_from_shapelyPoly, \
    shapelyBox2BoxYX, round_shapelyPoly_coords
from ..coord_calc import corner_coord_to_minmax
from ..coord_trafo import imYX2mapYX, transform_coordArray
from ..projection import prj_equal

__author__ = "Daniel Scheffler"


class boxObj(object):
    def __init__(self, **kwargs):
        """Create a dynamic/self-updating box object that represents a rectangular or quadratic coordinate box
        according to the given keyword arguments.

        Note: Either mapPoly+gt or imPoly+gt or wp+ws or boxMapYX+gt or boxImYX+gt must be passed.

        :Keyword Arguments:
            - gt (tuple):                   GDAL geotransform (default: (0, 1, 0, 0, 0, -1))
            - prj (str):                    projection as WKT string
            - mapPoly (shapely.Polygon):    Polygon with map unit vertices
            - imPoly (shapely.Polygon):     Polygon with image unit vertices
            - wp (tuple):                   window position in map units (x,y)
            - ws (tuple):                   window size in map units (x,y)
            - boxMapYX (list):              box map coordinates like [(ULy,ULx), (URy,URx), (LRy,LRx), (LLy,LLx)]
            - boxImYX (list):               box image coordinates like [(ULy,ULx), (URy,URx), (LRy,LRx), (LLy,LLx)]
        """
        # FIXME self.prj is not used
        # TODO allow boxObj to be instanced with gt, prj + rows/cols
        self.gt = kwargs.get('gt', (0, 1, 0, 0, 0, -1))
        self.prj = kwargs.get('prj', '')
        self._mapPoly = kwargs.get('mapPoly', None)
        self._imPoly = kwargs.get('imPoly', None)
        self.wp = kwargs.get('wp', None)
        self._ws = kwargs.get('ws', None)
        self._boxMapYX = kwargs.get('boxMapYX', None)
        self._boxImYX = kwargs.get('boxImYX', None)

        if self._mapPoly:
            if self.gt == (0, 1, 0, 0, 0, -1):
                raise ValueError(self.gt, "A geotransform must be passed if mapPoly is given.")
        else:
            # populate self._mapPoly
            if self._imPoly:
                self._mapPoly = shapelyImPoly_to_shapelyMapPoly(self._imPoly, self.gt)
            elif self._boxMapYX:
                self.boxMapYX = self._boxMapYX
            elif self._boxImYX:
                self.boxImYX = self._boxImYX
            elif self.wp or self._ws:  # asserts wp/ws in map units
                assert self.wp and self._ws, \
                    "'wp' and 'ws' must be passed together. Got wp=%s and ws=%s." % (self.wp, self._ws)
                (wpx, wpy), (wsx, wsy) = self.wp, self._ws
                self._mapPoly = box(wpx - wsx / 2, wpy - wsy / 2, wpx + wsx / 2, wpy + wsy / 2)
            else:
                raise ValueError("No proper set of arguments received.")

    # all getters and setters synchronize using self._mapPoly
    @property
    def mapPoly(self):
        imPoly = Polygon(get_boxImXY_from_shapelyPoly(self._mapPoly, self.gt))
        return shapelyImPoly_to_shapelyMapPoly(imPoly, self.gt)

    @mapPoly.setter
    def mapPoly(self, shapelyPoly):
        self._mapPoly = shapelyPoly

    @property
    def imPoly(self):
        return Polygon(get_boxImXY_from_shapelyPoly(self.mapPoly, self.gt))

    @imPoly.setter
    def imPoly(self, shapelyImPoly):
        self.mapPoly = shapelyImPoly_to_shapelyMapPoly(shapelyImPoly, self.gt)

    @property
    def boxMapYX(self):
        """Return a list of YX coordinate tuples for all corners in the order UL_YX, UR_YX, LR_YX, LL_YX.

        :return:    UL_YX, UR_YX, LR_YX, LL_YX
        """
        return shapelyBox2BoxYX(self.mapPoly, coord_type='map')

    @boxMapYX.setter
    def boxMapYX(self, mapBoxYX):
        mapBoxXY = [(i[1], i[0]) for i in mapBoxYX]
        xmin, xmax, ymin, ymax = corner_coord_to_minmax(mapBoxXY)
        self.mapPoly = box(xmin, ymin, xmax, ymax)

    @property
    def boxMapXY(self):
        """Return a list of XY coordinate tuples for all corners in the order UL_XY, UR_XY, LR_XY, LL_XY.

        :return:    UL_XY, UR_XY, LR_XY, LL_XY
        """
        return tuple((x, y) for y, x in self.boxMapYX)

    @boxMapXY.setter
    def boxMapXY(self, mapBoxXY):
        xmin, xmax, ymin, ymax = corner_coord_to_minmax(mapBoxXY)
        self.mapPoly = box(xmin, ymin, xmax, ymax)

    @property
    def boxImYX(self):
        temp_imPoly = round_shapelyPoly_coords(self.imPoly, precision=0)
        floatImBoxYX = shapelyBox2BoxYX(temp_imPoly, coord_type='image')
        return [[int(i[0]), int(i[1])] for i in floatImBoxYX]

    @boxImYX.setter
    def boxImYX(self, imBoxYX):
        imBoxXY = [(i[1], i[0]) for i in imBoxYX]
        xmin, xmax, ymin, ymax = corner_coord_to_minmax(imBoxXY)
        self.imPoly = box(xmin, ymin, xmax, ymax)

    @property
    def boxImXY(self):
        return tuple((x, y) for y, x in self.boxImYX)

    @boxImXY.setter
    def boxImXY(self, imBoxXY):
        xmin, xmax, ymin, ymax = corner_coord_to_minmax(imBoxXY)
        self.imPoly = box(xmin, ymin, xmax, ymax)

    @property
    def boundsMap(self):
        """Return xmin,xmax,ymin,ymax in map coordinates."""
        boxMapYX = shapelyBox2BoxYX(self.mapPoly, coord_type='image')
        boxMapXY = [(i[1], i[0]) for i in boxMapYX]
        return corner_coord_to_minmax(boxMapXY)

    @property
    def boundsIm(self):
        """Return xmin,xmax,ymin,ymax in image coordinates."""
        boxImXY = [(round(x, 0), round(y, 0)) for x, y in get_boxImXY_from_shapelyPoly(self.mapPoly, self.gt)]
        return corner_coord_to_minmax(boxImXY)  # xmin,xmax,ymin,ymax

    @property
    def imDimsYX(self):
        xmin, xmax, ymin, ymax = self.boundsIm
        return (ymax - ymin), (xmax - xmin)

    @property
    def imDimsXY(self):
        return self.imDimsYX[1], self.imDimsYX[0]

    @property
    def mapDimsYX(self):
        xmin, xmax, ymin, ymax = self.boundsMap
        return (ymax - ymin), (xmax - xmin)

    @property
    def mapDimsXY(self):
        return self.mapDimsYX[1], self.mapDimsYX[0]

    def buffer_imXY(self, buffImX: float = 0, buffImY: float = 0) -> None:
        """Buffer the box in X- and/or Y-direction.

        :param buffImX:     buffer value in x-direction as IMAGE UNITS (pixels)
        :param buffImY:     buffer value in y-direction as IMAGE UNITS (pixels)
        """
        xmin, xmax, ymin, ymax = self.boundsIm
        xmin, xmax, ymin, ymax = xmin - buffImX, xmax + buffImX, ymin - buffImY, ymax + buffImY
        self.imPoly = box(xmin, ymin, xmax, ymax)

    def buffer_mapXY(self, buffMapX: float = 0, buffMapY: float = 0) -> None:
        """Buffer the box in X- and/or Y-direction.

        :param buffMapX:     buffer value in x-direction as MAP UNITS
        :param buffMapY:     buffer value in y-direction as MAP UNITS
        """
        xmin, xmax, ymin, ymax = self.boundsMap
        xmin, xmax, ymin, ymax = xmin - buffMapX, xmax + buffMapX, ymin - buffMapY, ymax + buffMapY
        self.mapPoly = box(xmin, ymin, xmax, ymax)

    def is_larger_DimXY(self,
                        boundsIm2test: (float, float, float, float)
                        ) -> (bool, bool):
        """Check if the boxObj is larger than a given set of bounding image coordinates (in X- and/or Y-direction).

        :param boundsIm2test:   (xmin,xmax,ymin,ymax) as image coordinates
        """
        b2t_xmin, b2t_xmax, b2t_ymin, b2t_ymax = boundsIm2test
        xmin, xmax, ymin, ymax = self.boundsIm
        x_is_larger = xmin < b2t_xmin or xmax > b2t_xmax
        y_is_larger = ymin < b2t_ymin or ymax > b2t_ymax
        return x_is_larger, y_is_larger

    def get_coordArray_MapXY(self, prj: str = None) -> (np.ndarray, np.ndarray):
        """Return two coordinate arrays for X and Y coordinates in the given projection.

         NOTE: If no projection is given, <boxObj>.prj is used.

        :param prj:     GDAL projection as WKT string
        :return:
        """
        if not (self.gt and self.prj):
            raise ValueError('geotransform and projection must both be available for computing coordinate array.'
                             'boxObj.gt=%s; boxobj.prj=%s' % (self.gt, self.prj))

        xmin, xmax, ymin, ymax = self.boundsMap
        Xarr, Yarr = np.meshgrid(np.arange(xmin, xmax, abs(self.gt[1])),
                                 np.arange(ymax, ymin, -abs(self.gt[5])))
        if prj and not prj_equal(self.prj, prj):
            Xarr, Yarr = transform_coordArray(self.prj, prj, Xarr, Yarr)

        return Xarr, Yarr


def get_winPoly(wp_imYX: tuple,
                ws: tuple,
                gt: (float, float, float, float, float, float),
                match_grid: bool = False):
    """Create a shapely polygon from a given set of image cordinates, window size and geotransform.

    :param wp_imYX:
    :param ws:          X/Y window size
    :param gt:
    :param match_grid:
    """
    ws = (ws, ws) if isinstance(ws, int) else ws
    xmin, xmax, ymin, ymax = (
        wp_imYX[1] - ws[0] / 2, wp_imYX[1] + ws[0] / 2, wp_imYX[0] + ws[1] / 2, wp_imYX[0] - ws[1] / 2)
    if match_grid:
        xmin, xmax, ymin, ymax = [int(i) for i in [xmin, xmax, ymin, ymax]]
    box_YX = (ymax, xmin), (ymax, xmax), (ymin, xmax), (ymin, xmin)  # UL,UR,LR,LL
    UL, UR, LR, LL = [imYX2mapYX(imYX, gt) for imYX in box_YX]
    box_mapYX = UL, UR, LR, LL
    return Polygon([(UL[1], UL[0]), (UR[1], UR[0]), (LR[1], LR[0]), (LL[1], LR[0])]), box_mapYX, box_YX
