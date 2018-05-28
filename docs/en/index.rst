=======================================================
OWSLib |release| documentation
=======================================================

.. toctree::
   :maxdepth: 2

.. image:: https://www.openhub.net/p/owslib/widgets/project_partner_badge.gif
   :width: 193px
   :height: 33px
   :alt: OWSLib
   :target: https://www.openhub.net/p/owslib?ref=WidgetProjectPartnerBadge

:Author: Tom Kralidis
:Contact: tomkralidis at gmail.com
:Release: |release|
:Date: |today|

Introduction
============

OWSLib is a Python package for client programming with `Open Geospatial Consortium`_ (OGC) web service (hence OWS) interface standards, and their related content models.

OWSLib was buried down inside PCL, but has been brought out as a separate project in `r481 <http://trac.gispython.org/lab/changeset/481>`_.

Features
========

Standards Support
-----------------

+-------------------+---------------------+
| Standard          | Version(s)          |
+===================+=====================+
| `OGC WMS`_        | 1.1.1               |
+-------------------+---------------------+
| `OGC WFS`_        | 1.0.0, 1.1.0, 2.0.0 |
+-------------------+---------------------+
| `OGC WCS`_        | 1.0.0, 1.1.0        |
+-------------------+---------------------+
| `OGC WMC`_        | 1.1.0               |
+-------------------+---------------------+
| `OGC SOS`_        | 1.0.0, 2.0.0        |
+-------------------+---------------------+
| `OGC SensorML`_   | 1.0.1               |
+-------------------+---------------------+
| `OGC CSW`_        | 2.0.2               |
+-------------------+---------------------+
| `OGC WPS`_        | 1.0.0               |
+-------------------+---------------------+
| `OGC Filter`_     | 1.1.0               |
+-------------------+---------------------+
| `OGC OWS Common`_ | 1.0.0, 1.1.0, 2.0   |
+-------------------+---------------------+
| `NASA DIF`_       | 9.7                 |
+-------------------+---------------------+
| `FGDC CSDGM`_     | 1998                |
+-------------------+---------------------+
| `ISO 19139`_      | 2007                |
+-------------------+---------------------+
| `Dublin Core`_    | 1.1                 |
+-------------------+---------------------+
| `Swiss GM03`_     | 2.3                 |
+-------------------+---------------------+
| `WMTS`_           | 1.0.0               |
+-------------------+---------------------+
| `WaterML`_        | 1.0, 1.1, 2.0       |
+-------------------+---------------------+

Installation
============

Requirements
------------

OWSLib requires a Python interpreter, as well as `ElementTree <https://docs.python.org/2/library/xml.etree.elementtree.html>`_ or `lxml <http://lxml.de>`_ for XML parsing.

Install
-------

PyPI:

.. code-block:: bash

  $ easy_install OWSLib
  # pip works too
  $ pip install OWSLib

Git:

.. code-block:: bash

  $ git clone git://github.com/geopython/OWSLib.git


Anaconda:

.. note::

   The OWSLib conda packages are provided by the community, not OSGEO, and therefore there may be
   multiple packages available.  To search all conda channels: http://anaconda.org/search?q=type%3Aconda+owslib
   However usually conda-forge will be the most up-to-date.

.. code-block:: bash

  $ conda install -c conda-forge owslib

openSUSE:

.. code-block:: bash

  $ zypper ar http://download.opensuse.org/repositories/Application:/Geo/openSUSE_12.1/ GEO
  $ zypper refresh
  $ zypper install owslib

CentOS:

.. code-block:: bash

  $ wget -O /etc/yum.repos.d/CentOS-CBS.repo http://download.opensuse.org/repositories/Application:/Geo/CentOS_6/Application:Geo.repo
  $ yum install owslib

RedHat Enterprise Linux

.. code-block:: bash

  $ wget -O /etc/yum.repos.d/RHEL-CBS.repo http://download.opensuse.org/repositories/Application:/Geo/RHEL_6/Application:Geo.repo
  $ yum install owslib

Fedora:

.. note::

  As of Fedora 20, OWSLib is part of the Fedora core package collection

.. code-block:: bash

  $ yum install OWSLib

Usage
=====

WMS
---

