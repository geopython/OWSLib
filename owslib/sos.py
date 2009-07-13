# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2008, Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@hotmail.com>
#
# Contact email: tomkralidis@hotmail.com
# =============================================================================

"""
API for Sensor Observation Service (SOS) methods and metadata.

Currently supports only version 1.0.0 of the SOS protocol.
"""

import cgi
from urllib import urlencode
from urllib2 import urlopen
from urllib2 import HTTPPasswordMgrWithDefaultRealm
from urllib2 import HTTPBasicAuthHandler
from urllib2 import build_opener
from urllib2 import install_opener

from etree import etree

import owslib.ows as ows
import filter

class ServiceException(Exception):
    pass


class CapabilitiesError(Exception):
    pass


class SensorObservationService(object):
    """Abstraction for OGC Sensor Observation Service (SOS).

    Implements ISensorObservationService.
    """
    
    def __getitem__(self,name):
        ''' check contents dictionary to allow dict like access to service layers'''
        if name in self.__getattribute__('contents').keys():
            return self.__getattribute__('contents')[name]
        else:
            raise KeyError, "No content named %s" % name

    
    def __init__(self, url, version='1.0.0', xml=None, 
                username=None, password=None
                ):
        """Initialize."""
        self.url = url
        self.username = username
        self.password = password
        self.version = version
        self._capabilities = None
        self._open = urlopen
        
        if self.username and self.password:
            # Provide login information in order to use the SOS server
            # Create an OpenerDirector with support for Basic HTTP 
            # Authentication...
            passman = HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, self.url, self.username, self.password)
            auth_handler = HTTPBasicAuthHandler(passman)
            opener = build_opener(auth_handler)
            self._open = opener.open
            reader = SOSCapabilitiesReader(
                self.version, url=self.url, un=self.username, pw=self.password
                )
            self._capabilities = reader.readString(self.url)
        else:
            reader = SOSCapabilitiesReader(self.version)
            if xml:
                #read from stored xml
                self._capabilities = reader.readString(xml)
            else:
                #read from non-password protected server
                self._capabilities = reader.read(self.url)
                
       
        #build metadata objects
        self._buildMetadata()

    def _getcapproperty(self):
        if not self._capabilities:
            reader = SOSCapabilitiesReader(
                self.version, url=self.url, un=self.username, pw=self.password
                )
            self._capabilities = ServiceMetadata(reader.read(self.url))
        return self._capabilities
    capabilities = property(_getcapproperty, None)

    def _buildMetadata(self):         
        ''' set up capabilities metadata objects '''
        
        # ServiceIdentification
        val = self._capabilities.find('{http://www.opengis.net/ows/1.1}ServiceIdentification')
        self.identification=ows.ServiceIdentification(val)
        # ServiceProvider
        val = self._capabilities.find('{http://www.opengis.net/ows/1.1}ServiceProvider')
        self.provider=ows.ServiceProvider(val)
            
        # ServiceOperations metadata 
        self.operations=[]
        for elem in self._capabilities.findall('{http://www.opengis.net/ows/1.1}OperationsMetadata/{http://www.opengis.net/ows/1.1}Operation'):
            self.operations.append(ows.OperationsMetadata(elem))

        # FilterCapabilities
        val = self._capabilities.find('{http://www.opengis.net/sos/1.0}Filter_Capabilities')

        self.filters=filter.Filter_Capabilities(val)
 
        #serviceContents metadata: our assumption is that services use a top-level 
        #layer as a metadata organizer, nothing more.
        self.contents={}
        caps = self._capabilities.find('Capability')
        #for elem in caps.findall('Layer'):
        #    cm=ContentMetadata(elem)
        #    self.contents[cm.id]=cm       
        #    for subelem in elem.findall('Layer'):
        #        subcm=ContentMetadata(subelem, cm)
        #        self.contents[subcm.id]=subcm 
        
        #exceptions
        self.exceptions = ['text/xml']
            
    def items(self):
        '''supports dict-like items() access'''
        items=[]
        for item in self.contents:
            items.append((item,self.contents[item]))
        return items
    
    def getcapabilities(self):
        """Request and return capabilities document from the SOS as a 
        file-like object.
        NOTE: this is effectively redundant now"""
        
        reader = SOSCapabilitiesReader(
            self.version, url=self.url, un=self.username, pw=self.password
            )
        u = self._open(reader.capabilities_url(self.url))
       # check for service exceptions, and return
        if u.info().gettype() == 'application/vnd.ogc.se_xml':
            se_xml = u.read()
            se_tree = etree.fromstring(se_xml)
            raise ServiceException, \
                str(se_tree.find('ExceptionReport').text).strip()
        return u

    def getmap(self, layers=None, styles=None, srs=None, bbox=None,
               format=None, size=None, time=None, transparent=False,
               bgcolor='#FFFFFF',
               exceptions='application/vnd.ogc.se_xml',
               method='Get'
               ):
        """Request and return an image from the SOS as a file-like object.
        
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
        base_url = self.getOperationByName('GetMap').methods[method]['url']
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
        
        if time is not None:
            request['time'] = str(time)
        
        data = urlencode(request)
        if method == 'Post':
            u = self._open(base_url, data=data)
        else:
            u = self._open(base_url + data)

        # check for service exceptions, and return
        if u.info()['Content-Type'] == 'application/vnd.ogc.se_xml':
            se_xml = u.read()
            se_tree = etree.fromstring(se_xml)
            raise ServiceException, \
                str(se_tree.find('ExceptionReport').text).strip()
        return u

    def getfeatureinfo(self):
        raise NotImplementedError
    
    def getOperationByName(self, name): 
        """Return a named content item."""
        for item in self.operations:
            if item.name == name:
                return item
        raise KeyError, "No operation named %s" % name

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

class ContentMetadata:
	"""
	Abstraction for SOS layer metadata.

	Implements IContentMetadata.
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
                self.id=self.name #conform to new interface
		# bboxes
		b = elem.find('BoundingBox')
		self.boundingBox = None
                if b is not None:
                    try: #sometimes the SRS attribute is (wrongly) not provided
                        srs=b.attrib['SRS']
                    except KeyError:
                        srs=None
                    self.boundingBox = (
                            float(b.attrib['minx']),
                            float(b.attrib['miny']),
                            float(b.attrib['maxx']),
                            float(b.attrib['maxy']),
                            srs,
                    )
		elif self.parent:
                    if hasattr(self.parent, 'boundingBox'):
			self.boundingBox = self.parent.boundingBox
                    
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
                            if srslist:
				for srs in srslist.split():
					self.crsOptions.append(srs)
		elif self.parent:
                        self.crsOptions = self.parent.crsOptions
		else:
			#raise ValueError('%s no SRS available!?' % (elem,))
                        #Comment by D Lowe.
                        #Do not raise ValueError as it is possible that a layer is purely a parent layer and does not have SRS specified. Instead set crsOptions to None
                        self.crsOptions=None
		# styles
		self.styles = {}
		for s in elem.findall('Style'):
			name = s.find('Name')
			title = s.find('Title')
			if name is None or title is None:
				raise ValueError('%s missing name or title' % (s,))
			style = { 'title' : title.text }
			# legend url
			legend = s.find('LegendURL/OnlineResource')
			if legend is not None:
				style['legend'] = legend.attrib['{http://www.w3.org/1999/xlink}href']
			self.styles[name.text] = style

		# keywords
		self.keywords = [f.text for f in elem.findall('KeywordList/Keyword')]

                # timepositions - times for which data is available.
                self.timepositions=None
                for extent in elem.findall('Extent'):
                    if extent.attrib.get("name").lower() =='time':
                        self.timepositions=extent.text.split(',')
                        break
                
		self.layers = []
		for child in elem.findall('Layer'):
			self.layers.append(ContentMetadata(child, self))

	def __str__(self):
		return 'Layer Name: %s Title: %s' % (self.name, self.title)
        
