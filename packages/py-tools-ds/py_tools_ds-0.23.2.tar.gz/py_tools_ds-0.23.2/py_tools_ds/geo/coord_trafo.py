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

from typing import Union, Sequence, List
from warnings import catch_warnings, filterwarnings

import pyproj
import numpy as np
from shapely.ops import transform
from shapely.geometry.base import BaseGeometry
from osgeo import gdal, osr

__author__ = "Daniel Scheffler"


def transform_utm_to_wgs84(easting: float,
                           northing: float,
                           zone: int,
                           south: bool = False
                           ) -> (float, float):
    """Transform an UTM coordinate to lon, lat, altitude."""
    UTM = pyproj.Proj(proj='utm',
                      zone=abs(zone),
                      ellps='WGS84',
                      south=(zone < 0 or south))
    return UTM(easting, northing, inverse=True)


def get_utm_zone(longitude: float) -> int:
    """Get the UTM zone corresponding to the given longitude."""
    return int(1 + (longitude + 180.0) / 6.0)


def transform_wgs84_to_utm(lon: float,
                           lat: float,
                           zone: int = None
                           ) -> (float, float):
    """Return easting, northing, altitude for the given Lon/Lat coordinate.

    :param lon:     longitude
    :param lat:     latitude
    :param zone:    UTM zone (if not set it is derived automatically)
    """
    if not (-180. <= lon <= 180. and -90. <= lat <= 90.):
        raise ValueError((lon, lat), 'Input coordinates for transform_wgs84_to_utm() out of range.')

    UTM = pyproj.Proj(proj='utm',
                      zone=get_utm_zone(lon) if zone is None else zone,
                      ellps='WGS84')
    return UTM(lon, lat)


def transform_any_prj(prj_src: Union[str, int],
                      prj_tgt: Union[str, int],
                      x: Union[float, np.ndarray],
                      y: Union[float, np.ndarray]
                      ) -> (Union[float, np.ndarray], Union[float, np.ndarray]):
    """Transform X/Y data from any source projection to any target projection.

    :param prj_src:     GDAL projection as WKT string or EPSG code ('epsg:1234' or <EPSG_int>)
    :param prj_tgt:     GDAL projection as WKT string or EPSG code ('epsg:1234' or <EPSG_int>)
    :param x:           X-coordinate(s) to be transformed (either <float> or 1D-<np.ndarray>)
    :param y:           X-coordinate(s) to be transformed (either <float> or 1D-<np.ndarray>)
    :return:
    """
    transformer = pyproj.Transformer.from_crs(pyproj.CRS.from_user_input(prj_src),
                                              pyproj.CRS.from_user_input(prj_tgt),
                                              always_xy=True)
    with catch_warnings():
        # DeprecationWarning in pyproj 3.6.1 (future pyproj releases will fix this)
        filterwarnings(
            "ignore", category=DeprecationWarning, message=".*Conversion of an array with ndim > 0 to a scalar.*")

        return transformer.transform(x, y)


def transform_coordArray(prj_src: str,
                         prj_tgt: str,
                         Xarr: np.ndarray,
                         Yarr: np.ndarray,
                         Zarr: np.ndarray = None
                         ) -> Sequence[np.ndarray]:
    """Transform a geolocation array from one projection into another.

    HINT: This function is faster than transform_any_prj but works only for geolocation arrays.

    :param prj_src:     WKT string
    :param prj_tgt:     WKT string
    :param Xarr:        np.ndarray of shape (rows,cols)
    :param Yarr:        np.ndarray of shape (rows,cols)
    :param Zarr:        np.ndarray of shape (rows,cols)
    :return:
    """
    drv = gdal.GetDriverByName('MEM')

    with drv.Create('geoloc', Xarr.shape[1], Xarr.shape[0], 3, gdal.GDT_Float64) as geoloc_ds:
        geoloc_ds.GetRasterBand(1).WriteArray(Xarr)
        geoloc_ds.GetRasterBand(2).WriteArray(Yarr)
        if Zarr is not None:
            geoloc_ds.GetRasterBand(3).WriteArray(Zarr)

        def strip_wkt(wkt):
            return wkt\
                .replace('\n', '')\
                .replace('\r', '')\
                .replace(' ', '')

        transformer = gdal.Transformer(None, None, ['SRC_SRS=' + strip_wkt(prj_src),
                                                    'DST_SRS=' + strip_wkt(prj_tgt)])
        status = transformer.TransformGeolocations(geoloc_ds.GetRasterBand(1),
                                                   geoloc_ds.GetRasterBand(2),
                                                   geoloc_ds.GetRasterBand(3))

        if status:
            raise Exception('Error transforming coordinate array:  ' + gdal.GetLastErrorMsg())

        Xarr = geoloc_ds.GetRasterBand(1).ReadAsArray()
        Yarr = geoloc_ds.GetRasterBand(2).ReadAsArray()

        if Zarr is not None:
            Zarr = geoloc_ds.GetRasterBand(3).ReadAsArray()
            return Xarr, Yarr, Zarr
        else:
            return Xarr, Yarr


