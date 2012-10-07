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
API for Web Map Tile Service (WMTS) methods and metadata.

Currently borken.
"""

import cgi
import urllib2
from urllib import urlencode
from etree import etree
from .util import openURL, testXMLValue
from fgdc import Metadata
from iso import MD_Metadata

class ServiceException(Exception):
    """WMTS ServiceException

    Attributes:
        message -- short error message
        xml  -- full xml error message from server
    """

    def __init__(self, message, xml):
        self.message = message
        self.xml = xml
        
    def __str__(self):
        return repr(self.message)


class CapabilitiesError(Exception):
    pass


class WebMapTileService(object):
    """Abstraction for OGC Web Map Tile Service (WMTS).

    Implements IWebMapService.
    """
    
    def __getitem__(self,name):
        ''' check contents dictionary to allow dict like access to service layers'''
        if name in self.__getattribute__('contents').keys():
            return self.__getattribute__('contents')[name]
        else:
            raise KeyError, "No content named %s" % name

    
    def __init__(self, url, version='1.0.0', xml=None, 
                username=None, password=None, parse_remote_metadata=False
                ):
        """Initialize."""
        self.url = url
        self.username = username
        self.password = password
        self.version = version
        self._capabilities = None
        
        # Authentication handled by Reader
        reader = WMTSCapabilitiesReader(
                self.version, url=self.url, un=self.username, pw=self.password
                )
               
        if xml:  # read from stored xml
            self._capabilities = reader.readString(xml)
        else:  # read from server
            self._capabilities = reader.read(self.url)
	
        # avoid building capabilities metadata if the response is a ServiceExceptionReport
        # TODO: check if this needs a namespace
        se = self._capabilities.find('ServiceException') 
 	if se is not None: 
 	    err_message = str(se.text).strip() 
            raise ServiceException(err_message, xml) 

        # build metadata objects
        self._buildMetadata(parse_remote_metadata)

    def _getcapproperty(self):
        if not self._capabilities:
            reader = WMTSCapabilitiesReader(
                self.version, url=self.url, un=self.username, pw=self.password
                )
            self._capabilities = ServiceMetadata(reader.read(self.url))
        return self._capabilities

    def _buildMetadata(self, parse_remote_metadata=False):
        ''' set up capabilities metadata objects '''
        
        #serviceIdentification metadata
        serviceident=self._capabilities.find('{http://www.opengis.net/ows/1.1}ServiceIdentification')
        self.identification=ServiceIdentification(serviceident, self.version)   
        
        #serviceProvider metadata
        serviceprov=self._capabilities.find('{http://www.opengis.net/ows/1.1}ServiceProvider')
        self.provider=ServiceProvider(serviceprov)   
            
        #serviceOperations metadata 
        self.operations=[]
        for elem in self._capabilities.find('{http://www.opengis.net/ows/1.1}OperationsMetadata')[:]:
            self.operations.append(OperationsMetadata(elem))
          
        #serviceContents metadata: our assumption is that services use a top-level 
        #layer as a metadata organizer, nothing more.
        self.contents={}
        caps = self._capabilities.find('{http://www.opengis.net/wmts/1.0}Contents')
      
        def gather_layers(parent_elem, parent_metadata):
            for index, elem in enumerate(parent_elem.findall('{http://www.opengis.net/wmts/1.0}Layer')):
                cm = ContentMetadata(elem, parent=parent_metadata, index=index+1, parse_remote_metadata=parse_remote_metadata)
                if cm.id:
                    if cm.id in self.contents:
                        raise KeyError('Content metadata for layer "%s" already exists' % cm.id)
                    self.contents[cm.id] = cm
                gather_layers(elem, cm)
        gather_layers(caps, None)
        
        self.tilematrixset = {}
        for elem in caps.findall('{http://www.opengis.net/wmts/1.0}TileMatrixSet'):
	    tms = TileMatrixSet(elem)
            if tms.identifier:
		if tms.identifier in self.tilematrixset:
		    raise KeyError('TileMatrixSet with identifier "%s" already exists' % tms.identifier)
		self.tilematrixset[tms.identifier] = tms

    def items(self):
        '''supports dict-like items() access'''
        items=[]
        for item in self.contents:
            items.append((item,self.contents[item]))
        return items
    
    # TODO: implement this properly
    def gettile(self, layers=None, styles=None, srs=None, bbox=None,
               format=None, size=None, time=None, transparent=False,
               bgcolor='#FFFFFF',
               exceptions='application/vnd.ogc.se_xml',
               method='Get',
               **kwargs
               ):
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
        **kwargs : extra arguments
            anything else e.g. vendor specific parameters
        
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
        request['bbox'] = ','.join([repr(x) for x in bbox])
        request['format'] = str(format)
        request['transparent'] = str(transparent).upper()
        request['bgcolor'] = '0x' + bgcolor[1:7]
        request['exceptions'] = str(exceptions)
        
        if time is not None:
            request['time'] = str(time)
        
        if kwargs:
            for kw in kwargs:
                request[kw]=kwargs[kw]

        data = urlencode(request)
        
        u = openURL(base_url, data, method, username = self.username, password = self.password)

        # check for service exceptions, and return
        if u.info()['Content-Type'] == 'application/vnd.ogc.se_xml':
            se_xml = u.read()
            se_tree = etree.fromstring(se_xml)
            err_message = unicode(se_tree.find('ServiceException').text).strip()
            raise ServiceException(err_message, se_xml)
        return u
        
    def getServiceXML(self):
        xml = None
        if self._capabilities is not None:
            xml = etree.tostring(self._capabilities)
        return xml

    def getfeatureinfo(self):
        raise NotImplementedError
    
    def getOperationByName(self, name): 
        """Return a named content item."""
        for item in self.operations:
            if item.name == name:
                return item
        raise KeyError, "No operation named %s" % name
    
class ServiceIdentification(object):
    ''' Implements IServiceIdentificationMetadata '''
    
    def __init__(self, infoset, version):
        self._root=infoset
        self.type = testXMLValue(self._root.find('{http://www.opengis.net/ows/1.1}ServiceType'))
        self.version = version
        self.title = testXMLValue(self._root.find('{http://www.opengis.net/ows/1.1}Title'))
        self.abstract = testXMLValue(self._root.find('{http://www.opengis.net/ows/1.1}Abstract'))
        self.keywords = [f.text for f in self._root.findall('{http://www.opengis.net/ows/1.1}Keywords/{http://www.opengis.net/ows/1.1}Keyword')]
        self.accessconstraints = testXMLValue(self._root.find('{http://www.opengis.net/ows/1.1}AccessConstraints'))
        self.fees = testXMLValue(self._root.find('{http://www.opengis.net/ows/1.1}Fees'))

class TileMatrixSet(object):
    '''Holds one TileMatrixSet'''
    def __init__(self, elem):
        if elem.tag != '{http://www.opengis.net/wmts/1.0}TileMatrixSet':
            raise ValueError('%s should be a TileMatrixSet' % (elem,))
        self.identifier = testXMLValue(elem.find('{http://www.opengis.net/ows/1.1}Identifier')).strip()
        self.crs = testXMLValue(elem.find('{http://www.opengis.net/ows/1.1}SupportedCRS')).strip()
        if (self.crs == None) or (self.identifier == None):
	    raise ValueError('%s incomplete TileMatrixSet' % (elem,))
	self.tilematrix = {}
	for tilematrix in elem.findall('{http://www.opengis.net/wmts/1.0}TileMatrix'):
	    tm = TileMatrix(tilematrix)
            if tm.identifier:
		if tm.identifier in self.tilematrix:
		    raise KeyError('TileMatrix with identifier "%s" already exists' % tm.identifier)
		self.tilematrix[tm.identifier] = tm

class TileMatrix(object):
    '''Holds one TileMatrixSet'''
    def __init__(self, elem):
        if elem.tag != '{http://www.opengis.net/wmts/1.0}TileMatrix':
            raise ValueError('%s should be a TileMatrix' % (elem,))
        self.identifier = testXMLValue(elem.find('{http://www.opengis.net/ows/1.1}Identifier')).strip()
        sd = testXMLValue(elem.find('{http://www.opengis.net/wmts/1.0}ScaleDenominator'))
        if sd is None:
	    raise ValueError('%s is missing ScaleDenominator' % (elem,))
        self.scaledenominator = float(sd)
        tl = testXMLValue(elem.find('{http://www.opengis.net/wmts/1.0}TopLeftCorner'))
        if tl is None:
	    raise ValueError('%s is missing TopLeftCorner' % (elem,))
	(lon, lat) = tl.split(" ")
        self.topleftcorner = (float(lon), float(lat))
        width = testXMLValue(elem.find('{http://www.opengis.net/wmts/1.0}TileWidth'))
        height = testXMLValue(elem.find('{http://www.opengis.net/wmts/1.0}TileHeight'))
        if (width is None) or (height is None):
	    raise ValueError('%s is missing TileWidth and/or TileHeight' % (elem,))
        self.tilewidth = int(width)
        self.tileheight = int(height)
        mw = testXMLValue(elem.find('{http://www.opengis.net/wmts/1.0}MatrixWidth'))
        mh = testXMLValue(elem.find('{http://www.opengis.net/wmts/1.0}MatrixHeight'))
        if (mw is None) or (mh is None):
	    raise ValueError('%s is missing MatrixWidth and/or MatrixHeight' % (elem,))
	self.matrixwidth = int(mw)
	self.matrixheight = int(mh)
	# TODO: parse the rest of this
        #    <!-- top left point of tile matrix bounding box -->
        #    <TopLeftCorner>-180 90</TopLeftCorner>
        
class ServiceProvider(object):
    ''' Implements IServiceProviderMetatdata '''
    def __init__(self, infoset):
        self._root=infoset
        # TODO: fix this
        name=self._root.find('{http://www.opengis.net/ows/1.1}ProviderName')
        if name is not None:
            self.name=name.text
        else:
            self.name=None
        # print "sp:", etree.tostring(self._root, pretty_print=True, encoding=unicode)
        self.url=self._root.find('{http://www.opengis.net/ows/1.1}ProviderSite').attrib.get('{http://www.w3.org/1999/xlink}href', '')
        #contact metadata
        contact = self._root.find('{http://www.opengis.net/ows/1.1}ServiceContact')
        ## make sure there are children to parse
        if contact is not None and contact[:] != []:
            self.contact = ContactMetadata(contact)
        else:
            self.contact = None
            
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
    Abstraction for WMS layer metadata.

    Implements IContentMetadata.
    """
    def __init__(self, elem, parent=None, index=0, parse_remote_metadata=False):
        if elem.tag != '{http://www.opengis.net/wmts/1.0}Layer':
            raise ValueError('%s should be a Layer' % (elem,))
        
        self.parent = parent
        if parent:
            self.index = "%s.%d" % (parent.index, index)
        else:
            self.index = str(index)
        
        self.id = self.name = testXMLValue(elem.find('{http://www.opengis.net/ows/1.1}Identifier'))
        # title is mandatory property
        self.title = None
        title = testXMLValue(elem.find('{http://www.opengis.net/ows/1.1}Title'))
        if title is not None:
            self.title = title.strip()

        self.abstract = testXMLValue(elem.find('{http://www.opengis.net/ows/1.1}Abstract'))
        
        # bboxes
        b = elem.find('{http://www.opengis.net/ows/1.1}WGS84BoundingBox')
        self.boundingBox = None
        if b is not None:
            lc = b.find("{http://www.opengis.net/ows/1.1}LowerCorner")
            uc = b.find("{http://www.opengis.net/ows/1.1}UpperCorner")
            ll = [float(s) for s in lc.text.split()]
            ur = [float(s) for s in uc.text.split()]
            self.boundingBoxWGS84 = (ll[0],ll[1],ur[0],ur[1])
        # TODO: there is probably some more logic here, and it should probably be shared code

	self.tilematrixset = elem.find('{http://www.opengis.net/wmts/1.0}TileMatrixSetLink/{http://www.opengis.net/wmts/1.0}TileMatrixSet').text.strip()
        if self.tilematrixset is None:
                raise ValueError('%s missing TileMatrixSet' % (s,))
	    
        #Styles
        self.styles = {}
        for s in elem.findall('{http://www.opengis.net/wmts/1.0}Style'):
	    style = {}
	    isdefaulttext = s.attrib['isDefault']
	    style['isDefault'] = (isdefaulttext == "true")
            identifier = s.find('{http://www.opengis.net/ows/1.1}Identifier')
            if identifier is None:
                raise ValueError('%s missing identifier' % (s,))
            title = s.find('{http://www.opengis.net/ows/1.1}Title')
            if title is not None:
                style['title'] = title.text
	    self.styles[identifier.text] = style

        self.formats = [f.text for f in elem.findall('{http://www.opengis.net/wmts/1.0}Format')]
                
        self.layers = []
        for child in elem.findall('{http://www.opengis.net/wmts/1.0}Layer'):
            self.layers.append(ContentMetadata(child, self))

    def __str__(self):
        return 'Layer Name: %s Title: %s' % (self.name, self.title)


