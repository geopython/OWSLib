# =============================================================================
# OWSLib. Copyright (C) 2005 Sean C. Gillies
#
# Contact email: sgillies@frii.com
#
# $Id: wfs.py 503 2006-02-01 17:09:12Z dokai $
# =============================================================================

import cgi
from cStringIO import StringIO
from urllib import urlencode
from urllib2 import urlopen
import logging

from owslib.etree import etree

WFS_NAMESPACE = 'http://www.opengis.net/wfs'
OGC_NAMESPACE = 'http://www.opengis.net/ogc'


#TODO: use nspath in util.py
def nspath(path, ns=WFS_NAMESPACE):
    """
    Prefix the given path with the given namespace identifier.
    
    Parameters
    ----------
    path : string
        ElementTree API Compatible path expression

    ns : string
        The XML namespace. Defaults to WFS namespace.
    """
    components = []
    for component in path.split("/"):
        if component != '*':
            component = "{%s}%s" % (ns, component)
        components.append(component)
    return "/".join(components)


class ServiceException(Exception):
    pass


class WebFeatureService_1_0_0(object):
    """Abstraction for OGC Web Feature Service (WFS).

    Implements IWebFeatureService.
    """
    def __new__(self,url, version, xml):
        """ overridden __new__ method 
        
        @type url: string
        @param url: url of WFS capabilities document
        @type xml: string
        @param xml: elementtree object
        @return: initialized WebFeatureService_1_0_0 object
        """
        obj=object.__new__(self)
        obj.__init__(url, version, xml)
        self.log = logging.getLogger()
        consoleh  = logging.StreamHandler()
        self.log.addHandler(consoleh)    
        return obj
    
    def __getitem__(self,name):
        ''' check contents dictionary to allow dict like access to service layers'''
        if name in self.__getattribute__('contents').keys():
            return self.__getattribute__('contents')[name]
        else:
            raise KeyError, "No content named %s" % name
    
    
    def __init__(self, url, version, xml=None):
        """Initialize."""
        self.url = url
        self.version = version
        self._capabilities = None
        reader = WFSCapabilitiesReader(self.version)
        if xml:
            self._capabilities = reader.readString(xml)
        else:
            self._capabilities = reader.read(self.url)
        self._buildMetadata()
    
    def _buildMetadata(self):
        '''set up capabilities metadata objects: '''
        
        #serviceIdentification metadata
        serviceelem=self._capabilities.find(nspath('Service'))
        self.identification=ServiceIdentification(serviceelem, self.version)  
    
        #serviceProvider metadata
        self.provider=ServiceProvider(serviceelem)   
        
        #serviceOperations metadata 
        self.operations=[]
        for elem in self._capabilities.find(nspath('Capability/Request'))[:]:
            self.operations.append(OperationMetadata(elem))
                   
        #serviceContents metadata: our assumption is that services use a top-level 
        #layer as a metadata organizer, nothing more. 
        
        self.contents={} 
        featuretypelist=self._capabilities.find(nspath('FeatureTypeList'))
        features = self._capabilities.findall(nspath('FeatureTypeList/FeatureType'))
        for feature in features:
            cm=ContentMetadata(feature, featuretypelist)
            self.contents[cm.id]=cm       
        
        #exceptions
        self.exceptions = [f.text for f \
                in self._capabilities.findall('Capability/Exception/Format')]
      
    def getcapabilities(self):
        """Request and return capabilities document from the WFS as a 
        file-like object.
        NOTE: this is effectively redundant now"""
        reader = WFSCapabilitiesReader(self.version)
        return urlopen(reader.capabilities_url(self.url))
    
    def items(self):
        '''supports dict-like items() access'''
        items=[]
        for item in self.contents:
            items.append((item,self.contents[item]))
        return items
    
    def getfeature(self, typename=None, filter=None, bbox=None, featureid=None,
                   featureversion=None, propertyname=['*'], maxfeatures=None,
                   srsname=None, method='{http://www.opengis.net/wfs}Get'):
        """Request and return feature data as a file-like object.
        
        Parameters
        ----------
        typename : list
            List of typenames (string)
        filter : string 
            XML-encoded OGC filter expression.
        bbox : tuple
            (left, bottom, right, top) in the feature type's coordinates.
        featureid : list
            List of unique feature ids (string)
        featureversion : string
            Default is most recent feature version.
        propertyname : list
            List of feature property names. '*' matches all.
        maxfeatures : int
            Maximum number of features to be returned.
        method : string
            Qualified name of the HTTP DCP method to use.
        srsname: string
            EPSG code to request the data in
            
        There are 3 different modes of use

        1) typename and bbox (simple spatial query)
        2) typename and filter (more expressive)
        3) featureid (direct access to known features)
        """
        base_url = self.getOperationByName('{http://www.opengis.net/wfs}GetFeature').methods[method]['url']
        request = {'service': 'WFS', 'version': self.version, 'request': 'GetFeature'}
        
        # check featureid
        if featureid:
            request['featureid'] = ','.join(featureid)
        elif bbox and typename:
            request['bbox'] = ','.join([str(x) for x in bbox])
        elif filter and typename:
            request['filter'] = str(filter)
        
        if srsname:
            request['srsname'] = str(srsname)
            
        assert len(typename) > 0
        request['typename'] = ','.join(typename)
        
        request['propertyname'] = ','.join(propertyname)
        if featureversion: request['featureversion'] = str(featureversion)
        if maxfeatures: request['maxfeatures'] = str(maxfeatures)

        data = urlencode(request)

        if method == 'Post':
            u = urlopen(base_url, data=data)
        else:
            u = urlopen(base_url + data)
        
        # check for service exceptions, rewrap, and return
        # We're going to assume that anything with a content-length > 32k
        # is data. We'll check anything smaller.
        try:
            length = int(u.info()['Content-Length'])
            have_read = False
        except KeyError:
            data = u.read()
            have_read = True
            length = len(data)
     
        if length < 32000:
            if not have_read:
                data = u.read()
            tree = etree.fromstring(data)
            if tree.tag == "{%s}ServiceExceptionReport" % OGC_NAMESPACE:
                se = tree.find(nspath('ServiceException', OGC_NAMESPACE))
                raise ServiceException, str(se.text).strip()

            return StringIO(data)
        else:
            if have_read:
                return StringIO(data)
            return u

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
        self.type = self._root.find(nspath('Name')).text
        self.version = version
        self.title = self._root.find(nspath('Title')).text
        abstract = self._root.find(nspath('Abstract'))
        if abstract is not None:
            self.abstract = abstract.text
        else:
            self.abstract = None
        self.keywords = [f.text for f in self._root.findall(nspath('Keywords'))]
        accessconstraints=self._root.find(nspath('AccessConstraints'))
        if accessconstraints is not None:
            self.accessconstraints = accessconstraints.text
        else:
            accessconstraints=None
        fees = self._root.find(nspath('Fees'))
        if fees is not None:
            self.fees = fees.text
             
