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

from osgeo import ogr, osr

from ...dtypes.conversion import get_dtypeStr
from ...geo.projection import EPSG2WKT


__author__ = "Daniel Scheffler"


def write_shp(path_out, shapely_geom, prj=None, attrDict=None):
    shapely_geom = [shapely_geom] if not isinstance(shapely_geom, list) else shapely_geom
    attrDict = [attrDict] if not isinstance(attrDict, list) else attrDict
    # print(len(shapely_geom))
    # print(len(attrDict))
    assert len(shapely_geom) == len(attrDict), "'shapely_geom' and 'attrDict' must have the same length."
    assert os.path.exists(os.path.dirname(path_out)), 'Directory %s does not exist.' % os.path.dirname(path_out)

    print('Writing %s ...' % path_out)
    if os.path.exists(path_out):
        os.remove(path_out)

    with ogr.GetDriverByName("Esri Shapefile").CreateDataSource(path_out) as ds:
        if prj is not None:
            prj = prj if not isinstance(prj, int) else EPSG2WKT(prj)
            srs = osr.SpatialReference()
            srs.ImportFromWkt(prj)
        else:
            srs = None

        geom_type = list(set([gm.geom_type for gm in shapely_geom]))
        assert len(geom_type) == 1, 'All shapely geometries must belong to the same type. Got %s.' % geom_type

        ogr_geom_dict = dict(Point=ogr.wkbPoint, LineString=ogr.wkbLineString, Polygon=ogr.wkbPolygon)
        layer = ds.CreateLayer('', srs, ogr_geom_dict.get(geom_type[0], None))

        if isinstance(attrDict[0], dict):
            for attr in attrDict[0].keys():
                assert len(attr) <= 10, "ogr does not support fieldnames longer than 10 digits. '%s' is too long" % attr
                DTypeStr = get_dtypeStr(attrDict[0][attr])
                FieldType = \
                    ogr.OFTInteger if DTypeStr.startswith('int') else \
                    ogr.OFTReal if DTypeStr.startswith('float') else \
                    ogr.OFTString if DTypeStr.startswith('str') else \
                    ogr.OFTDateTime if DTypeStr.startswith('date') else None
                FieldDefn = ogr.FieldDefn(attr, FieldType)
                if DTypeStr.startswith('float'):
                    FieldDefn.SetPrecision(6)
                layer.CreateField(FieldDefn)  # Add one attribute

        for i in range(len(shapely_geom)):
            # Create a new feature (attribute and geometry)
            feat = ogr.Feature(layer.GetLayerDefn())
            feat.SetGeometry(ogr.CreateGeometryFromWkb(shapely_geom[i].wkb))  # Make a geometry, from Shapely object

            list_attr2set = attrDict[0].keys() if isinstance(attrDict[0], dict) else []

            for attr in list_attr2set:
                val = attrDict[i][attr]
                DTypeStr = get_dtypeStr(val)
                val = int(val) if DTypeStr.startswith('int') else float(val) if DTypeStr.startswith('float') else \
                    str(val) if DTypeStr.startswith('str') else val
                feat.SetField(attr, val)

            layer.CreateFeature(feat)
            feat.Destroy()

        # Save and close everything
        del layer