class OperationsMetadata:
    """Abstraction for WMTS OperationsMetadata.
    
    Implements IOperationMetadata.
    """
    def __init__(self, elem):
        """."""
        self.name = elem.attrib['name']
       	# print "om:", etree.tostring(elem, pretty_print=True, encoding=unicode)
        # formatOptions
        self.formatOptions = [f.text for f in elem.findall('{http://www.opengis.net/ows/1.1}Format')]
        methods = []
        for verb in elem.findall('{http://www.opengis.net/ows/1.1}DCP/{http://www.opengis.net/ows/1.1}HTTP'):
            url = verb.find('{http://www.opengis.net/ows/1.1}Get').attrib['{http://www.w3.org/1999/xlink}href']
            encodings = []
	    constraints = verb.findall('{http://www.opengis.net/ows/1.1}Get/{http://www.opengis.net/ows/1.1}Constraint')
	    for constraint in constraints:
		if constraint.attrib['name'] == "GetEncoding":
		    for encoding in constraint.findall('{http://www.opengis.net/ows/1.1}AllowedValues/{http://www.opengis.net/ows/1.1}Value'):
			encodings.append(encoding.text)
            methods.append(('HTTP', {'url': url, 'encodings': encodings}))
        self.methods = dict(methods)

class ContactMetadata:
    """Abstraction for contact details advertised in GetCapabilities.
    """
    def __init__(self, elem):
        name = elem.find('{http://www.opengis.net/ows/1.1}IndividualName')
        if name is not None:
            self.name=str.strip(name.text)
        else:
            self.name=None

        self.address = self.city = self.region = None
        self.postcode = self.country = self.email = None

        address = elem.find('{http://www.opengis.net/ows/1.1}ContactInfo/{http://www.opengis.net/ows/1.1}Address')
        if address is not None:
            deliverypoint = address.find('{http://www.opengis.net/ows/1.1}DeliveryPoint')
            if deliverypoint is not None: self.address = str.strip(deliverypoint.text)
            
            city = address.find('{http://www.opengis.net/ows/1.1}City')
            if city is not None: self.city = str.strip(city.text)

            region = address.find('{http://www.opengis.net/ows/1.1}AdministrativeArea')
            if region is not None: self.region = str.strip(region.text)

            postcode = address.find('{http://www.opengis.net/ows/1.1}PostalCode')
            if postcode is not None: self.postcode = str.strip(postcode.text)

            country = address.find('{http://www.opengis.net/ows/1.1}Country')
            if country is not None: self.country = str.strip(country.text)
            
	    email = address.find('{http://www.opengis.net/ows/1.1}ElectronicMailAddress')
	    if email is not None: self.email=str.strip(email.text)

        position = elem.find('{http://www.opengis.net/ows/1.1}PositionName')
        if position is not None: self.position = str.strip(position.text)
        else: self.position = None

      