class ServiceProvider(object):
    ''' Implements IServiceProviderMetatdata '''
    def __init__(self, infoset):
        self._root=infoset
        name=self._root.find(nspath('ContactInformation/ContactPersonPrimary/ContactOrganization'))
        if name is not None:
            self.name=name.text
        else:
            self.name=None
        self.url=self._root.find(nspath('OnlineResource')).attrib.get('{http://www.w3.org/1999/xlink}href', '')
        if self.url == '':
            self.url=self._root.find(nspath('OnlineResource')).text
        #contact metadata
        contact = self._root.find('ContactInformation')
        ## sometimes there is a contact block that is empty, so make
        ## sure there are children to parse
        if contact is not None and contact.getchildren():
            self.contact = ContactMetadata(contact)
        else:
            self.contact = None

class ContactMetadata:
    """Abstraction for contact details advertised in GetCapabilities.
    Not fully tested due to lack of Contact info in test capabilities doc.
    """
    def __init__(self, elem):
        name = elem.find(nspath('ContactPersonPrimary/ContactPerson'))
        if name is not None:
            self.name=name.text
        else:
            self.name=None
        email = elem.find(nspath('ContactElectronicMailAddress'))
        if email is not None:
            self.email=email.text
        else:
            self.email=None

        self.address = self.city = self.region = None
        self.postcode = self.country = None

        address = elem.find(nspath('ContactAddress'))
        if address is not None:
            street = address.find(nspath('Address'))
            if street is not None: self.address = street.text

            city = address.find(nspath('City'))
            if city is not None: self.city = city.text

            region = address.find(nspath('StateOrProvince'))
            if region is not None: self.region = region.text

            postcode = address.find(nspath('PostCode'))
            if postcode is not None: self.postcode = postcode.text

            country = address.find(nspath('Country'))
            if country is not None: self.country = country.text

        organization = elem.find(nspath('ContactPersonPrimary/ContactOrganization'))
        if organization is not None: self.organization = organization.text
        else:self.organization = None

        position = elem.find(nspath('ContactPosition'))
        if position is not None: self.position = position.text
        else: self.position = None


