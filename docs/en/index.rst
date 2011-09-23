=======================================================
OWSLib |release| documentation
=======================================================

.. toctree::
   :maxdepth: 2

.. image:: http://www.ohloh.net/p/owslib/widgets/project_partner_badge.gif
   :width: 193px
   :height: 33px
   :alt: OWSLib
   :target: http://www.ohloh.net/p/owslib?ref=WidgetProjectPartnerBadge

:Author: Tom Kralidis
:Contact: tomkralidis at hotmail.com
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

+-------------------+-------------------+
| Standard          | Version(s)        |
+===================+===================+
| `OGC WMS`_        | 1.1.1             |
+-------------------+-------------------+
| `OGC WFS`_        | 1.0.0, 2.0.0      |
+-------------------+-------------------+
| `OGC WCS`_        | 1.0.0, 1.1.0      |
+-------------------+-------------------+
| `OGC WMC`_        | 1.1.0             |
+-------------------+-------------------+
| `OGC SOS`_        | 1.0.0             |
+-------------------+-------------------+
| `OGC CSW`_        | 2.0.2             |
+-------------------+-------------------+
| `OGC Filter`_     | 1.1.0             |
+-------------------+-------------------+
| `OGC OWS Common`_ | 1.0.0, 1.1.0, 2.0 |
+-------------------+-------------------+
| `NASA DIF`_       | 9.7               |
+-------------------+-------------------+
| `FGDC CSDGM`_     | 1998              |
+-------------------+-------------------+
| `ISO 19139`_      | 2007              |
+-------------------+-------------------+
| `Dublin Core`_    | 1.1               |
+-------------------+-------------------+

Installation
============

Requirements
------------

OWSLib requires a Python interpreter, as well as `ElementTree <http://effbot.org/zone/element-index.htm>`_ or `lxml <http://codespeak.net/lxml>`_ for XML parsing.

Install
-------

PyPI:

.. code-block:: bash

  $ easy_install OWSLib

Subversion:

.. code-block:: bash

  $ svn co https://owslib.svn.sourceforge.net/svnroot/owslib/trunk/

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

  >>> csw.getrecords(keywords=['birds'], maxrecords=20)
  >>> csw.results    
  {'matches': 101, 'nextrecord': 21, 'returned': 20}
  >>> for rec in csw.records:
  ...     print csw.records[rec].title    
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

  >>> csw.getrecords(keywords=['birds'],bbox=[-141,42,-52,84])
  >>> csw.results
  {'matches': 3, 'nextrecord': 0, 'returned': 3}
  >>> 

Search for 'birds' or 'fowl'

.. code-block:: python

  >>> csw.getrecords(keywords=['birds', 'fowl'])
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

  >>> csw.transaction(ttype='insert', typename='gmd:MD_Metadata', record=open(file.xml).read())

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

SOS
---

ISO
---

.. code-block:: python

  >>> from owslib.iso import *
  >>> m=MD_Metadata(etree.parse('tests/data/9250AA67-F3AC-6C12-0CB9-0662231AA181_iso.xml')
  >>> m.identification.topiccategory
  'farming'
  >>> 

ISO Codelists:

.. include:: ../../tests/iso_codelist.txt

Dublin Core
-----------

NASA DIF
--------

FGDC
----

Development
===========

The OWSLib wiki is located at https://sourceforge.net/apps/trac/owslib.

The OWSLib source code is available at https://owslib.svn.sourceforge.net/svnroot/owslib/trunk/.  You can browse the source code at https://sourceforge.net/apps/trac/owslib/browser.

You can find out about software metrics at the OWSLib ohloh page at http://www.ohloh.net/p/OWSLib.

Testing
-------

Support
=======

OWSLib shares a wiki and email list with the Python Cartographic Library Community.

The Community is the primary means for OWSLib users and developers to exchange application ideas, discuss potential software improvements, and ask questions.

Subscribing to Community
------------------------

To subscribe to the Community listserv visit https://lists.sourceforge.net/mailman/listinfo/owslib-devel. You can later change your subscription information or leave the list at this website.

Submitting Questions to Community
---------------------------------

To submit questions to the Community listserv, first join the list by following the subscription procedure above. Then post questions to the list by sending an email message to owslib-devel@lists.sourceforge.net.

Searching the Archives
----------------------

All Community archives are located in https://sourceforge.net/mailarchive/forum.php?forum_name=owslib-devel.

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

 * Sean Gillies <sgillies@frii.com>
 * Julien Anguenot <ja@nuxeo.com>
 * Kai Lautaportti <kai.lautaportti@hexagonit.fi>
 * Dominic Lowe <D.Lowe@rl.ac.uk>
 * Jo Walsh <jo@frot.org>
 * Tom Kralidis <tomkralidis@hotmail.com>

.. _`Open Geospatial Consortium`: http://www.opengeospatial.org/
.. _`OGC WMS`: http://www.opengeospatial.org/standards/wms
.. _`OGC WFS`: http://www.opengeospatial.org/standards/wfs
.. _`OGC WCS`: http://www.opengeospatial.org/standards/wcs
.. _`OGC WMC`: http://www.opengeospatial.org/standards/wmc
.. _`OGC SOS`: http://www.opengeospatial.org/standards/sos
.. _`OGC CSW`: http://www.opengeospatial.org/standards/cat
.. _`OGC Filter`: http://www.opengeospatial.org/standards/filter
.. _`OGC OWS Common`: http://www.opengeospatial.org/standards/common
.. _`NASA DIF`: http://gcmd.nasa.gov/User/difguide/ 
.. _`FGDC CSDGM`: http://www.fgdc.gov/metadata/csdgm
.. _`ISO 19115`: http://www.iso.org/iso/catalogue_detail.htm?csnumber=26020
.. _`ISO 19139`: http://www.iso.org/iso/catalogue_detail.htm?csnumber=32557
.. _`Dublin Core`: http://www.dublincore.org/
