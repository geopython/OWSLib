OWSLib
======

.. image:: https://github.com/geopython/OWSLib/workflows/build%20%E2%9A%99%EF%B8%8F/badge.svg
   :target: https://github.com/geopython/OWSLib/actions
   :alt: Build Status

.. image:: https://api.codacy.com/project/badge/Grade/09f15588c99943e3976cdf20b7b32c8d
   :target: https://www.codacy.com/project/cehbrecht/OWSLib/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=geopython/OWSLib&amp;utm_campaign=Badge_Grade_Dashboard
   :alt: Codacy Check

.. image:: https://img.shields.io/github/license/geopython/OWSLib.svg
    :target: https://github.com/geopython/OWSLib/blob/master/LICENSE
    :alt: GitHub license

.. image:: https://badges.gitter.im/geopython/OWSLib.svg
    :target: https://gitter.im/geopython/OWSLib?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
    :alt: Join the chat at https://gitter.im/geopython/OWSLib

OWSLib is a Python package for client programming with Open Geospatial
Consortium (OGC) web service (hence OWS) interface standards, and their
related content models.

Full documentation is available at http://geopython.github.io/OWSLib

OWSLib provides a common API for accessing service metadata and wrappers for
numerous OGC Web Service interfaces.

Dependencies
------------

OWSLib requires elementtree (standard in 2.5 as xml.etree) or lxml.

Installation
------------

See http://geopython.github.io/OWSLib/#installation

Usage
-----

Find out what a WMS has to offer. Service metadata::

    >>> from owslib.wms import WebMapService
    >>> wms = WebMapService('http://wms.jpl.nasa.gov/wms.cgi', version='1.1.1')
    >>> wms.identification.type
    'OGC:WMS'
    >>> wms.identification.version
    '1.1.1'
    >>> wms.identification.title
    'JPL Global Imagery Service'
    >>> wms.identification.abstract
    'WMS Server maintained by JPL, worldwide satellite imagery.'

Available layers::

    >>> list(wms.contents)
    ['us_landsat_wgs84', 'modis', 'global_mosaic_base', 'huemapped_srtm',
    'srtm_mag', 'daily_terra', 'us_ned', 'us_elevation', 'global_mosaic',
    'daily_terra_ndvi', 'daily_aqua_ndvi', 'daily_aqua_721', 'daily_planet',
    'BMNG', 'srtmplus', 'us_colordem', None, 'daily_aqua', 'worldwind_dem',
    'daily_terra_721']

Details of a layer::

    >>> wms['global_mosaic'].title
    'WMS Global Mosaic, pan sharpened'
    >>> wms['global_mosaic'].boundingBoxWGS84
    (-180.0, -60.0, 180.0, 84.0)
    >>> wms['global_mosaic'].crsOptions
    ['EPSG:4326', 'AUTO:42003']
    >>> wms['global_mosaic'].styles
    {'pseudo_bright': {'title': 'Pseudo-color image (Uses IR and Visual bands,
    542 mapping), gamma 1.5'}, 'pseudo': {'title': '(default) Pseudo-color
    image, pan sharpened (Uses IR and Visual bands, 542 mapping), gamma 1.5'},
    'visual': {'title': 'Real-color image, pan sharpened (Uses the visual
    bands, 321 mapping), gamma 1.5'}, 'pseudo_low': {'title': 'Pseudo-color
    image, pan sharpened (Uses IR and Visual bands, 542 mapping)'},
    'visual_low': {'title': 'Real-color image, pan sharpened (Uses the visual
    bands, 321 mapping)'}, 'visual_bright': {'title': 'Real-color image (Uses
    the visual bands, 321 mapping), gamma 1.5'}}

Available methods, their URLs, and available formats::

    >>> [op.name for op in wms.operations]
    ['GetTileService', 'GetCapabilities', 'GetMap']
    >>> wms.getOperationByName('GetMap').methods
    {'Get': {'url': 'http://wms.jpl.nasa.gov/wms.cgi?'}}
    >>> wms.getOperationByName('GetMap').formatOptions
    ['image/jpeg', 'image/png', 'image/geotiff', 'image/tiff']

That's everything needed to make a request for imagery::

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

A very similar API exists for WebFeatureService. See
tests/wfs_MapServerWFSCapabilities.txt for details.

There is also support for Web Coverage Service (WCS), Catalogue
Service for the Web (CSW), Web Processing Service (WPS), and Web
Map Tile Service (WMTS). Some of those are beta quality.


Logging
-------
OWSLib logs messages to the 'owslib' named python logger. You may
configure your application to use the log messages like so:

    >>> import logging
    >>> owslib_log = logging.getLogger('owslib')
    >>> # Add formatting and handlers as needed, for example to log to the console
    >>> ch = logging.StreamHandler()
    >>> ch.setLevel(logging.DEBUG)
    >>> ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    >>> # add the handler to the logger
    >>> owslib_log.addHandler(ch)
    >>> owslib_log.setLevel(logging.DEBUG)

Releasing
---------

.. code-block:: bash

  # update version
  vi VERSION.txt
  vi owslib/__init__.py
  git commit -m 'update release version' VERSION.txt owslib/__init__.py
  # push changes
  git push origin master
  git tag -a x.y.z -m 'tagging OWSLib release x.y.z'
  # push tag
  git push --tags
  # update live docs
  cd docs
  make html
  ./publish.sh
  # update on PyPI (must be a maintainer)
  python setup.py sdist bdist_wheel --universal
  twine upload dist/*

Support
-------

http://lists.osgeo.org/mailman/listinfo/owslib-users
http://lists.osgeo.org/mailman/listinfo/owslib-devel
