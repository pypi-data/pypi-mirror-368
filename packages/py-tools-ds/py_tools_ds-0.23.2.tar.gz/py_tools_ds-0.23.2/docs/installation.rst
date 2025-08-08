.. _installation:

============
Installation
============


Using Anaconda or Miniconda (recommended)
-----------------------------------------

Using conda_ (latest version recommended), py_tools_ds is installed as follows:


1. Create virtual environment for py_tools_ds (optional but recommended):

   .. code-block:: bash

    $ conda create -c conda-forge --name py_tools_ds python=3
    $ conda activate py_tools_ds


2. Then install py_tools_ds itself:

   .. code-block:: bash

    $ conda install -c conda-forge py-tools-ds


This is the preferred method to install py_tools_ds, as it always installs the most recent stable release and
automatically resolves all the dependencies.


Using pip (not recommended)
---------------------------

There is also a `pip`_ installer for py_tools_ds. However, please note that py_tools_ds depends on some
open source packages that may cause problems when installed with pip. Therefore, we strongly recommend
to resolve the following dependencies before the pip installer is run:


    * gdal
    * numpy
    * pyproj >=2.1.0
    * shapely


Then, the pip installer can be run by:

   .. code-block:: bash

    $ pip install py_tools_ds

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.



.. note::

    py_tools_ds has been tested with Python 3.8+.,
    i.e., should be fully compatible to all Python versions from 3.8 onwards.


.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/
.. _conda: https://docs.conda.io
