Installation
============

Requirements
------------

OWSLib requires a Python interpreter, as well as `ElementTree <https://docs.python.org/2/library/xml.etree.elementtree.html>`_ or `lxml <http://lxml.de>`_ for XML parsing.

Install
-------

PyPI:

.. code-block:: bash

  easy_install OWSLib
  # pip works too
  pip install OWSLib

Git:

.. code-block:: bash

  git clone git://github.com/geopython/OWSLib.git


Anaconda:

.. note::

   The OWSLib conda packages are provided by the community, not OSGEO, and therefore there may be
   multiple packages available.  To search all conda channels: http://anaconda.org/search?q=type%3Aconda+owslib
   However usually conda-forge will be the most up-to-date.

.. code-block:: bash

  conda install -c conda-forge owslib

openSUSE:

.. code-block:: bash

  zypper ar http://download.opensuse.org/repositories/Application:/Geo/openSUSE_12.1/ GEO
  zypper refresh
  zypper install owslib

CentOS:

.. code-block:: bash

  wget -O /etc/yum.repos.d/CentOS-CBS.repo http://download.opensuse.org/repositories/Application:/Geo/CentOS_6/Application:Geo.repo
  yum install owslib

RedHat Enterprise Linux

.. code-block:: bash

  wget -O /etc/yum.repos.d/RHEL-CBS.repo http://download.opensuse.org/repositories/Application:/Geo/RHEL_6/Application:Geo.repo
  yum install owslib

Fedora:

.. note::

  As of Fedora 20, OWSLib is part of the Fedora core package collection

.. code-block:: bash

  yum install OWSLib
