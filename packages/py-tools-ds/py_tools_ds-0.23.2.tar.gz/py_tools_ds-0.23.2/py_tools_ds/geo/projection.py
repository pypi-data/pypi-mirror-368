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

import re
import warnings
from pyproj import CRS
from typing import Union
from osgeo import osr

from ..environment import gdal_env

__author__ = "Daniel Scheffler"


# try to set GDAL_DATA if not set or invalid
gdal_env.try2set_GDAL_DATA()


def get_proj4info(proj: Union[str, int] = None) -> str:
    """Return PROJ4 formatted projection info for the given projection.

    e.g. '+proj=utm +zone=43 +datum=WGS84 +units=m +no_defs '

    :param proj:    the projection to get PROJ4 formatted info for (WKT or 'epsg:1234' or <EPSG_int>)
    """
    return CRS.from_user_input(proj).to_proj4().strip()


def proj4_to_dict(proj4: str) -> dict:
    """Convert a PROJ4-like string into a dictionary.

    :param proj4:   the PROJ4-like string
    """
    return CRS.from_proj4(proj4).to_dict()


def dict_to_proj4(proj4dict: dict) -> str:
    """Convert a PROJ4-like dictionary into a PROJ4 string.

    :param proj4dict:   the PROJ4-like dictionary
    """
    return CRS.from_dict(proj4dict).to_proj4()


def proj4_to_WKT(proj4str: str) -> str:
    """Convert a PROJ4-like string into a WKT string.

    :param proj4str:   the PROJ4-like string
    """
    return CRS.from_proj4(proj4str).to_wkt()


def prj_equal(prj1: Union[None, int, str],
              prj2: Union[None, int, str]
              ) -> bool:
    """Check if the given two projections are equal.

    :param prj1: projection 1 (WKT or 'epsg:1234' or <EPSG_int>)
    :param prj2: projection 2 (WKT or 'epsg:1234' or <EPSG_int>)
    """
    if prj1 is None and prj2 is None or prj1 == prj2:
        return True
    else:
        # CRS.equals was added in pyproj 2.5
        crs1 = CRS.from_user_input(prj1)
        crs2 = CRS.from_user_input(prj2)

        return crs1.equals(crs2)


def isProjectedOrGeographic(prj: Union[str, int, dict]) -> Union[str, None]:
    """

    :param prj: accepts EPSG, Proj4 and WKT projections
    """
    if prj is None:
        return None

    crs = CRS.from_user_input(prj)

    return 'projected' if crs.is_projected else 'geographic' if crs.is_geographic else None


def isLocal(prj: Union[str, int, dict]) -> Union[bool, None]:
    """

    :param prj: accepts EPSG, Proj4 and WKT projections
    """
    if not prj:
        return True

    srs = osr.SpatialReference()
    if prj.startswith('EPSG:'):
        srs.ImportFromEPSG(int(prj.split(':')[1]))
    elif prj.startswith('+proj='):
        srs.ImportFromProj4(prj)
    elif 'GEOGCS' in prj or \
         'GEOGCRS' in prj or \
         'PROJCS' in prj or \
         'PROJCS' in prj or \
         'LOCAL_CS' in prj:
        srs.ImportFromWkt(prj)
    else:
        raise RuntimeError('Unknown input projection: \n%s' % prj)

    return srs.IsLocal()


def EPSG2Proj4(EPSG_code: int) -> str:
    return CRS.from_epsg(EPSG_code).to_proj4() if EPSG_code is not None else ''


def EPSG2WKT(EPSG_code: int) -> str:
    return CRS.from_epsg(EPSG_code).to_wkt(pretty=False) if EPSG_code is not None else ''


def WKT2EPSG(wkt: str) -> Union[int, None]:
    """Transform a WKT string to an EPSG code.

    :param wkt:  WKT definition
    :returns:    EPSG code
    """
    if not isinstance(wkt, str):
        raise TypeError("'wkt' must be a string. Received %s." % type(wkt))
    if not wkt:
        return None

    wkt = ''.join([line.strip().replace('\n', '').replace('\r', '')
                   for line in wkt.splitlines()])
    ccrs = CRS.from_wkt(wkt)

    if not ccrs.is_bound:
        epsg = ccrs.to_epsg()
    else:
        epsg = ccrs.source_crs.to_epsg()

    if epsg is None:
        warnings.warn('Could not find a suitable EPSG code for the input WKT string.', RuntimeWarning)
    else:
        return epsg


def get_UTMzone(prj: str) -> Union[int, None]:
    if isProjectedOrGeographic(prj) == 'projected':
        srs = osr.SpatialReference()
        srs.ImportFromWkt(prj)
        return srs.GetUTMZone()
    else:
        return None


def get_prjLonLat(fmt: str = 'wkt') -> Union[str, dict]:
    """Return standard geographic projection (EPSG 4326) in the WKT or PROJ4 format.

    :param fmt:     target format - 'WKT' or 'PROJ4'
    """
    if not re.search('wkt', fmt, re.I) or re.search('Proj4', fmt, re.I):
        raise ValueError(fmt, 'Unsupported output format.')

    if re.search('wkt', fmt, re.I):
        return CRS.from_epsg(4326).to_wkt()
    else:
        return CRS.from_epsg(4326).to_proj4()