Find out what a WMS has to offer. Service metadata:

.. code-block:: python

  >>> from owslib.wms import WebMapService
  >>> wms = WebMapService('http://wms.jpl.nasa.gov/wms.cgi', version='1.1.1')
  >>> wms.identification.type
  'OGC:WMS'
  >>> wms.identification.title
  'JPL Global Imagery Service'

Available layers:

.. code-block:: python

  >>> list(wms.contents)
  ['global_mosaic', 'global_mosaic_base', 'us_landsat_wgs84', 'srtm_mag', 'daily_terra_721', 'daily_aqua_721', 'daily_terra_ndvi', 'daily_aqua_ndvi', 'daily_terra', 'daily_aqua', 'BMNG', 'modis', 'huemapped_srtm', 'srtmplus', 'worldwind_dem', 'us_ned', 'us_elevation', 'us_colordem']

Details of a layer:

.. code-block:: python

  >>> wms['global_mosaic'].title
  'WMS Global Mosaic, pan sharpened'
  >>> wms['global_mosaic'].queryable
  0
  >>> wms['global_mosaic'].opaque
  0
  >>> wms['global_mosaic'].boundingBox
  >>> wms['global_mosaic'].boundingBoxWGS84
  (-180.0, -60.0, 180.0, 84.0)
  >>> wms['global_mosaic'].crsOptions
  ['EPSG:4326', 'AUTO:42003']
  >>> wms['global_mosaic'].styles
  {'pseudo_bright': {'title': 'Pseudo-color image (Uses IR and Visual bands, 542 mapping), gamma 1.5'}, 'pseudo': {'title': '(default) Pseudo-color image, pan sharpened (Uses IR and Visual bands, 542 mapping), gamma 1.5'}, 'visual': {'title': 'Real-color image, pan sharpened (Uses the visual bands, 321 mapping), gamma 1.5'}, 'pseudo_low': {'title': 'Pseudo-color image, pan sharpened (Uses IR and Visual bands, 542 mapping)'}, 'visual_low': {'title': 'Real-color image, pan sharpened (Uses the visual bands, 321 mapping)'}, 'visual_bright': {'title': 'Real-color image (Uses the visual bands, 321 mapping), gamma 1.5'}}

Available methods, their URLs, and available formats:

.. code-block:: python

  >>> [op.name for op in wms.operations]
  ['GetCapabilities', 'GetMap']
  >>> wms.getOperationByName('GetMap').methods
  {'Get': {'url': 'http://wms.jpl.nasa.gov/wms.cgi?'}}
  >>> wms.getOperationByName('GetMap').formatOptions
  ['image/jpeg', 'image/png', 'image/geotiff', 'image/tiff']

That's everything needed to make a request for imagery:

.. code-block:: python

  >>> img = wms.getmap(   layers=['global_mosaic'],
  ...                     styles=['visual_bright'],
  ...                     srs='EPSG:4326',
  ...                     bbox=(-112, 36, -106, 41),
  ...                     size=(300, 250),
  ...                     format='image/jpeg',
  ...                     transparent=True
  ...                     )
  >>> out = open('jpl_mosaic_visb.jpg', 'wb')
  >>> out.write(img.read())
  >>> out.close()

Result:

.. image:: ../_static/jpl_mosaic_visb.jpg
   :width: 300px
   :height: 250px
   :alt: WMS GetMap generated by OWSLib


WFS
---
Connect to a WFS and inspect its capabilities.

::

    >>> from owslib.wfs import WebFeatureService
    >>> wfs11 = WebFeatureService(url='http://geoserv.weichand.de:8080/geoserver/wfs', version='1.1.0')
    >>> wfs11.identification.title
    'INSPIRE WFS 2.0 DemoServer Verwaltungsgrenzen Bayern

    >>> [operation.name for operation in wfs11.operations]
    ['GetCapabilities', 'DescribeFeatureType', 'GetFeature', 'GetGmlObject']

List FeatureTypes

::

    >>> list(wfs11.contents)
    ['bvv:vg_ex', 'bvv:bayern_ex', 'bvv:lkr_ex', 'bvv:regbez_ex', 'bvv:gmd_ex']