class ContentMetadata:
    """Abstraction for WFS metadata.
    
    Implements IMetadata.
    """

    def __init__(self, elem, parent):
        """."""
        self.id = elem.find(nspath('Name')).text
        self.title = elem.find(nspath('Title')).text
        # bboxes
        self.boundingBox = None
        b = elem.find(nspath('BoundingBox'))
        if b is not None:
            self.boundingBox = (float(b.attrib['minx']),float(b.attrib['miny']),
                    float(b.attrib['maxx']), float(b.attrib['maxy']),
                    b.attrib['SRS'])
        self.boundingBoxWGS84 = None
        b = elem.find(nspath('LatLongBoundingBox'))
        if b is not None:
            self.boundingBoxWGS84 = (
                    float(b.attrib['minx']),float(b.attrib['miny']),
                    float(b.attrib['maxx']), float(b.attrib['maxy']),
                    )
        # crs options
        self.crsOptions = [srs.text for srs in elem.findall(nspath('SRS'))]

        # verbs
        self.verbOptions = [op.tag for op \
            in parent.findall(nspath('Operations/*'))]
        self.verbOptions + [op.tag for op \
            in elem.findall(nspath('Operations/*')) \
            if op.tag not in self.verbOptions]
        
        #others not used but needed for iContentMetadata harmonisation
        self.styles=None
        self.timepositions=None

class OperationMetadata:
    """Abstraction for WFS metadata.
    
    Implements IMetadata.
    """
    def __init__(self, elem):
        """."""
        self.name = elem.tag
        # formatOptions
        self.formatOptions = [f.tag for f in elem.findall(nspath('ResultFormat/*'))]
        methods = []
        for verb in elem.findall(nspath('DCPType/HTTP/*')):
            url = verb.attrib['onlineResource']
            methods.append((verb.tag, {'url': url}))
        self.methods = dict(methods)


class WFSCapabilitiesReader(object):
    """Read and parse capabilities document into a lxml.etree infoset
    """

    def __init__(self, version='1.0'):
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
            qs.append(('service', 'WFS'))
        if 'request' not in params:
            qs.append(('request', 'GetCapabilities'))
        if 'version' not in params:
            qs.append(('version', self.version))

        urlqs = urlencode(tuple(qs))
        return service_url.split('?')[0] + '?' + urlqs

    def read(self, url):
        """Get and parse a WFS capabilities document, returning an
        instance of WFSCapabilitiesInfoset

        Parameters
        ----------
        url : string
            The URL to the WFS capabilities document.
        """
        request = self.capabilities_url(url)
        u = urlopen(request)
        return etree.fromstring(u.read())

    def readString(self, st):
        """Parse a WFS capabilities document, returning an
        instance of WFSCapabilitiesInfoset

        string should be an XML capabilities document
        """
        if not isinstance(st, str):
            raise ValueError("String must be of type string, not %s" % type(st))
        return etree.fromstring(st)
    
