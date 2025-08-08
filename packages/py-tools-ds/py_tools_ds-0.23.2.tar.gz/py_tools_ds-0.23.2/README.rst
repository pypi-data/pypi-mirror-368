===========
py_tools_ds
===========

A collection of geospatial data analysis tools that simplify standard operations when handling geospatial raster
and vector data as well as projections.


* Free software: Apache 2.0
* Documentation: https://danschef.git-pages.gfz-potsdam.de/py_tools_ds/doc/


Status
------

.. image:: https://git.gfz-potsdam.de/danschef/py_tools_ds/badges/main/pipeline.svg
        :target: https://git.gfz-potsdam.de/danschef/py_tools_ds/commits/main
.. image:: https://git.gfz-potsdam.de/danschef/py_tools_ds/badges/main/coverage.svg
        :target: https://danschef.git-pages.gfz-potsdam.de/py_tools_ds/coverage/
.. image:: https://img.shields.io/pypi/v/py_tools_ds.svg
        :target: https://pypi.python.org/pypi/py_tools_ds
.. image:: https://img.shields.io/conda/vn/conda-forge/py-tools-ds.svg
        :target: https://anaconda.org/conda-forge/py-tools-ds
.. image:: https://img.shields.io/pypi/l/py_tools_ds.svg
        :target: https://git.gfz-potsdam.de/danschef/py_tools_ds/blob/main/LICENSE
.. image:: https://img.shields.io/pypi/pyversions/py_tools_ds.svg
        :target: https://img.shields.io/pypi/pyversions/py_tools_ds.svg
.. image:: https://img.shields.io/pypi/dm/py_tools_ds.svg
        :target: https://pypi.python.org/pypi/py_tools_ds

See also the latest coverage_ report and the pytest_ HTML report.


Features
--------

* TODO


Installation
------------

py_tools_ds depends on some open source packages which are usually installed without problems by the automatic install
routine. However, for some projects, we strongly recommend resolving the dependency before the automatic installer
is run. This approach avoids problems with conflicting versions of the same software.
Using conda_, the recommended approach is:

*via conda + pip*

 .. code-block:: console

    # create virtual environment for py_tools_ds, this is optional
    conda create -y -q -c conda-forge --name py_tools_ds python=3
    conda activate py_tools_ds
    conda install -c conda-forge numpy gdal 'pyproj>=2.1.0' shapely scikit-image pandas

 Then install py_tools_ds using the pip installer:

 .. code-block:: console

    pip install py_tools_ds

*via conda channel (currently only for Linux-64)*

 .. code-block:: console

    # create virtual environment for py_tools_ds, this is optional
    conda create -y -q --name py_tools_ds python=3
    conda activate py_tools_ds
    conda install -c danschef -c conda-forge -c defaults py_tools_ds


History / Changelog
-------------------

You can find the protocol of recent changes in the py_tools_ds package
`here <https://git.gfz-potsdam.de/danschef/py_tools_ds/-/blob/main/HISTORY.rst>`__.


Credits
-------

The py_tools_ds package was developed within the context of the GeoMultiSens project funded
by the German Federal Ministry of Education and Research (project grant code: 01 IS 14 010 A-C).

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _coverage: https://danschef.git-pages.gfz-potsdam.de/py_tools_ds/coverage/
.. _pytest: https://danschef.git-pages.gfz-potsdam.de/py_tools_ds/test_reports/report.html
.. _conda: https://docs.conda.io/