Download GML using ``typename``, ``bbox`` and ``srsname``.

::

    >>> # OWSLib will switch the axis order from EN to NE automatically if designated by EPSG-Registry
    >>> response = wfs11.getfeature(typename='bvv:gmd_ex', bbox=(4500000,5500000,4500500,5500500), srsname='urn:x-ogc:def:crs:EPSG:31468')

Download GML using ``typename`` and ``filter``. OWSLib currently only
support filter building for WFS 1.1 (FE.1.1).

::

    >>> from owslib.fes import *
    >>> from owslib.etree import etree
    >>> from owslib.wfs import WebFeatureService
    >>> wfs11 = WebFeatureService(url='http://geoserv.weichand.de:8080/geoserver/wfs', version='1.1.0')

    >>> filter = PropertyIsLike(propertyname='bez_gem', literal='Ingolstadt', wildCard='*')
    >>> filterxml = etree.tostring(filter.toXML()).decode("utf-8")
    >>> response = wfs11.getfeature(typename='bvv:gmd_ex', filter=filterxml)

Save response to a file.

::

    >>> out = open('/tmp/data.gml', 'wb')
    >>> out.write(bytes(response.read(), 'UTF-8'))
    >>> out.close()

Download GML using ``StoredQueries``\ (only available for WFS 2.0
services)

::

    >>> from owslib.wfs import WebFeatureService
    >>> wfs20 = WebFeatureService(url='http://geoserv.weichand.de:8080/geoserver/wfs', version='2.0.0')

    >>> # List StoredQueries
    >>> [storedquery.id for storedquery in wfs20.storedqueries]
    ['bboxQuery', 'urn:ogc:def:query:OGC-WFS::GetFeatureById', 'GemeindeByGemeindeschluesselEpsg31468', 'DWithinQuery']

    >>> # List Parameters for StoredQuery[1]
    >>> parameter.name for parameter in wfs20.storedqueries[1].parameters]
    ['ID']


    >>> response = wfs20.getfeature(storedQueryID='urn:ogc:def:query:OGC-WFS::GetFeatureById', storedQueryParams={'ID':'gmd_ex.1'})


WCS
---

CSW
---

Connect to a CSW, and inspect its properties:

.. code-block:: python

  >>> from owslib.csw import CatalogueServiceWeb
  >>> csw = CatalogueServiceWeb('http://geodiscover.cgdi.ca/wes/serviceManagerCSW/csw')
  >>> csw.identification.type
  'CSW'
  >>> [op.name for op in csw.operations]
  ['GetCapabilities', 'GetRecords', 'GetRecordById', 'DescribeRecord', 'GetDomain']

Get supported resultType's:

.. code-block:: python

  >>> csw.getdomain('GetRecords.resultType')
  >>> csw.results
  {'values': ['results', 'validate', 'hits'], 'parameter': 'GetRecords.resultType', 'type': 'csw:DomainValuesType'}
  >>>

Search for bird data:

.. code-block:: python

  >>> from owslib.fes import PropertyIsEqualTo, PropertyIsLike, BBox
  >>> birds_query = PropertyIsEqualTo('csw:AnyText', 'birds')
  >>> csw.getrecords2(constraints=[birds_query], maxrecords=20)
  >>> csw.results
  {'matches': 101, 'nextrecord': 21, 'returned': 20}
  >>> for rec in csw.records:
  ...     print(csw.records[rec].title)
  ...
  ALLSPECIES
  NatureServe Canada References
  Bird Studies Canada - BirdMap WMS
  Parks Canada Geomatics Metadata Repository
  Bird Studies Canada - BirdMap WFS
  eBird Canada - Survey Locations
  WHC CitizenScience WMS
  Project FeederWatch - Survey Locations
  North American Bird Banding and Encounter Database
  Wildlife Habitat Canada CitizenScience WFS
  Parks Canada Geomatics Metadata Repository
  Parks Canada Geomatics Metadata Repository
  Wildlife Habitat Canada CitizenScience WMS
  Canadian IBA Polygon layer
  Land
  Wildlife Habitat Canada CitizenScience WMS
  WATER
  Parks Canada Geomatics Metadata Repository
  Breeding Bird Survey
  SCALE
  >>>

