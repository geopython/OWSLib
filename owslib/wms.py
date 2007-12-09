# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2004, 2006 Sean C. Gillies
# Copyright (c) 2005 Nuxeo SARL <http://nuxeo.com>
#
# Authors : Sean Gillies <sgillies@frii.com>
#           Julien Anguenot <ja@nuxeo.com>
#
# Contact email: sgillies@frii.com
# =============================================================================

"""
API for Web Map Service (WMS) methods and metadata.

Currently supports only version 1.1.1 of the WMS protocol.
"""

import cgi
from urllib import urlencode
from urllib2 import urlopen

from etree import etree


class ServiceException(Exception):
    pass


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
        # initialize from saved capability document
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
        """Request and return capabilities document from the WMS as a 
        file-like object."""
        reader = WMSCapabilitiesReader(self.version)
        u = urlopen(reader.capabilities_url(self.url))
        # check for service exceptions, and return
        if u.info().gettype() == 'application/vnd.ogc.se_xml':
            se_xml = u.read()
            se_tree = etree.fromstring(se_xml)
            raise ServiceException, \
                str(se_tree.find('ServiceException').text).strip()
        return u

    def getmap(self, layers=None, styles=None, srs=None, bbox=None,
               format=None, size=None, transparent=False, bgcolor='#FFFFFF',
               exceptions='application/vnd.ogc.se_xml',
               method='Get'):
        """Request and return an image from the WMS as a file-like object.
        
        Parameters
        ----------
        layers : list
            List of content layer names.
        styles : list
            Optional list of named styles, must be the same length as the
            layers list.
        srs : string
            A spatial reference system identifier.
        bbox : tuple
            (left, bottom, right, top) in srs units.
        format : string
            Output image format such as 'image/jpeg'.
        size : tuple
            (width, height) in pixels.
        transparent : bool
            Optional. Transparent background if True.
        bgcolor : string
            Optional. Image background color.
        method : string
            Optional. HTTP DCP method name: Get or Post.
        
        Example
        -------
            >>> img = wms.getmap(layers=['global_mosaic'],
            ...                  styles=['visual'],
            ...                  srs='EPSG:4326', 
            ...                  bbox=(-112,36,-106,41),
            ...                  format='image/jpeg',
            ...                  size=(300,250),
            ...                  transparent=True,
            ...                  )
            >>> out = open('example.jpg', 'wb')
            >>> out.write(img.read())
            >>> out.close()

        """
        md = self.capabilities
        base_url = md.getOperationByName('GetMap').methods[method]['url']
        request = {'version': self.version, 'request': 'GetMap'}
        
        # check layers and styles
        assert len(layers) > 0
        request['layers'] = ','.join(layers)
        if styles:
            assert len(styles) == len(layers)
            request['styles'] = ','.join(styles)
        else:
            request['styles'] = ''

        # size
        request['width'] = str(size[0])
        request['height'] = str(size[1])
        
        request['srs'] = str(srs)
        request['bbox'] = ','.join([str(x) for x in bbox])
        request['format'] = str(format)
        request['transparent'] = str(transparent).upper()
        request['bgcolor'] = '0x' + bgcolor[1:7]
        request['exceptions'] = str(exceptions)
        
        data = urlencode(request)
        if method == 'Post':
            u = urlopen(base_url, data=data)
        else:
            u = urlopen(base_url + data)

        # check for service exceptions, and return
        if u.info()['Content-Type'] == 'application/vnd.ogc.se_xml':
            se_xml = u.read()
            se_tree = etree.fromstring(se_xml)
            raise ServiceException, \
                str(se_tree.find('ServiceException').text).strip()
        return u

    def getfeatureinfo(self):
        raise NotImplementedError
        
        
class ServiceMetadata(object):
    """Abstraction for WMS metadata.
    
    Implements IServiceMetadata.
    """

    def __init__(self, infoset):
        """Initialize from an element tree."""
        self._root = infoset.getroot()
        # properties
        self.service = self._root.find('Service/Name').text
        self.title = self._root.find('Service/Title').text
	abstract = self._root.find('Service/Abstract')
	if abstract is not None:
	        self.abstract = self._root.find('Service/Abstract').text
	else:
		self.abstract = None
        self.link = self._root.find('Service/OnlineResource').attrib.get('{http://www.w3.org/1999/xlink}href', '')
        
        # operations []
        self.operations = []
        for elem in self._root.findall('Capability/Request/*'):
            self.operations.append(OperationMetadata(elem))

        # exceptions
        self.exceptions = [f.text for f \
                in self._root.findall('Capability/Exception/Format')]
        
        # contents: our assumption is that services use a top-level layer
        # as a metadata organizer, nothing more.
	caps = self._root.find('Capability')
	self.layers = []
	for elem in caps.findall('Layer'):
		self.layers.append(ContentMetadata(elem))

        # keywords
        self.keywords = [f.text for f in self._root.findall('Service/KeywordList/Keyword')]
        
        # contact person
	contact = self._root.find('Service/ContactInformation')
	## sometimes there is a contact block that is empty, so make
	## sure there are children to parse
	if contact is not None and contact.getchildren():
            self.provider = ContactMetadata(contact)
        else:
            self.provider = None

    @property
    def contents(self):
	"""backwards compatible flat list of contents"""
        return list(self._rcontents(self))
    def _rcontents(self, layer):
        for l in layer.layers:
            yield l
            for l in self._rcontents(l):
                yield l
            
    def getContentByName(self, name):
        """Return a named content item."""
        for item in self.contents:
            if item.name == name:
                return item
        raise KeyError, "No content named %s" % name

    def getOperationByName(self, name):
        """Return a named content item."""
        for item in self.operations:
            if item.name == name:
                return item
        raise KeyError, "No operation named %s" % name

    #def toXML(self):
    #    """x
    #    """
    #    top = etree.Element('a')
    #    top.text = self.getName()
    #    return etree.tostring(top)


