# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2004, 2006 Sean C. Gillies
# Copyright (c) 2007 STFC <http://www.stfc.ac.uk>
#
# Authors : 
#          Dominic Lowe <d.lowe@rl.ac.uk>
#
# Contact email: d.lowe@rl.ac.uk
# =============================================================================

from urllib import urlencode
from urllib2 import urlopen
from owslib.etree import etree
import cgi
from StringIO import StringIO
class WCSBase(object):
    """Base class to be subclassed by version dependent WCS classes. Provides 'high-level' version independent methods"""
    def __new__(self,url, xml):
        """ overridden __new__ method 
        
        @type url: string
        @param url: url of WCS capabilities document
        @type xml: string
        @param xml: elementtree object
        @return: inititalised WCSBase object
        """
        obj=object.__new__(self, url, xml)
        obj.__init__(url, xml)
        return obj
    
    def __init__(self):
        pass    
    
    def _getGenCovListProperty(self):
        '''genericCoverages attribute is used to hold a list of CoverageInfo objects which are generic and independent of the WCS version. As a result of this they may be lossy compared to interrogating the version specific capabilities document, but they serve the purpose of providing a uniform view of different WCS versions '''
        if not hasattr(self, '_genericCoverages'):
            self._genericCoverages=self._buildGenericCoverages()
        return self._genericCoverages
    genericCoverages=property(_getGenCovListProperty, None)
    
    
    def _getGenServiceProperty(self):
        '''genericService attribute is used to hold a list of non-version specific info about the service '''
        if not hasattr(self, '_genericService'):
            self._genericService=self._buildGenericServiceInfo()
        return self._genericService
    serviceInfo=property(_getGenServiceProperty, None)
    
    def _buildGenericCoverages(self):
        ''' must be overridden to provide enable generic interface'''        
        return []
    
    def _buildGenericProviderInfo(self):
        ''' must be overridden to provide enable generic interface'''
        return ProviderInfo()
    
    
    def _buildGenericServiceInfo(self):
        ''' must be overridden to provide enable generic interface'''
        return ServiceInfo()
     
    
    #def listCoverages(self):
        #''' returns a dictionary contining the {id, name} values for each coverageSummary'''
        #coverages={}
        #for item in self.genericCoverages:
            #coverages[item.identifier]=item.labelordescription
        #return coverages

    def getCvgByIdentifier(self,identifier):
        ''' returns a version independent coverage object '''
        for item in self.genericCoverages:
            if item.identifier == identifier:
                return item
        raise KeyError, "No coverage summary with identifier %s" %identifier
    
    def getCvgByLabel(self,label):
        ''' returns a version independent coverage object '''
        for item in self.genericCoverages:
            if item.labelordescription == label:
                return item
        raise KeyError, "No coverage summary with label %s" %label
        
    def getDescribeCoverage(self,identifier):
         reader = DescribeCoverageReader(self.version, identifier)
         #Note: should implement some sort of cache so the same request isn't repeated
         return reader.read(self.url)
    
class WCSCapabilitiesReader(object):
    """Read and parses WCS capabilities document into a lxml.etree infoset
    """

    def __init__(self, version):
        """Initialize
        @type version: string
        @param version: WCS Version parameter e.g '1.0.0'
        """
        self.version = version
        self._infoset = None

    def capabilities_url(self, service_url):
        """Return a capabilities url
        @type service_url: string
        @param service_url: base url of WCS service
        @rtype: string
        @return: getCapabilities URL
        """
        qs = []
        if service_url.find('?') != -1:
            qs = cgi.parse_qsl(service_url.split('?')[1])

        params = [x[0] for x in qs]

        if 'service' not in params:
            qs.append(('service', 'WCS'))
        if 'request' not in params:
            qs.append(('request', 'GetCapabilities'))
        if 'version' not in params:
            qs.append(('version', self.version))

        urlqs = urlencode(tuple(qs))
        return service_url.split('?')[0] + '?' + urlqs

    def read(self, service_url):
        """Get and parse a WCS capabilities document, returning an
        elementtree tree

        @type service_url: string
        @param service_url: The base url, to which is appended the service,
        version, and request parameters
        @rtype: elementtree tree
        @return: An elementtree tree representation of the capabilities document
        """
        request = self.capabilities_url(service_url)
        u = urlopen(request)
        return etree.fromstring(u.read())
    
    def readString(self, st):
        """Parse a WCS capabilities document, returning an
        instance of WCSCapabilitiesInfoset

        string should be an XML capabilities document
        """
        if not isinstance(st, str):
            raise ValueError("String must be of type string, not %s" % type(st))
        return etree.fromstring(st)
    