Search for bird data in Canada:

.. code-block:: python

  >>> bbox_query = BBox([-141,42,-52,84])
  >>> csw.getrecords2(constraints=[birds_query, bbox_query])
  >>> csw.results
  {'matches': 3, 'nextrecord': 0, 'returned': 3}
  >>>

Search for keywords like 'birds' or 'fowl'

.. code-block:: python

  >>> birds_query_like = PropertyIsLike('dc:subject', '%birds%')
  >>> fowl_query_like = PropertyIsLike('dc:subject', '%fowl%')
  >>> csw.getrecords2(constraints=[birds_query_like, fowl_query_like])
  >>> csw.results
  {'matches': 107, 'nextrecord': 11, 'returned': 10}
  >>>

Search for a specific record:

.. code-block:: python

  >>> csw.getrecordbyid(id=['9250AA67-F3AC-6C12-0CB9-0662231AA181'])
  >>> c.records['9250AA67-F3AC-6C12-0CB9-0662231AA181'].title
  'ALLSPECIES'

Search with a CQL query

.. code-block:: python

  >>> csw.getrecords(cql='csw:AnyText like "%birds%"')

Transaction: insert

.. code-block:: python

  >>> csw.transaction(ttype='insert', typename='gmd:MD_Metadata', record=open("file.xml").read())

Transaction: update

.. code-block:: python


  >>> # update ALL records
  >>> csw.transaction(ttype='update', typename='csw:Record', propertyname='dc:title', propertyvalue='New Title')
  >>> # update records satisfying keywords filter
  >>> csw.transaction(ttype='update', typename='csw:Record', propertyname='dc:title', propertyvalue='New Title', keywords=['birds','fowl'])
  >>> # update records satisfying BBOX filter
  >>> csw.transaction(ttype='update', typename='csw:Record', propertyname='dc:title', propertyvalue='New Title', bbox=[-141,42,-52,84])

Transaction: delete

.. code-block:: python

  >>> # delete ALL records
  >>> csw.transaction(ttype='delete', typename='gmd:MD_Metadata')
  >>> # delete records satisfying keywords filter
  >>> csw.transaction(ttype='delete', typename='gmd:MD_Metadata', keywords=['birds','fowl'])
  >>> # delete records satisfying BBOX filter
  >>> csw.transaction(ttype='delete', typename='gmd:MD_Metadata', bbox=[-141,42,-52,84])

Harvest a resource

.. code-block:: python

  >>> csw.harvest('http://host/url.xml', 'http://www.isotc211.org/2005/gmd')


WMC
---

WPS
---

.. include:: ../../tests/_broken/doctests_sphinx/wps_example_usgs.txt

SOS 1.0
-------

GetCapabilities

.. include:: ../../tests/doctests/sos_10_getcapabilities.txt

GetObservation

.. include:: ../../tests/doctests/sos_10_ndbc_getobservation.txt

SOS 2.0
-------

Examples of service metadata and GetObservation
+++++++++++++++++++++++++++++++++++++++++++++++

.. include:: ../../tests/_broken/doctests_sphinx/sos_20_52N_demo.txt

Using the GetObservation response decoder for O&M and WaterML2.0 results
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. include:: ../../tests/_broken/doctests_sphinx/sos_20_timeseries_decoder_ioos.txt

SensorML
--------
.. include:: ../../tests/doctests/sml_ndbc_station.txt

ISO
---

.. code-block:: python

  >>> from owslib.iso import *
  >>> m=MD_Metadata(etree.parse('tests/resources/9250AA67-F3AC-6C12-0CB9-0662231AA181_iso.xml'))
  >>> m.identification.topiccategory
  'farming'
  >>>

ISO Codelists:

.. include:: ../../tests/doctests/iso_codelist.txt

CRS Handling
------------

.. include:: ../../tests/doctests/crs.txt

Dublin Core
-----------

NASA DIF
--------

FGDC
----

Swiss GM03
----------

.. include:: ../../tests/doctests/gm03_parse.txt

WMTS
----

.. include:: ../../tests/_broken/doctests_sphinx/wmts_demo.txt

Result:

