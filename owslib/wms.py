# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2004 Sean C. Gillies
# Copyright (c) 2005 Nuxeo SARL <http://nuxeo.com>
#
# Authors : Sean Gillies <sgillies@frii.com>
#           Julien Anguenot <ja@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA
#
# Contact email: sgillies@frii.com
# =============================================================================

import cgi
import sys
import urllib

from owslib.etree import etree

class WMSError(Exception):
    """Base class for WMS module errors
    """

    def __init__(self, message):
        """Initialize a WMS Error"""
        self.message = message

    def toxml(self):
        """Serialize into a WMS Service Exception XML
        """
        preamble = '<?xml version="1.0" ?>'
        report_elem = etree.Element('ServiceExceptionReport')
        report_elem.attrib['version'] = '1.1.1'
        # Service Exception
        exception_elem = etree.Element('ServiceException')
        exception_elem.text = self.message
        report_elem.append(exception_elem)
        return preamble + etree.tostring(report_elem)


class CapabilitiesError(Exception):
    pass


class WebMapService(object):
    """Abstraction for OGC Web Map Service (WMS).

    Implements IWebMapService.
    """
    
    def __init__(self, url, version='1.1.1', xml=None):
        """Initialize."""
        self.url = url
        self.version = version
        self._capabilities = None
        if xml:
            reader = WMSCapabilitiesReader(self.version)
            self._capabilities = ServiceMetadata(reader.readString(xml))
        
    def _getcapproperty(self):
        if not self._capabilities:
            reader = WMSCapabilitiesReader(self.version)
            self._capabilities = ServiceMetadata(reader.read(self.url))
        return self._capabilities
    capabilities = property(_getcapproperty, None)
            
    def getcapabilities(self):
        """Request and return capabilities document from the WMS."""
        raise NotImplementedError
        

class ServiceMetadata(object):
    """Abstraction for WMS metadata.
    
    Implements IServiceMetadata.
    """

    def __init__(self, infoset):
        """Initialize from an element tree."""
        self._root = infoset.getroot()
        #print >> sys.stderr, self._root
        # properties
        self.service = self._root.find('Service/Name').text
        self.title = self._root.find('Service/Title').text
        # operations []
        # contents []
        self.contents = []
        for elem in self._root.findall('Capability/Layer/Layer'):
            self.contents.append(ContentMetadata(elem))
         

    #def toXML(self):
    #    """x
    #    """
    #    top = etree.Element('a')
    #    top.text = self.getName()
    #    return etree.tostring(top)


class ContentMetadata:
    """Abstraction for WMS metadata.
    
    Implements IMetadata.
    """

    def __init__(self, element):
        """."""
        self.name = element.find('Name').text
        self.title = element.find('Title').text
        

class WMSCapabilitiesInfoset:
    """High-level container for WMS Capabilities based on lxml.etree
    """

    def __init__(self, infoset):
        """Initialize"""
        self._infoset = infoset

    def getroot(self):
        return self._infoset

    def getservice(self):
        return self._infoset.find('Service')

    def servicename(self):
        e_service = self.getservice()
        return e_service.find('Name').text

    def servicetitle(self):
        e_service = self.getservice()
        return e_service.find('Title').text

    def getmapformats(self):
        e_getmap = self._infoset.find('Capability/Request/GetMap')
        formats = ()
        for f in e_getmap.getiterator('Format'):
            formats = formats + (f.text,)
        return formats

    def layersrs(self):
        e_layer = self._infoset.find('Capability/Layer')
        srs = ()
        for s in e_layer.getiterator('SRS'):
            srs = srs + (s.text,)
        return srs

    def layernames(self):
        names = ()
        for n in self._infoset.findall('Capability/Layer/Layer/Name'):
            names = names + (n.text,)
        return names

    def layertitles(self):
        titles = ()
        for n in self._infoset.findall('Capability/Layer/Layer/Title'):
            titles = titles + (n.text,)
        return titles

    def getLayerInfo(self):
        info = {}
        for layer in self._infoset.findall('Capability/Layer/Layer'):
            if layer.findall('Title'):
                info[layer.findall('Title')[0].text] = layer.findall('Style')
        return info

    def bounds(self, name):
        """Returns the bounds of the specified layer as a tuple.

        Like (minx, miny, maxx, maxy, epsg)
        """
        top_layer = self._infoset.find('Capability/Layer')
        for layer in top_layer.findall('Layer'):
            n = layer.find('Name')
            if n.text == name:
                # First check for a BoundingBox
                b = layer.find('BoundingBox')
                if b is not None:
                    return (float(b.attrib['minx']), float(b.attrib['miny']),
                            float(b.attrib['maxx']), float(b.attrib['maxy']),
                            b.attrib['SRS'])
                else:
                    b = layer.find('LatLonBoundingBox')
                    #import pdb; pdb.set_trace()
                    if b is not None:
                        return (float(b.attrib['minx']),float(b.attrib['miny']),
                                float(b.attrib['maxx']),float(b.attrib['maxy']),
                                'EPSG:4326')
                # Look at the top level layer
                b = top_layer.find('BoundingBox')
                if b is not None:
                    return (float(b.attrib['minx']), float(b.attrib['miny']),
                            float(b.attrib['maxx']), float(b.attrib['maxy']),
                            b.attrib['SRS'])
                else:
                    b = top_layer.find('LatLonBoundingBox')
                    if b is not None:
                        return (float(b.attrib['minx']),float(b.attrib['miny']),
                                float(b.attrib['maxx']),float(b.attrib['maxy']),
                                'EPSG:4326')
        # If we haven't returned a bbox, raise an exception
        raise CapabilitiesError, "No bounding box specified for layer %s" % name
                
        
class WMSCapabilitiesReader:
    """Read and parse capabilities document into a lxml.etree infoset
    """

    def __init__(self, version='1.1.1'):
        """Initialize"""
        self.version = version
        self._infoset = None

    def capabilities_url(self, service_url):
        """Return a capabilities url
        """
        qs = []
        if service_url.find('?') != -1:
            qs = cgi.parse_qsl(service_url.split('?')[1])

        params = [x[0] for x in qs]

        if 'service' not in params:
            qs.append(('service', 'WMS'))
        if 'request' not in params:
            qs.append(('request', 'GetCapabilities'))
        if 'version' not in params:
            qs.append(('version', self.version))

        urlqs = urllib.urlencode(tuple(qs))
        return service_url.split('?')[0] + '?' + urlqs

    def read(self, service_url):
        """Get and parse a WMS capabilities document, returning an
        instance of WMSCapabilitiesInfoset

        service_url is the base url, to which is appended the service,
        version, and request parameters
        """
        request = self.capabilities_url(service_url)
        u = urllib.urlopen(request)
        return WMSCapabilitiesInfoset(etree.fromstring(u.read()))

    def readString(self, st):
        """Parse a WMS capabilities document, returning an
        instance of WMSCapabilitiesInfoset

        string should be an XML capabilities document
        """
        if not isinstance(st, str):
            raise ValueError("String must be of type string, not %s" % type(st))
        return WMSCapabilitiesInfoset(etree.fromstring(st))
    