def mapXY2imXY(mapXY: Union[tuple, np.ndarray],
               gt: (float, float, float, float, float, float),
               ) -> Union[tuple, np.ndarray]:
    """Translate the given geo coordinates into pixel locations according to the given image geotransform.

    :param mapXY:   The geo coordinates to be translated in the form (x,y) or as np.ndarray [Nx1].
    :param gt:      GDAL geotransform
    :returns:       image coordinate tuple X/Y (column, row) or np.ndarray [Nx2]
    """
    if isinstance(mapXY, np.ndarray):
        ndim = mapXY.ndim
        if ndim == 1:
            mapXY = mapXY.reshape(1, 2)
        assert mapXY.shape[1] == 2, 'An array in shape [Nx2] is needed. Got shape %s.' % mapXY.shape
        imXY = np.empty_like(mapXY, dtype=float)
        imXY[:, 0] = (mapXY[:, 0] - gt[0]) / gt[1]
        imXY[:, 1] = (mapXY[:, 1] - gt[3]) / gt[5]
        return imXY if ndim > 1 else imXY.flatten()
    else:
        return (mapXY[0] - gt[0]) / gt[1], \
               (mapXY[1] - gt[3]) / gt[5]


def imXY2mapXY(imXY: Union[tuple, np.ndarray],
               gt: (float, float, float, float, float, float)
               ) -> Union[tuple, np.ndarray]:
    """Translate the given pixel X/Y locations into geo coordinates according to the given image geotransform.

    :param imXY:    The image coordinates to be translated in the form (x,y) or as np.ndarray [Nx1].
    :param gt:      GDAL geotransform
    :returns:       geo coordinate tuple X/Y (mapX, mapY) or np.ndarray [Nx2]
    """
    if isinstance(imXY, np.ndarray):
        ndim = imXY.ndim
        if imXY.ndim == 1:
            imXY = imXY.reshape(1, 2)
        assert imXY.shape[1] == 2, 'An array in shape [Nx2] is needed. Got shape %s.' % imXY.shape
        mapXY = np.empty_like(imXY, dtype=float)
        mapXY[:, 0] = gt[0] + imXY[:, 0] * abs(gt[1])
        mapXY[:, 1] = gt[3] - imXY[:, 1] * abs(gt[5])
        return mapXY if ndim > 1 else mapXY.flatten()
    else:
        return (gt[0] + imXY[0] * abs(gt[1])), \
               (gt[3] - imXY[1] * abs(gt[5]))


def mapYX2imYX(mapYX, gt):
    return (mapYX[0] - gt[3]) / gt[5], \
           (mapYX[1] - gt[0]) / gt[1]


def imYX2mapYX(imYX, gt):
    return gt[3] - (imYX[0] * abs(gt[5])), \
           gt[0] + (imYX[1] * gt[1])


def pixelToMapYX(pixelCoords, geotransform, projection):
    # MapXYPairs = imXY2mapXY(np.array(pixelPairs), geotransform)

    # Create a spatial reference object
    srs = osr.SpatialReference()
    srs.ImportFromWkt(projection)

    # Set up the coordinate transformation object
    ct = osr.CoordinateTransformation(srs, srs)

    pixelCoords = [pixelCoords] if not type(pixelCoords[0]) in [list, tuple] else pixelCoords

    mapXYPairs = [ct.TransformPoint(pixX * geotransform[1] + geotransform[0],
                                    pixY * geotransform[5] + geotransform[3])[:2]
                  for pixX, pixY in pixelCoords]

    return [[mapY, mapX] for mapX, mapY in mapXYPairs]


