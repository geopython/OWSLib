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
from owslib.util import openURL, testXMLValue, nspath, extract_xml_list
from owslib.etree import etree
from owslib.fgdc import Metadata
from owslib.iso import MD_Metadata
from owslib.crs import Crs
from owslib.namespaces import OWSLibNamespaces

ns = OWSLibNamespaces()

def wfs_ns(item):
    return nspath(item,ns.get_namespace('wfs'))

class ServiceException(Exception):
    pass

class WebFeatureService_1_0_0(object):
    """Abstraction for OGC Web Feature Service (WFS).

    Implements IWebFeatureService.
    """
    def __new__(self,url, version, xml, parse_remote_metadata=False):
        """ overridden __new__ method 
        
        @type url: string
        @param url: url of WFS capabilities document
        @type xml: string
        @param xml: elementtree object
        @type parse_remote_metadata: boolean
        @param parse_remote_metadata: whether to fully process MetadataURL elements
        @return: initialized WebFeatureService_1_0_0 object
        """
        obj=object.__new__(self)
        obj.__init__(url, version, xml, parse_remote_metadata)
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
    
    
    def __init__(self, url, version, xml=None, parse_remote_metadata=False):
        """Initialize."""
        self.url = url
        self.version = version
        self._capabilities = None
        reader = WFSCapabilitiesReader(self.version)
        if xml:
            self._capabilities = reader.read_string(xml)
        else:
            self._capabilities = reader.read(self.url)
        self._build_metadata(parse_remote_metadata)
    
    def _build_metadata(self, parse_remote_metadata=False):
        '''set up capabilities metadata objects: '''
        
        #serviceIdentification metadata
        serviceelem=self._capabilities.find(wfs_ns('Service'))
        self.identification=ServiceIdentification(serviceelem, self.version)  
    
        #serviceProvider metadata
        self.provider=ServiceProvider(serviceelem)   
        
        #serviceOperations metadata 
        self.operations=[]
        for elem in self._capabilities.find(wfs_ns('Capability/Request'))[:]:
            self.operations.append(OperationMetadata(elem))
                   
        #serviceContents metadata: our assumption is that services use a top-level 
        #layer as a metadata organizer, nothing more. 
        
        self.contents={} 
        featuretypelist=self._capabilities.find(wfs_ns('FeatureTypeList'))
        features = self._capabilities.findall(wfs_ns('FeatureTypeList/FeatureType'))
        for feature in features:
            cm=ContentMetadata(feature, featuretypelist, parse_remote_metadata)
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
        base_url = self.get_operation_by_name('{http://www.opengis.net/wfs}GetFeature').methods[method]['url']
        request = {'service': 'WFS', 'version': self.version, 'request': 'GetFeature'}
        
        # check featureid
        if featureid:
            request['featureid'] = ','.join(featureid)
        elif bbox and typename:
            request['bbox'] = ','.join([repr(x) for x in bbox])
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
        u = openURL(base_url, data, method)
        
        
        # check for service exceptions, rewrap, and return
        # We're going to assume that anything with a content-length > 32k
        # is data. We'll check anything smaller.
        try:
            length = int(u.info()['Content-Length'])
            have_read = False
        except (KeyError, AttributeError):
            data = u.read()
            have_read = True
            length = len(data)
     
        if length < 32000:
            if not have_read:
                data = u.read()
            tree = etree.fromstring(data)
            if tree.tag == "{%s}ServiceExceptionReport" % ns.get_namespace('ogc'):
                se = tree.find(nspath('ServiceException', ns.get_namespace('ogc')))
                raise ServiceException, str(se.text).strip()

            return StringIO(data)
        else:
            if have_read:
                return StringIO(data)
            return u

    def get_operation_by_name(self, name):
        """Return a named operation item."""
        for item in self.operations:
            if item.name == name:
                return item
        raise KeyError, "No operation named %s" % name

