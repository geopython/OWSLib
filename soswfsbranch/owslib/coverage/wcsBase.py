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

#!/usr/bin/env python

import logging

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
        self.log = logging.getLogger()
        consoleh  = logging.StreamHandler()
        self.log.addHandler(consoleh)	
        return obj
    
    def __init__(self):
        pass    
           
    def getDescribeCoverage(self,identifier):
         reader = DescribeCoverageReader(self.version, identifier)
         #Note: should implement some sort of cache so the same request isn't repeated
         return reader.read(self.url)
         
    def setLogLevel(self, level='CRITICAL'):
        #accepts level = DEBUG, INFO, WARNING, ERROR, CRITICAL
        if level=='DEBUG':
            self.log.setLevel(logging.DEBUG)
        elif level=='INFO':
            self.log.setLevel(logging.INFO)     
        elif level=='WARNING':
            self.log.setLevel(logging.WARNING)
        elif level=='ERROR':
            self.log.setLevel(logging.ERROR)
        elif level=='CRITICAL':
            self.log.setLevel(logging.CRITICAL)
        
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
            #NOTE: WCS 1.1.0 is ambigous about whether it should be identifier
            #or identifiers (see tables 9, 10 of specification)  
            if 'identifiers' not in params:
                qs.append(('identifiers', self.identifier))
            if 'identifier' not in params:
                qs.append(('identifier', self.identifier))
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
    
       
class RereadableURL(StringIO, object):
    """ Class that acts like a combination of StringIO and url - has seek method and url headers etc """
    def __init__(self, u):
        #get url headers etc from url
        self.headers = u.headers                
        #get file like seek, read methods from StringIO
        content=u.read()
        super(RereadableURL, self).__init__(content)