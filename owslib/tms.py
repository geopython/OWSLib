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

from etree import etree
from .util import openURL, testXMLValue


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

    def _buildMetadata(self, parse_remote_metadata=False):
        ''' set up capabilities metadata objects '''
        if self._capabilities.attrib.get('version'):
            self.version = self._capabilities.attrib.get('version')
        self.identification=ServiceIdentification(self._capabilities, self.version)

        #import ipdb; ipdb.set_trace()

    def getServiceXML(self):
        xml = None
        if self._capabilities is not None:
            xml = etree.tostring(self._capabilities)
        return xml

class ServiceIdentification(object):
    ''' Implements IServiceIdentificationMetadata '''

    def __init__(self, infoset, version):
        self._root=infoset
        self.version = version
        self.title = testXMLValue(self._root.find('Title'))
        self.abstract = testXMLValue(self._root.find('Abstract'))
        self.keywords = []
        f = self._root.find('KeywordList')
        if f:
            self.keywords = f.text.split()
        self.url = self._root.attrib.get('services')


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