class DescribeCoverageReader(object):
    """Read and parses WCS DescribeCoverage document into a lxml.etree infoset
    """

    def __init__(self, version, identifier):
        """Initialize
        @type version: string
        @param version: WCS Version parameter e.g '1.0.0'
        """
        self.version = version
        self._infoset = None
        self.identifier=identifier

    def descCov_url(self, service_url):
        """Return a describe coverage url
        @type service_url: string
        @param service_url: base url of WCS service
        @rtype: string
        @return: getCapabilities URL
        """
        qs = []
        if service_url.find('?') != -1:
            qs = cgi.parse_qsl(service_url.split('?')[1])

        params = [x[0] for x in qs]

        if 'service' not in params:
            qs.append(('service', 'WCS'))
        if 'request' not in params:
            qs.append(('request', 'DescribeCoverage'))
        if 'version' not in params:
            qs.append(('version', self.version))
        
        if self.version == '1.0.0':
            if 'coverage' not in params:
                qs.append(('coverage', self.identifier))
        elif self.version == '1.1.0':
            if 'identifiers' not in params:
                qs.append(('identifiers', self.identifier))
                qs.append(('format', 'text/xml'))
        urlqs = urlencode(tuple(qs))
        return service_url.split('?')[0] + '?' + urlqs

    def read(self, service_url):
        """Get and parse a Describe Coverage document, returning an
        elementtree tree

        @type service_url: string
        @param service_url: The base url, to which is appended the service,
        version, and request parameters
        @rtype: elementtree tree
        @return: An elementtree tree representation of the capabilities document
        """
        request = self.descCov_url(service_url)
        u = urlopen(request)
        return etree.fromstring(u.read())
          
    
    
class CoverageInfo(object):
    '''' Information about a coverage, not tied to any particular WCS version '''
    def __init__(self, identifier= None, labelordescription=None, wgs84bbox=None, otherbbox=None, _timeLimits=None):
        self.identifier=identifier
        self.labelordescription=labelordescription
        self.wgs84bbox=wgs84bbox
        self.otherbbox=otherbbox
        self._timeLimits=_timeLimits
        self._supCRS=lambda(i):None
        self._supFormats=lambda(i):None
        
    def getSupportedCRS(self):
         '''the supCRS method should be altered by the calling object so that the correct value is returned. This will probably require a DescribeCoverage request, which is version specific '''
         return self._supCRS(self.identifier)
     
    def getSupportedFormats(self):
         '''the supFormats method should be altered by the calling object so that the correct value is returned. This will probably require a DescribeCoverage request, which is version specific '''
         return self._supFormats(self.identifier)
    
    def getTimeLimits(self):
        if not self._timeLimits:
            try:
                return self._times(self.identifier) #some versions (eg 1.1.0) may require a describe coverage request to get time limits
            except:
                return None
        else:
            return self._timeLimits#others (eg 1.0.0) may have retrieved it from the original getcapabilites requests
     
    supportedCRS=property(getSupportedCRS, None)
    supportedFormats=property(getSupportedFormats, None)
    timeLimits=property(getTimeLimits, None)

        
class ServiceInfo(object):
    '''' Information about the service available and the provider, not tied to any particular WCS version '''
    def __init__(self, fees=None, accessConstraints=None, providerName=None,contactName=None,contactPosition=None,addressString=None,phone=None,fax=None,email=None):
        self.fees=fees
        self.accessConstraints=accessConstraints
        self.providerName=providerName
        self.contactName=contactName
        self.contactPosition=contactPosition
        self.addressString=addressString
        self.phone=phone
        self.fax=fax
        self.email=email
       
class RereadableURL(StringIO, object):
    """ Class that acts like a combination of StringIO and url - has seek method and url headers etc """
    def __init__(self, u):
        #get url headers etc from url
        self.headers = u.headers                
        #get file like seek, read methods from StringIO
        content=u.read()
        super(RereadableURL, self).__init__(content)