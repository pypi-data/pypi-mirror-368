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

import sys
from time import time
from datetime import timedelta

__author__ = "Daniel Scheffler"


class Timer(object):
    def __init__(self, timeout=None, use_as_callback=False):
        self.starttime = time()
        self.endtime = self.starttime + timeout if timeout else None
        self.timeout = timeout
        self.use_as_cb = use_as_callback

    @property
    def timed_out(self):
        if self.endtime:
            if time() > self.endtime:
                if self.use_as_cb:
                    # raise a KeyBoardInterrupt instead of a TimeOutError
                    # as this is catchable by gdal.GetLastException()
                    raise KeyboardInterrupt()
                else:
                    return True
            else:
                if self.use_as_cb:
                    pass
                else:
                    return False
        else:
            return False

    @property
    def elapsed(self):
        return str(timedelta(seconds=time() - self.starttime)).split('.')[0]
        # return '%.2f sek' %(time()-self.starttime)

    def __call__(self, percent01, message, user_data):
        """Allow Timer instances to be callable and thus to be used as callback function, e.g., for GDAL.

        :param percent01:   this is not used but expected when used as GDAL callback
        :param message:     this is not used but expected when used as GDAL callback
        :param user_data:   this is not used but expected when used as GDAL callback
        :return:
        """
        return self.timed_out


class ProgressBar(object):
    def __init__(self, prefix='', suffix='Complete', decimals=1, barLength=50, show_elapsed=True,
                 timeout=None, use_as_callback=False, out=sys.stderr):
        """Call an instance of this class in a loop to create terminal progress bar.

        NOTE: This class can also be used as callback function, e.g. for GDAL.
              Just pass an instance of ProgressBar to the respective callback keyword.

        :param prefix:         prefix string (Str)
        :param suffix:         suffix string (Str)
        :param decimals:       positive number of decimals in percent complete (Int)
        :param barLength:      character length of bar (Int)
        :param show_elapsed:   displays the elapsed time right after the progress bar (bool)
        :param timeout:        breaks the process after a given time in seconds (float)

        http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
        """
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.barLength = barLength
        self.show_elapsed = show_elapsed
        self.timeout = timeout
        self.Timer = Timer(timeout=timeout)
        self.use_as_cb = use_as_callback
        self.out = out

        self._percdone = list(range(10, 110, 10))

    def print_progress(self, percent: float):
        """Print progress.

        - based on http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console.

        :param percent: a number between 0 and 100
        :return:
        """
        if self.Timer.timed_out:
            if self.out is not None:
                self.out.flush()
            if self.use_as_cb:
                # raise a KeyBoardInterrupt instead of a TimeOutError
                # as this is catchable by gdal.GetLastException()
                raise KeyboardInterrupt()
            else:
                raise TimeoutError(f'No progress for {self.timeout} seconds.')

        formatStr = "{0:." + str(self.decimals) + "f}"
        percents = formatStr.format(percent)
        filledLength = int(round(self.barLength * percent / 100))
        # bar         = '█' * filledLength + '-' * (barLength - filledLength) # this is not compatible to shell console
        bar = '=' * filledLength + '-' * (self.barLength - filledLength)

        if self.out is not None:
            # reset the cursor to the beginning of the line and allows to write over what was previously on the line
            self.out.write('\r')

            # [%s/%s] numberDone
            suffix = self.suffix if not self.show_elapsed else '%s  => %s' % (self.suffix, self.Timer.elapsed)
            self.out.write('%s |%s| %s%s %s' % (self.prefix, bar, percents, '%', suffix))

            if percent >= 100.:
                self.out.write('\n')

            self.out.flush()

        else:
            # in some environments, sys.stderr can also be None
            # pydocs: usually Windows GUI apps that aren’t connected to a console and Python apps started with pythonw
            try:
                percnext = self._percdone[0]
                if percent >= percnext:
                    print(f'{percents} %')
                    self._percdone.pop(0)

            except IndexError:  # pragma: no cover
                pass

    def __call__(self, percent01, message, user_data):
        """Allow ProgressBar instances to be callable and thus to be used as callback function, e.g., for GDAL.

        :param percent01:   a float number between 0 and 1
        :param message:     this is not used but expected when used as GDAL callback
        :param user_data:   this is not used but expected when used as GDAL callback
        :return:
        """
        self.print_progress(percent01 * 100)


def tqdm_hook(t):
    """

    Wraps tqdm instance. Don't forget to close() or __exit__()
    the tqdm instance once you're done with it (easiest using `with` syntax).

    .. code-block:: python
       :caption: Example:

       with tqdm(...) as t:
           reporthook = my_hook(t)
           urllib.urlretrieve(..., reporthook=reporthook)

    https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
    """
    last_b = [0]

    def inner(b=1, bsize=1, tsize=None):
        """
        b  : int, optional
            Number of blocks just transferred [default: 1].
        bsize  : int, optional
            Size of each block (in tqdm units) [default: 1].
        tsize  : int, optional
            Total size (in tqdm units). If [default: None] remains unchanged.
        """
        if tsize is not None:
            t.total = tsize
        t.update((b - last_b[0]) * bsize)
        last_b[0] = b

    return inner


def printPercentage(i, i_total):
    """Print a percentage counter from within a loop.

    .. code-block:: python
       :caption: Example:

       for i in range(100+1):
           time.sleep(0.1)
           printPercentage(i)

    :param i:
    :param i_total:
    :return:

    https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
    """
    sys.stdout.write(('=' * i) + ('' * (i_total - i)) + ("\r [ %d" % i + "% ] "))
    sys.stdout.flush()
