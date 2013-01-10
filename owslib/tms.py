# -*- coding: UTF-8 -*-
# =============================================================================
# Copyright (C) 2013 Christian Ledermann <christian.ledermann@gmail.com>
#
# Based on wms.py, which has the following copyright statement:
# Copyright (c) 2004, 2006 Sean C. Gillies
# Copyright (c) 2005 Nuxeo SARL <http://nuxeo.com>
#
# Authors : Sean Gillies <sgillies@frii.com>
#           Julien Anguenot <ja@nuxeo.com>
#
# Contact email: sgillies@frii.com
# =============================================================================

# TMS as defined in:
# http://wiki.osgeo.org/wiki/Tile_Map_Service_Specification

from etree import etree
from .util import openURL, testXMLValue


def force900913(epsg):
# http://osgeo-org.1560.n6.nabble.com/OSGEO-code-td3852851.html
# "EPSG:900913" = ["OSGEO:41001", "EPSG:3785", "EPSG:3857", "EPSG:54004"]
    if epsg.upper() in ["OSGEO:41001", "EPSG:3785", "EPSG:3857", "EPSG:54004"]:
        return "EPSG:900913"
    else:
        return epsg


class ServiceException(Exception):
    pass

class TileMapService(object):
    """Abstraction for OGC Tile Map Service (TMS).

    Implements IWebMapService.
    """

    def __init__(self, url, version='1.0.0', xml=None,
                username=None, password=None, parse_remote_metadata=False
                ):
        """Initialize."""
        self.url = url
        self.username = username
        self.password = password
        self.version = version
        self.services = None
        self._capabilities = None

        # Authentication handled by Reader
        reader = TMSCapabilitiesReader(
                self.version, url=self.url, un=self.username, pw=self.password
                )
        if xml:  # read from stored xml
            self._capabilities = reader.readString(xml)
        else:  # read from server
            self._capabilities = reader.read(self.url)

        # build metadata objects
        self._buildMetadata(parse_remote_metadata)


    def _getcapproperty(self):
        if not self._capabilities:
            reader = TMSCapabilitiesReader(
                self.version, url=self.url, un=self.username, pw=self.password
                )
            self._capabilities = ServiceMetadata(reader.read(self.url))
        return self._capabilities


    def _buildMetadata(self, parse_remote_metadata=False):
        ''' set up capabilities metadata objects '''
        if self._capabilities.attrib.get('version'):
            self.version = self._capabilities.attrib.get('version')
        self.identification=ServiceIdentification(self._capabilities, self.version)

        self.contents={}
        tilemaps = self._capabilities.find('TileMaps')
        if tilemaps is not None:
            for tilemap in tilemaps.findall('TileMap'):
                cm = ContentMetadata(tilemap, un=self.username, pw=self.password)
                if cm.id:
                    if cm.id in self.contents:
                        raise KeyError('Content metadata for layer "%s" already exists' % cm.id)
                    self.contents[cm.id] = cm

    def getServiceXML(self):
        xml = None
        if self._capabilities is not None:
            xml = etree.tostring(self._capabilities)
        return xml

class ServiceIdentification(object):

    def __init__(self, infoset, version):
        self._root=infoset
        if self._root.tag != 'TileMapService':
            raise ServiceException
        self.version = version
        self.title = testXMLValue(self._root.find('Title'))
        self.abstract = testXMLValue(self._root.find('Abstract'))
        self.keywords = []
        f = self._root.find('KeywordList')
        if f is not None:
            self.keywords = f.text.split()
        self.url = self._root.attrib.get('services')


class ContentMetadata(object):
    """
    Abstraction for TMS layer metadata.
    """
    def __str__(self):
        return 'Layer Title: %s, URL: %s' % (self.title, self.id)

    def __init__(self, elem, un=None, pw=None):
        if elem.tag != 'TileMap':
            raise ValueError('%s should be a TileMap' % (elem,))
        self.id = elem.attrib['href']
        self.title = elem.attrib['title']
        self.srs = force900913(elem.attrib['srs'])
        self.profile = elem.attrib['profile']
        self.password = pw
        self.username = pw
        self._tile_map = None
        self._tm_elem = None

    def _get_tilemap(self):
        if self._tile_map is None:
            u = openURL(self.id, '', method='Get', username = self.username, password = self.password)
            elem = etree.fromstring(u.read())
            self._tm_elem = elem
            if elem.tag != 'TileMap':
                raise ValueError('%s should be a TileMap' % (elem,))
            self._tile_map ={}
            self._tile_map['title'] = testXMLValue(elem.find('Title'))
            self._tile_map['abstract'] = testXMLValue(elem.find('Abstract'))
            self._tile_map['srs'] = force900913(testXMLValue(elem.find('SRS')))
            assert(self._tile_map['srs'] == self.srs)
            bbox = elem.find('BoundingBox')
            self._tile_map['boundingBox'] = (bbox.attrib['minx'],
                                            bbox.attrib['miny'],
                                            bbox.attrib['maxx'],
                                            bbox.attrib['maxy'])
            origin = elem.find('Origin')
            self._tile_map['origin'] = (origin.attrib['x'], origin.attrib['y'])
            tf = elem.find('TileFormat')
            self._tile_map['width'] = tf.attrib['width']
            self._tile_map['height'] = tf.attrib['height']
            self._tile_map['mime-type'] = tf.attrib['mime-type']
            self._tile_map['extension'] = tf.attrib['extension']
        return self._tile_map


    @property
    def abstract(self):
        return self._get_tilemap()['abstract']

    @property
    def width(self):
        return self._get_tilemap()['width']

    @property
    def height(self):
        return self._get_tilemap()['height']

    @property
    def mimetype(self):
        return self._get_tilemap()['mime-type']

    @property
    def extension(self):
        return self._get_tilemap()['extension']

    @property
    def boundingBox(self):
        return self._get_tilemap()['boundingBox']

    @property
    def origin(self):
        return self._get_tilemap()['origin']




class TMSCapabilitiesReader(object):
    """Read and parse capabilities document into a lxml.etree infoset
    """

    def __init__(self, version='1.0.0', url=None, un=None, pw=None):
        """Initialize"""
        self.version = version
        self._infoset = None
        self.url = url
        self.username = un
        self.password = pw


    def read(self, service_url):
        """Get and parse a TMS capabilities document, returning an
        elementtree instance
        """
        u = openURL(service_url, '', method='Get', username = self.username, password = self.password)
        return etree.fromstring(u.read())

    def readString(self, st):
        """Parse a TMS capabilities document, returning an elementtree instance

        string should be an XML capabilities document
        """
        if not isinstance(st, str):
            raise ValueError("String must be of type string, not %s" % type(st))
        return etree.fromstring(st)
