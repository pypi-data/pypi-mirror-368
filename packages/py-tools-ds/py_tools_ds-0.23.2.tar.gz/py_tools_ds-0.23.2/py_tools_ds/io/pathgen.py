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

import tempfile
import os

__author__ = "Daniel Scheffler"


def get_tempfile(ext=None, prefix=None, tgt_dir=None):
    """Return the path to a tempfile.mkstemp() file that can be passed to any function that expects a physical path.

    NOTE: The tempfile has to be deleted manually.

    :param ext:     file extension (None if None)
    :param prefix:  optional file prefix
    :param tgt_dir: target directory (automatically set if None)
    """
    prefix = 'py_tools_ds__' if prefix is None else prefix
    fd, path = tempfile.mkstemp(prefix=prefix, suffix=ext, dir=tgt_dir)
    os.close(fd)
    return path


def get_generic_outpath(dir_out='', fName_out='', prefix='', ext='', create_outDir=True,
                        prevent_overwriting=False):
    """Generate an output path accourding to the given parameters.

    :param dir_out:             output directory
    :param fName_out:           output filename
    :param prefix:              a prefix for the output filename. ignored if fName_out is given
    :param ext:                 the file extension to use
    :param create_outDir:       whether to automatically create the output directory or not
    :param prevent_overwriting: whether to prevent that an output filename is chosen which exists in the filesystem
    :return:
    """
    dir_out = dir_out if dir_out else os.path.abspath(os.path.curdir)
    if create_outDir and not os.path.isdir(dir_out):
        os.makedirs(dir_out)

    if not fName_out:
        fName_out = '%soutput' % prefix + ('.%s' % ext if ext else '')
        if prevent_overwriting:
            count = 1
            while os.path.exists(os.path.join(dir_out, fName_out)):
                if count == 1:
                    fName_out += str(count)
                else:
                    fName_out[-1] = str(count)

    return os.path.join(dir_out, fName_out)