def pixelToLatLon(pixelPairs: List[Sequence[float]],
                  geotransform: (float, float, float, float, float, float),
                  projection: str
                  ) -> List[Sequence[float]]:
    """Translate the given pixel X/Y locations into latitude/longitude locations.

    :param pixelPairs:      Image coordinate pairs to be translated in the form [[x1,y1],[x2,y2]]
    :param geotransform:    GDAL GeoTransform
    :param projection:      WKT string
    :returns:               The lat/lon translation of the pixel pairings in the form [[lat1,lon1],[lat2,lon2]]
    """
    MapXYPairs = imXY2mapXY(np.array(pixelPairs), geotransform)
    lons, lats = transform_any_prj(projection, 4326, MapXYPairs[:, 0], MapXYPairs[:, 1])

    # validate output lat/lon values
    if not (-180 <= np.min(lons) <= 180) or not (-180 <= np.max(lons) <= 180):
        raise RuntimeError('Output longitude values out of bounds.')
    if not (-90 <= np.min(lats) <= 90) or not (-90 <= np.max(lats) <= 90):
        raise RuntimeError('Output latitudes values out of bounds.')

    LatLonPairs = np.vstack([lats, lons]).T.tolist()

    return LatLonPairs


def latLonToPixel(latLonPairs: List[Sequence[float]],
                  geotransform: (float, float, float, float, float, float),
                  projection: str
                  ) -> List[Sequence[float]]:
    """Translate the given latitude/longitude pairs into pixel X/Y locations.

    :param latLonPairs:     The decimal lat/lon pairings to be translated in the form [[lat1,lon1],[lat2,lon2]]
    :param geotransform:    GDAL GeoTransform
    :param projection:      WKT string
    :return:            The pixel translation of the lat/lon pairings in the form [[x1,y1],[x2,y2]]
    """
    latLonArr = np.array(latLonPairs)

    # validate input lat/lon values
    if not (-180 <= np.min(latLonArr[:, 1]) <= 180) or not (-180 <= np.max(latLonArr[:, 1]) <= 180):
        raise ValueError('Longitude value out of bounds.')
    if not (-90 <= np.min(latLonArr[:, 0]) <= 90) or not (-90 <= np.max(latLonArr[:, 0]) <= 90):
        raise ValueError('Latitude value out of bounds.')

    mapXs, mapYs = transform_any_prj(4326, projection, latLonArr[:, 1], latLonArr[:, 0])
    imXYarr = mapXY2imXY(np.vstack([mapXs, mapYs]).T, geotransform)

    pixelPairs = imXYarr.tolist()

    return pixelPairs


def lonlat_to_pixel(lon, lat, inverse_geo_transform):
    """Translate the given lon, lat to the grid pixel coordinates in data array (zero start)."""
    # transform to utm
    utm_x, utm_y = transform_wgs84_to_utm(lon, lat)

    # apply inverse geo transform
    pixel_x, pixel_y = gdal.ApplyGeoTransform(inverse_geo_transform, utm_x, utm_y)
    pixel_x = int(pixel_x) - 1  # adjust to 0 start for array
    pixel_y = int(pixel_y) - 1  # adjust to 0 start for array

    return pixel_x, abs(pixel_y)  # y pixel is likly a negative value given geo_transform


def transform_GCPlist(gcpList: list,
                      prj_src: str,
                      prj_tgt: str
                      ):
    """

    :param gcpList:     list of ground control points in the output coordinate system
                        to be used for warping, e.g. [gdal.GCP(mapX,mapY,mapZ,column,row),...]
    :param prj_src:     WKT string
    :param prj_tgt:     WKT string
    :return:
    """
    return [gdal.GCP(*(list(transform_any_prj(prj_src, prj_tgt, GCP.GCPX, GCP.GCPY)) +
                       [GCP.GCPZ, GCP.GCPPixel, GCP.GCPLine]))  # Python 2.7 compatible syntax
            for GCP in gcpList]


def reproject_shapelyGeometry(shapelyGeometry: BaseGeometry,
                              prj_src: Union[str, int],
                              prj_tgt: Union[str, int]
                              ) -> BaseGeometry:
    """Reproject any shapely geometry from one projection to another.

    :param shapelyGeometry: any shapely geometry instance
    :param prj_src:         GDAL projection as WKT string or EPSG code ('epsg:1234' or <EPSG_int>)
    :param prj_tgt:         GDAL projection as WKT string or EPSG code ('epsg:1234' or <EPSG_int>)
    """
    project = pyproj.Transformer.from_proj(
        pyproj.CRS.from_user_input(prj_src),
        pyproj.CRS.from_user_input(prj_tgt),
        always_xy=True)

    with catch_warnings():
        # DeprecationWarning in pyproj 3.6.1 (future pyproj releases will fix this)
        filterwarnings(
            "ignore", category=DeprecationWarning, message=".*Conversion of an array with ndim > 0 to a scalar.*")

        return transform(project.transform, shapelyGeometry)  # apply projection
