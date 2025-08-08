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

import json
import socket
from urllib.request import urlopen


def get_geoinfo():
    """Return a dictionary containing country, city, longitude, latitude and IP of the executing host."""
    url = 'http://ipinfo.io/json'
    info = json.loads(urlopen(url).read())
    ip = info['ip']

    urlFoLaction = "http://www.freegeoip.net/json/{0}".format(ip)
    locationInfo = json.loads(urlopen(urlFoLaction).read())

    return dict(
        Country=locationInfo['country_name'],
        City=locationInfo['city'],
        Latitude=str(locationInfo['latitude']),
        Longitude=str(locationInfo['longitude']),
        IP=str(locationInfo['ip'])
    )


def is_connected(REMOTE_SERVER="www.google.com"):
    """Check if an internet connection is present."""
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(REMOTE_SERVER)
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection((host, 80), 2)
        return True
    except Exception:
        pass
    return False