class ServiceIdentification(object):
    ''' Implements IServiceIdentificationMetadata '''
    def __init__(self, infoset, version):
        self._root=infoset
        self.type = testXMLValue(self._root.find(wfs_ns('Name')))
        self.version = version
        self.title = testXMLValue(self._root.find(wfs_ns('Title')))
        self.abstract = testXMLValue(self._root.find(wfs_ns('Abstract')))
        self.keywords = extract_xml_list(self._root.findall(wfs_ns('Keywords')))
        self.fees = testXMLValue(self._root.find(wfs_ns('Fees')))
        self.accessconstraints = testXMLValue(self._root.find(wfs_ns('AccessConstraints')))

class ServiceProvider(object):
    ''' Implements IServiceProviderMetatdata '''
    def __init__(self, infoset):
        self._root=infoset
        self.url = testXMLValue(self._root.find(wfs_ns('OnlineResource')))

class ContentMetadata:
    """Abstraction for WFS metadata.
    
    Implements IMetadata.
    """

    def __init__(self, elem, parent, parse_remote_metadata=False):
        """."""
        self.id = testXMLValue(elem.find(wfs_ns('Name')))
        self.title = testXMLValue(elem.find(wfs_ns('Title')))
        self.abstract = testXMLValue(elem.find(wfs_ns('Abstract')))
        self.keywords = extract_xml_list(elem.findall(wfs_ns('Keywords')))

        # bboxes
        self.boundingBox = None
        b = elem.find(wfs_ns('BoundingBox'))
        if b is not None:
            self.boundingBox = (float(b.attrib['minx']),float(b.attrib['miny']),
                    float(b.attrib['maxx']), float(b.attrib['maxy']),
                    b.attrib['SRS'])
        self.boundingBoxWGS84 = None
        b = elem.find(wfs_ns('LatLongBoundingBox'))
        if b is not None:
            self.boundingBoxWGS84 = (
                    float(b.attrib['minx']),float(b.attrib['miny']),
                    float(b.attrib['maxx']), float(b.attrib['maxy']),
                    )
        # crs options
        self.crsOptions = [Crs(srs.text) for srs in elem.findall(wfs_ns('SRS'))]

        # verbs
        self.verbOptions = [op.tag for op \
            in parent.findall(wfs_ns('Operations/*'))]
        self.verbOptions + [op.tag for op \
            in elem.findall(wfs_ns('Operations/*')) \
            if op.tag not in self.verbOptions]
        
        #others not used but needed for iContentMetadata harmonisation
        self.styles=None
        self.timepositions=None

        # MetadataURLs
        self.metadataUrls = []
        for m in elem.findall(wfs_ns('MetadataURL')):
            metadataUrl = {
                'type': testXMLValue(m.attrib['type'], attrib=True),
                'format': testXMLValue(m.find('Format')),
                'url': testXMLValue(m)
            }

            if metadataUrl['url'] is not None and parse_remote_metadata:  # download URL
                try:
                    content = urlopen(metadataUrl['url'])
                    doc = etree.parse(content)
                    if metadataUrl['type'] is not None:
                        if metadataUrl['type'] == 'FGDC':
                            metadataUrl['metadata'] = Metadata(doc)
                        if metadataUrl['type'] == 'TC211':
                            metadataUrl['metadata'] = MD_Metadata(doc)
                except Exception, err:
                    metadataUrl['metadata'] = None

            self.metadataUrls.append(metadataUrl)

class OperationMetadata:
    """Abstraction for WFS metadata.
    
    Implements IMetadata.
    """
    def __init__(self, elem):
        """."""
        self.name = elem.tag
        # formatOptions
        self.formatOptions = [f.tag for f in elem.findall(wfs_ns('ResultFormat/*'))]
        methods = []
        for verb in elem.findall(wfs_ns('DCPType/HTTP/*')):
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

    def read_string(self, st):
        """Parse a WFS capabilities document, returning an
        instance of WFSCapabilitiesInfoset

        string should be an XML capabilities document
        """
        if not isinstance(st, str):
            raise ValueError("String must be of type string, not %s" % type(st))
        return etree.fromstring(st)
    