class ContentMetadata:
	"""
	Abstraction for WMS metadata.

	Implements IMetadata.
	"""
	def __init__(self, elem, parent=None):
		self.parent = parent
		if elem.tag != 'Layer':
			raise ValueError('%s should be a Layer' % (elem,))
		for key in ('Name', 'Title', 'Attribution'):
			val = elem.find(key)
			if val is not None:
				setattr(self, key.lower(), val.text.strip())
			else:
				setattr(self, key.lower(), None)

		# bboxes
		b = elem.find('BoundingBox')
		if b is not None:
			self.boundingBox = (
				float(b.attrib['minx']),
				float(b.attrib['miny']),
				float(b.attrib['maxx']),
				float(b.attrib['maxy']),
				b.attrib['SRS'],
			)
		elif self.parent:
			self.boundingBox = self.parent.boundingBox
		else:
			self.boundingBox = None

		b = elem.find('LatLonBoundingBox')
		if b is not None:
			self.boundingBoxWGS84 = (
				float(b.attrib['minx']),
				float(b.attrib['miny']),
				float(b.attrib['maxx']),
				float(b.attrib['maxy']),
			)
		elif self.parent:
			self.boundingBoxWGS84 = self.parent.boundingBoxWGS84
		else:
			self.boundingBoxWGS84 = None

		# crs options
		self.crsOptions = []
		if elem.find('SRS') is not None:
			## some servers found in the wild use a single SRS
			## tag containing a whitespace separated list of SRIDs
			## instead of several SRS tags. hence the inner loop
			for srslist in map(lambda x: x.text, elem.findall('SRS')):
				for srs in srslist.split():
					self.crsOptions.append(srs)
		elif self.parent:
			self.crsOptions = self.parent.crsOptions
		else:
			raise ValueError('%s no SRS available!?' % (elem,))

		# styles
		self.styles = {}
		for s in elem.findall('Style'):
			name = s.find('Name')
			title = s.find('Title')
			if name is None or title is None:
				raise ValueError('%s missing name or title' % (s,))
			self.styles[name.text] = { 'title' : title.text }

		self.layers = []
		for child in elem.findall('Layer'):
			self.layers.append(ContentMetadata(child, self))

	def __str__(self):
		return 'Layer Name: %s Title: %s' % (self.name, self.title)

class OperationMetadata:
    """Abstraction for WMS metadata.
    
    Implements IMetadata.
    """
    def __init__(self, elem):
        """."""
        self.name = elem.tag
        # formatOptions
        self.formatOptions = [f.text for f in elem.findall('Format')]
        methods = []
        for verb in elem.findall('DCPType/HTTP/*'):
            url = verb.find('OnlineResource').attrib['{http://www.w3.org/1999/xlink}href']
            methods.append((verb.tag, {'url': url}))
        self.methods = dict(methods)

class ContactMetadata:
	"""Abstraction for contact details advertised in GetCapabilities.
	"""
	def __init__(self, elem):
		self.name = elem.find('ContactPersonPrimary/ContactPerson').text
		self.email = elem.find('ContactElectronicMailAddress').text 

		self.address = self.city = self.region = None
		self.postcode = self.country = None

		address = elem.find('ContactAddress')
		if address is not None:
			street = address.find('Address')
			if street is not None: self.address = street.text

			city = address.find('City')
			if city is not None: self.city = city.text

			region = address.find('StateOrProvince')
			if region is not None: self.region = region.text

			postcode = address.find('PostCode')
			if postcode is not None: self.postcode = postcode.text

			country = address.find('Country')
			if country is not None: self.country = country.text

		organization = elem.find('ContactPersonPrimary/ContactOrganization')
		if organization is not None: self.organization = organization.text
		else:self.organization = None

		position = elem.find('ContactPosition')
		if position is not None: self.position = position.text
		else: self.position = None

# Deprecated classes follow
# TODO: remove

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

        urlqs = urlencode(tuple(qs))
        return service_url.split('?')[0] + '?' + urlqs

    def read(self, service_url):
        """Get and parse a WMS capabilities document, returning an
        instance of WMSCapabilitiesInfoset

        service_url is the base url, to which is appended the service,
        version, and request parameters
        """
        request = self.capabilities_url(service_url)
        u = urlopen(request)
        return WMSCapabilitiesInfoset(etree.fromstring(u.read()))

    def readString(self, st):
        """Parse a WMS capabilities document, returning an
        instance of WMSCapabilitiesInfoset

        string should be an XML capabilities document
        """
        if not isinstance(st, str):
            raise ValueError("String must be of type string, not %s" % type(st))
        return WMSCapabilitiesInfoset(etree.fromstring(st))


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