.. image:: ../_static/nasa_modis_terra_truecolour.jpg
   :width: 512px
   :height: 512px
   :alt: WMTS GetTile generated by OWSLib

WaterML
-------

.. include:: ../../tests/doctests/wml11_cuahsi.txt

Development
===========

The OWSLib wiki is located at https://github.com/geopython/OWSLib/wiki

The OWSLib source code is available at https://github.com/geopython/OWSLib

You can find out about software metrics at the OWSLib ohloh page at http://www.ohloh.net/p/OWSLib.

Testing
-------

.. code-block:: bash

   $ python setup.py test

Or ...

.. code-block:: bash

    # install requirements
    $ pip install -r requirements.txt
    $ pip install -r requirements-dev.txt # needed for tests only

    # run tests
    python -m pytest

    # additional pep8 tests
    pep8 owslib/wmts.py

Support
=======

Mailing Lists
-------------

OWSLib provides users and developers mailing lists.  Subscription options and archives are available at http://lists.osgeo.org/mailman/listinfo/owslib-users and http://lists.osgeo.org/mailman/listinfo/owslib-devel.

Submitting Questions to Community
---------------------------------

To submit questions to a mailing list, first join the list by following the subscription procedure above. Then post questions to the list by sending an email message to either owslib-users@lists.osgeo.org or owslib-devel@lists.osgeo.org.

Searching the Archives
----------------------

All Community archives are located in http://lists.osgeo.org/pipermail/owslib-users/ http://lists.osgeo.org/pipermail/owslib-devel/

Metrics
-------

You can find out about software metrics at the OWSLib `ohloh`_ page.

IRC
---

As well, visit OWSLib on IRC on ``#geopython`` at `freenode`_ for realtime discussion.


Logging
=======

OWSLib logs messages to the 'owslib' named python logger.  You may configure your
application to use the log messages like so:

.. code-block:: python

    import logging
    owslib_log = logging.getLogger('owslib')
    # Add formatting and handlers as needed
    owslib_log.setLevel(logging.DEBUG)


License
=======

Copyright (c) 2006, Ancient World Mapping Center
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the University of North Carolina nor the names of
      its contributors may be used to endorse or promote products derived
      from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

Credits
=======

.. include:: ../../AUTHORS.rst

.. _`Open Geospatial Consortium`: http://www.opengeospatial.org/
.. _`OGC WMS`: http://www.opengeospatial.org/standards/wms
.. _`OGC WFS`: http://www.opengeospatial.org/standards/wfs
.. _`OGC WCS`: http://www.opengeospatial.org/standards/wcs
.. _`OGC WMC`: http://www.opengeospatial.org/standards/wmc
.. _`OGC WPS`: http://www.opengeospatial.org/standards/wps
.. _`OGC SOS`: http://www.opengeospatial.org/standards/sos
.. _`OGC O&M`: http://www.opengeospatial.org/standards/om
.. _`OGC WaterML2.0`: http://www.opengeospatial.org/standards/waterml
.. _`OGC SensorML`: http://www.opengeospatial.org/standards/sensorml
.. _`OGC CSW`: http://www.opengeospatial.org/standards/cat
.. _`OGC WMTS`: http://www.opengeospatial.org/standards/wmts
.. _`OGC Filter`: http://www.opengeospatial.org/standards/filter
.. _`OGC OWS Common`: http://www.opengeospatial.org/standards/common
.. _`NASA DIF`: http://gcmd.nasa.gov/User/difguide/
.. _`FGDC CSDGM`: http://www.fgdc.gov/metadata/csdgm
.. _`ISO 19115`: http://www.iso.org/iso/catalogue_detail.htm?csnumber=26020
.. _`ISO 19139`: http://www.iso.org/iso/catalogue_detail.htm?csnumber=32557
.. _`Dublin Core`: http://www.dublincore.org/
.. _`freenode`: http://freenode.net/
.. _`ohloh`: http://www.ohloh.net/p/OWSLib
.. _`CIA.vc`: http://cia.vc/stats/project/OWSLib
.. _`WaterML`: http://his.cuahsi.org/wofws.html#waterml
.. _`Swiss GM03`: http://www.geocat.ch/internet/geocat/en/home/documentation/gm03.html