class SOSCapabilitiesReader:
    """Read and parse capabilities document into a lxml.etree infoset
    """

    def __init__(self, version='1.0.0', url=None, un=None, pw=None):
        """Initialize"""
        self.version = version
        self._infoset = None
        self.url = url
        self.username = un
        self.password = pw
        self._open = urlopen

        if self.username and self.password:
            # Provide login information in order to use the SOS server
            # Create an OpenerDirector with support for Basic HTTP 
            # Authentication...
            passman = HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, self.url, self.username, self.password)
            auth_handler = HTTPBasicAuthHandler(passman)
            opener = build_opener(auth_handler)
            self._open = opener.open

    def capabilities_url(self, service_url):
        """Return a capabilities url
        """
        qs = []
        if service_url.find('?') != -1:
            qs = cgi.parse_qsl(service_url.split('?')[1])

        params = [x[0] for x in qs]

        if 'service' not in params:
            qs.append(('service', 'SOS'))
        if 'request' not in params:
            qs.append(('request', 'GetCapabilities'))
        if 'version' not in params:
            qs.append(('version', self.version))

        urlqs = urlencode(tuple(qs))
        return service_url.split('?')[0] + '?' + urlqs

    def read(self, service_url):
        """Get and parse a SOS capabilities document, returning an
        elementtree instance

        service_url is the base url, to which is appended the service,
        version, and request parameters
        """
        request = self.capabilities_url(service_url)
        u = self._open(request)
        return etree.fromstring(u.read())

    def readString(self, st):
        """Parse a SOS capabilities document, returning an elementtree instance

        string should be an XML capabilities document
        """
        if not isinstance(st, str):
            raise ValueError("String must be of type string, not %s" % type(st))
        return etree.fromstring(st)


class SOSError(Exception):
    """Base class for SOS module errors
    """

    def __init__(self, version, language, code, locator, text):
        """Initialize an SOS Error"""
        self=ows.OWSExceptionReport("1.0.0", "en-US", "InvalidParameterValue", "request", "foo")

    def toxml(self):
        """Serialize into SOS Exception Report XML
        """
        return self.toxml() 
