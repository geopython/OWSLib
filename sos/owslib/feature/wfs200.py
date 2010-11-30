# =============================================================================
# OWSLib. Copyright (C) 2005 Sean C. Gillies
#
# Contact email: sgillies@frii.com
#
# $Id: wfs.py 503 2006-02-01 17:09:12Z dokai $
# =============================================================================

#owslib imports:
from owslib.ows import ServiceIdentification, ServiceProvider, OperationsMetadata
from owslib.etree import etree
from owslib.util import nspath, testXMLValue

#other imports
import cgi
from cStringIO import StringIO
from urllib import urlencode
from urllib2 import urlopen

import logging
hdlr = logging.FileHandler('/tmp/owslibwfs.log')
log = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
log.setLevel(logging.DEBUG)

WFS_NAMESPACE = 'http://www.opengis.net/wfs/2.0'
OGC_NAMESPACE = 'http://www.opengis.net/ogc'
GML_NAMESPACE = 'http://www.opengis.net/gml'
FES_NAMESPACE = 'http://www.opengis.net/fes/2.0'



class ServiceException(Exception):
    pass


class WebFeatureService_2_0_0(object):
    """Abstraction for OGC Web Feature Service (WFS).

    Implements IWebFeatureService.
    """
    def __new__(self,url, version, xml):
        """ overridden __new__ method 
        
        @type url: string
        @param url: url of WFS capabilities document
        @type xml: string
        @param xml: elementtree object
        @return: initialized WebFeatureService_2_0_0 object
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
    
    
    def __init__(self, url,  version, xml=None):
        """Initialize."""
        log.debug('building WFS %s'%url)
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
        serviceidentelem=self._capabilities.find(nspath('ServiceIdentification'))
        self.identification=ServiceIdentification(serviceidentelem)  
        #need to add to keywords list from featuretypelist information:
        featuretypelistelem=self._capabilities.find(nspath('FeatureTypeList', ns=WFS_NAMESPACE))
        featuretypeelems=featuretypelistelem.findall(nspath('FeatureType', ns=WFS_NAMESPACE))
        for f in featuretypeelems:  
            kwds=f.findall(nspath('Keywords/Keyword'))
            if kwds is not None:
                for kwd in kwds[:]:
                    if kwd.text not in self.identification.keywords:
                        self.identification.keywords.append(kwd.text)
	
   
        #TODO: update serviceProvider metadata, miss it out for now
        serviceproviderelem=self._capabilities.find(nspath('ServiceProvider'))
        self.provider=ServiceProvider(serviceproviderelem)   
        
        #serviceOperations metadata 
        self.operations=[]
        
        for elem in self._capabilities.find(nspath('OperationsMetadata'))[:]:
            if elem.tag !=nspath('ExtendedCapabilities'):
                self.operations.append(OperationsMetadata(elem))
                   
        #serviceContents metadata: our assumption is that services use a top-level 
        #layer as a metadata organizer, nothing more. 
        
        self.contents={} 
        featuretypelist=self._capabilities.find(nspath('FeatureTypeList',ns=WFS_NAMESPACE))
        features = self._capabilities.findall(nspath('FeatureTypeList/FeatureType', ns=WFS_NAMESPACE))
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
                   featureversion=None, propertyname=None, maxfeatures=None,storedQueryID=None, storedQueryParams={},
                   method=nspath('Get')):
        """Request and return feature data as a file-like object.
        #TODO: NOTE: have changed property name from ['*'] to None - check the use of this in WFS 2.0
        Parameters
        ----------
        typename : list
            List of typenames (string)
        filter : string 
            XML-encoded OGC filter expression.
        bbox : tuple
            (left, bottom, right, top) in the feature type's coordinates == (minx, miny, maxx, maxy)
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

        There are 3 different modes of use

        1) typename and bbox (simple spatial query)
        2) typename and filter (==query) (more expressive)
        3) featureid (direct access to known features)
        """
        #log.debug(self.getOperationByName('GetFeature'))
        base_url = self.getOperationByName('GetFeature').methods[method]['url']
        request = {'service': 'WFS', 'version': self.version, 'request': 'GetFeature'}
        
        # check featureid
        if featureid:
            request['featureid'] = ','.join(featureid)
        elif bbox:
#            request['bbox'] = ','.join([str(x) for x in bbox])
            request['query'] ='<Query xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" xmlns:csml="http://ndg.nerc.ac.uk/csml"><ogc:Filter><ogc:BBOX><gml:Envelope srsName="WGS84"><gml:lowerCorner>%s %s</gml:lowerCorner><gml:upperCorner>%s %s</gml:upperCorner></gml:Envelope></ogc:BBOX></ogc:Filter></Query>'%(bbox[1],bbox[0],bbox[3],bbox[2])
        elif filter:
            request['query'] = str(filter)
        if typename:
            request['typename'] = ','.join(typename)
        if propertyname: 
            request['propertyname'] = ','.join(propertyname)
        if featureversion: 
            request['featureversion'] = str(featureversion)
        if maxfeatures: 
            request['maxfeatures'] = str(maxfeatures)
        if storedQueryID: 
            request['storedQuery_id']=str(storedQueryID)
            for param in storedQueryParams:
                request[param]=storedQueryParams[param]
                
        
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

    def getpropertyvalue(self, query=None, storedquery_id=None, valuereference=None, typename=None, method=nspath('Get'),**kwargs):
        ''' the WFS GetPropertyValue method'''         
        base_url = self.getOperationByName('GetPropertyValue').methods[method]['url']
        request = {'service': 'WFS', 'version': self.version, 'request': 'GetPropertyValue'}
        if query:
            request['query'] = str(query)
        if valuereference: 
            request['valueReference'] = str(valuereference)
        if storedquery_id: 
            request['storedQuery_id'] = str(storedquery_id)
        if typename:
            request['typename']=str(typename)
        if kwargs:
            for kw in kwargs.keys():
                request[kw]=str(kwargs[kw])
        data=urlencode(request)
        u = urlopen(base_url + data)
        return u.read()
        
        
    def _getStoredQueries(self):
        ''' gets descriptions of the stored queries available on the server '''
        sqs=[]
        #This method makes two calls to the WFS - one ListStoredQueries, and one DescribeStoredQueries. The information is then
        #aggregated in 'StoredQuery' objects
        method=nspath('Get')
        
        #first make the ListStoredQueries response and save the results in a dictionary if form {storedqueryid:(title, returnfeaturetype)}
        base_url = self.getOperationByName('ListStoredQueries').methods[method]['url']
        request = {'service': 'WFS', 'version': self.version, 'request': 'ListStoredQueries'}
        data = urlencode(request)
        u = urlopen(base_url + data)
        tree=etree.fromstring(u.read())
        base_url = self.getOperationByName('ListStoredQueries').methods[method]['url']
        tempdict={}       
        for sqelem in tree[:]:
            title=rft=id=None
            id=sqelem.get('id')
            for elem in sqelem[:]:
                if elem.tag==nspath('Title', WFS_NAMESPACE):
                    title=elem.text
                elif elem.tag==nspath('ReturnFeatureType', WFS_NAMESPACE):
                    rft=elem.text
            tempdict[id]=(title,rft)        #store in temporary dictionary
        
        #then make the DescribeStoredQueries request and get the rest of the information about the stored queries 
        base_url = self.getOperationByName('DescribeStoredQueries').methods[method]['url']
        request = {'service': 'WFS', 'version': self.version, 'request': 'DescribeStoredQueries'}
        data = urlencode(request)
        u = urlopen(base_url + data)
        tree=etree.fromstring(u.read())
        tempdict2={} 
        for sqelem in tree[:]:
            params=[] #list to store parameters for the stored query description
            id =sqelem.get('id')
            for elem in sqelem[:]:
                if elem.tag==nspath('Abstract', WFS_NAMESPACE):
                    abstract=elem.text
                elif elem.tag==nspath('Parameter', WFS_NAMESPACE):
                    newparam=Parameter(elem.get('name'), elem.get('type'))
                    params.append(newparam)
            tempdict2[id]=(abstract, params) #store in another temporary dictionary
        
        #now group the results into StoredQuery objects:
        for key in tempdict.keys(): 
            abstract='blah'
            parameters=[]
            sqs.append(StoredQuery(key, tempdict[key][0], tempdict[key][1], tempdict2[key][0], tempdict2[key][1]))
        return sqs
    storedqueries = property(_getStoredQueries, None)

    def getOperationByName(self, name):
        """Return a named content item."""
        for item in self.operations:
            if item.name == name:
                return item
        raise KeyError, "No operation named %s" % name

class StoredQuery(object):
    '''' Class to describe a storedquery '''
    def __init__(self, id, title, returntype, abstract, parameters):
        self.id=id
        self.title=title
        self.returnfeaturetype=returntype
        self.abstract=abstract
        self.parameters=parameters
        
class Parameter(object):
    def __init__(self, name, type):
        self.name=name
        self.type=type
        
    
class ContentMetadata:
    """Abstraction for WFS metadata.
    
    Implements IMetadata.
    """

    def __init__(self, elem, parent):
        """."""
        self.id = elem.find(nspath('Name',ns=WFS_NAMESPACE)).text
        self.title = elem.find(nspath('Title',ns=WFS_NAMESPACE)).text
        # bboxes
        self.boundingBox = None
        b = elem.find(nspath('BoundingBox',ns=WFS_NAMESPACE))
        if b is not None:
            self.boundingBox = (float(b.attrib['minx']),float(b.attrib['miny']),
                    float(b.attrib['maxx']), float(b.attrib['maxy']),
                    b.attrib['SRS'])
        self.boundingBoxWGS84 = None
        b = elem.find(nspath('LatLongBoundingBox',ns=WFS_NAMESPACE))
        if b is not None:
            self.boundingBoxWGS84 = (
                    float(b.attrib['minx']),float(b.attrib['miny']),
                    float(b.attrib['maxx']), float(b.attrib['maxy']),
                    )
        # crs options
        self.crsOptions = [srs.text for srs in elem.findall(nspath('SRS'))]

        # verbs
        self.verbOptions = [op.tag for op \
            in parent.findall(nspath('Operations/*',ns=WFS_NAMESPACE))]
        self.verbOptions + [op.tag for op \
            in elem.findall(nspath('Operations/*',ns=WFS_NAMESPACE)) \
            if op.tag not in self.verbOptions]
        
        #others not used but needed for iContentMetadata harmonisation
        self.styles=None
        self.timepositions=None

class WFSCapabilitiesReader(object):
    """Read and parse capabilities document into a lxml.etree infoset
    """

    def __init__(self, version='2.0.0'):
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
