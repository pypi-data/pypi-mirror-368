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

import os
import sys
import re

__author__ = "Daniel Scheffler"


def find_epsgfile():
    """Locate the proj.4 epsg file (defaults to '/usr/local/share/proj/epsg')."""
    try:
        epsgfile = os.environ['GDAL_DATA'].replace('/gdal', '/proj/epsg')
        assert os.path.exists(epsgfile)
    except (KeyError, AssertionError):
        try:
            from pyproj import __file__ as pyprojpath
            epsgfile = os.path.join(os.path.dirname(pyprojpath), 'data/epsg')
            assert os.path.exists(epsgfile)
        except (ImportError, AssertionError):
            epsgfile = '/usr/local/share/proj/epsg'
            if not os.path.exists(epsgfile):
                raise RuntimeError('Could not locate epsg file for converting WKT to EPSG code. '
                                   'Please make sure that your GDAL_DATA environment variable is properly set and the '
                                   'pyproj library is installed.')
    return epsgfile


def try2set_GDAL_DATA():
    """Try to set the 'GDAL_DATA' environment variable in case it is unset or invalid."""
    if 'GDAL_DATA' not in os.environ or not os.path.isdir(os.environ['GDAL_DATA']):
        is_anaconda = 'conda' in sys.version or 'Continuum' in sys.version or \
                      re.search('conda', sys.executable, re.I)
        if is_anaconda:
            if sys.platform in ['linux', 'linux2']:
                GDAL_DATA = os.path.join(os.path.dirname(sys.executable), "..", "share", "gdal")
            else:
                GDAL_DATA = os.path.join(os.path.dirname(sys.executable), "Library", "share", "gdal")
        else:
            GDAL_DATA = os.path.join("usr", "local", "share", "gdal") if sys.platform in ['linux', 'linux2'] else ''

        if os.path.isdir(GDAL_DATA):
            os.environ['GDAL_DATA'] = GDAL_DATA