class WMTSCapabilitiesReader:
    """Read and parse capabilities document into a lxml.etree infoset
    """

    def __init__(self, version='1.0.0', url=None, un=None, pw=None):
        """Initialize"""
        self.version = version
        self._infoset = None
        self.url = url
        self.username = un
        self.password = pw

    def capabilities_url(self, service_url):
        """Return a capabilities url
        """
        qs = []
        if service_url.find('?') != -1:
            qs = cgi.parse_qsl(service_url.split('?')[1])

        params = [x[0] for x in qs]

        if 'service' not in params:
            qs.append(('service', 'WMTS'))
        if 'request' not in params:
            qs.append(('request', 'GetCapabilities'))
        if 'version' not in params:
            qs.append(('version', self.version))

        urlqs = urlencode(tuple(qs))
        return service_url.split('?')[0] + '?' + urlqs

    def read(self, service_url):
        """Get and parse a WMS capabilities document, returning an
        elementtree instance

        service_url is the base url, to which is appended the service,
        version, and request parameters
        """
        getcaprequest = self.capabilities_url(service_url)

        #now split it up again to use the generic openURL function...
        spliturl=getcaprequest.split('?')
        u = openURL(spliturl[0], spliturl[1], method='Get', username = self.username, password = self.password)
        return etree.fromstring(u.read())

    def readString(self, st):
        """Parse a WMTS capabilities document, returning an elementtree instance

        string should be an XML capabilities document
        """
        if not isinstance(st, str):
            raise ValueError("String must be of type string, not %s" % type(st))
        return etree.fromstring(st)
