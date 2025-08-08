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

import warnings
from typing import Iterable, Tuple
import numpy as np

# custom
from shapely.geometry import Polygon

__author__ = "Daniel Scheffler"


def get_corner_coordinates(gt, cols, rows):
    """Return (ULxy, LLxy, LRxy, URxy) in the same coordinate units like the given geotransform."""
    ext = []
    xarr = [0, cols]
    yarr = [0, rows]
    for px in xarr:
        for py in yarr:
            x = gt[0] + (px * gt[1]) + (py * gt[2])
            y = gt[3] + (px * gt[4]) + (py * gt[5])
            ext.append([x, y])
        yarr.reverse()
    return ext


def calc_FullDataset_corner_positions(mask_1bit: np.ndarray,
                                      assert_four_corners: bool = True,
                                      algorithm: str = 'shapely'
                                      ) -> list:
    """Calculate the image coordinates of the true data corners from a nodata mask.

    NOTE: Algorithm 'shapely' calculates the corner coordinates of the convex hull of the given mask. Since the convex
    hull not always reflects all the true corner coordinates the result can have a limitation in this regard.

    :param mask_1bit:               2D-numpy array 1bit
    :param assert_four_corners:     whether to assert four corners or not
    :param algorithm:               shapely' or 'numpy' (default: 'shapely')
    :return:                        [UL, UR, LL, LR] as [(ULrow,ULcol),(URrow,URcol),...]
    """
    # check if the mask extent covers real data or only nodata
    pixVals = np.unique(mask_1bit)
    if not (True in pixVals or 1 in pixVals):
        # 'According to the given mask the mask extent is completely outside the image.
        # No calculation of image corner coordinates possible.'
        return []

    rows, cols = mask_1bit.shape[:2]

    if sum([mask_1bit[0, 0], mask_1bit[0, cols - 1], mask_1bit[rows - 1, 0], mask_1bit[rows - 1, cols - 1]]) == 4:
        # if mask contains pixel value 1 in all the four corners: return outer corner coords
        out = [(0, 0), (0, cols - 1), (rows - 1, 0), (rows - 1, cols - 1)]  # UL, UR, LL, LR
    else:
        assert algorithm in ['shapely', 'numpy'], "Algorithm '%' does not exist. Choose between 'shapely' and 'numpy'."

        if algorithm == 'shapely':
            # get outline
            topbottom = np.empty((1, 2 * mask_1bit.shape[1]), dtype=np.uint16)
            topbottom[0, 0:mask_1bit.shape[1]] = np.argmax(mask_1bit, axis=0)
            topbottom[0, mask_1bit.shape[1]:] = (mask_1bit.shape[0] - 1) - np.argmax(np.flipud(mask_1bit), axis=0)
            mask = np.tile(np.any(mask_1bit, axis=0), (2,))
            xvalues = np.tile(np.arange(mask_1bit.shape[1]), (1, 2))
            outline = np.vstack([topbottom, xvalues])[:, mask].T

            with warnings.catch_warnings():
                warnings.simplefilter('ignore')  # FIXME not working
                poly = Polygon(outline).convex_hull
                poly = poly.simplify(20, preserve_topology=True)
                poly = Polygon(list(set(
                    poly.exterior.coords))).convex_hull  # eliminiate duplicates except of 1 (because poly is closed)
                unique_corn_YX = sorted(set(poly.exterior.coords),
                                        key=lambda x: poly.exterior.coords[:].index(x))  # [(rows,cols),rows,cols]

            if assert_four_corners or len(unique_corn_YX) == 4:
                # sort calculated corners like this: [UL, UR, LL, LR]
                assert len(unique_corn_YX) == 4, \
                    'Found %s unique corner coordinates instead of 4. Exiting.' % len(unique_corn_YX)

                def get_dist(P1yx, P2yx):
                    return np.sqrt((P1yx[0] - P2yx[0]) ** 2 + (P1yx[1] - P2yx[1]) ** 2)

                def get_closest(tgtYX, srcYXs):
                    return srcYXs[np.array([get_dist(tgtYX, srcYX) for srcYX in srcYXs]).argmin()]

                out = [get_closest(tgtYX, unique_corn_YX) for tgtYX in
                       [(0, 0), (0, cols - 1), (rows - 1, 0), (rows - 1, cols - 1)]]
            else:
                out = unique_corn_YX

        else:  # alg='numpy'
            cols_containing_data = np.any(mask_1bit, axis=0)
            rows_containing_data = np.any(mask_1bit, axis=1)

            first_dataCol = list(cols_containing_data).index(True)
            last_dataCol = cols - (list(reversed(cols_containing_data)).index(True) + 1)
            first_dataRow = list(rows_containing_data).index(True)
            last_dataRow = rows - (list(reversed(rows_containing_data)).index(True) + 1)

            StartStopRows_in_first_dataCol = [list(mask_1bit[:, first_dataCol]).index(True),
                                              (rows - list(reversed(mask_1bit[:, first_dataCol])).index(True) + 1)]
            StartStopRows_in_last_dataCol = [list(mask_1bit[:, last_dataCol]).index(True),
                                             (rows - list(reversed(mask_1bit[:, last_dataCol])).index(True) + 1)]
            StartStopCols_in_first_dataRow = [list(mask_1bit[first_dataRow, :]).index(True),
                                              (cols - list(reversed(mask_1bit[first_dataRow, :])).index(True) + 1)]
            StartStopCols_in_last_dataRow = [list(mask_1bit[last_dataRow, :]).index(True),
                                             (cols - list(reversed(mask_1bit[last_dataRow, :])).index(True) + 1)]

            if True in [abs(np.diff(i)[0]) > 10 for i in
                        [StartStopRows_in_first_dataCol, StartStopRows_in_last_dataCol,
                         StartStopCols_in_first_dataRow, StartStopCols_in_last_dataRow]]:
                # In case of cut image corners (e.g. ALOS AVNIR-2 Level-1B2):
                # Calculation of trueDataCornerPos outside of the image.'''
                line_N = ((StartStopCols_in_first_dataRow[1], first_dataRow),
                          (last_dataCol, StartStopRows_in_last_dataCol[0]))
                line_S = ((first_dataCol, StartStopRows_in_first_dataCol[1]),
                          (StartStopCols_in_last_dataRow[0], last_dataRow))
                line_W = ((StartStopCols_in_first_dataRow[0], first_dataRow),
                          (first_dataCol, StartStopRows_in_first_dataCol[0]))
                line_O = ((last_dataCol, StartStopRows_in_last_dataCol[1]),
                          (StartStopCols_in_last_dataRow[1], last_dataRow))
                from .vector.topology import find_line_intersection_point  # import here avoids circular dependencies
                corners = [list(reversed(find_line_intersection_point(line_N, line_W))),
                           list(reversed(find_line_intersection_point(line_N, line_O))),
                           list(reversed(find_line_intersection_point(line_S, line_W))),
                           list(reversed(find_line_intersection_point(line_S, line_O)))]
            else:
                dataRow_in_first_dataCol = np.mean(StartStopRows_in_first_dataCol)
                dataRow_in_last_dataCol = np.mean(StartStopRows_in_last_dataCol)
                dataCol_in_first_dataRow = np.mean(StartStopCols_in_first_dataRow)
                dataCol_in_last_dataRow = np.mean(StartStopCols_in_last_dataRow)
                corners = [(first_dataRow, dataCol_in_first_dataRow), (dataRow_in_last_dataCol, last_dataCol),
                           (last_dataRow, dataCol_in_last_dataRow), (dataRow_in_first_dataCol, first_dataCol)]

            def get_closest(refR, refC):
                return corners[np.array([np.sqrt((refR - c[0]) ** 2 + (refC - c[1]) ** 2) for c in
                                         corners]).argmin()]  # FIXME this can also result in only 2 corners
            out = [get_closest(refR, refC) for refR, refC in
                   [(0, 0), (0, cols - 1), (rows - 1, 0), (rows - 1, cols - 1)]]
            # if UL[0] == 0 and UR[0] == 0:
            #     envi.save_image(os.path.abspath('./testing/out/__faulty_mask_1bit.hdr'),
            #                     self.mask_1bit, dtype= 'uint8', interleave='bsq', ext='.bsq',force=True)
            # print(UL,UR,LL,LR)
    return out


def corner_coord_to_minmax(
    corner_coords:  Iterable[Tuple[float, float]]
) -> (float, float, float, float):
    """Return the bounding coordinates for a given set of XY coordinates.

    :param corner_coords:   four XY tuples of corner coordinates. Their order does not matter.
    :return: xmin,xmax,ymin,ymax
    """
    x_vals, y_vals = zip(*corner_coords)
    xmin, xmax, ymin, ymax = min(x_vals), max(x_vals), min(y_vals), max(y_vals)

    return xmin, xmax, ymin, ymax
