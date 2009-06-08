#!/usr/bin/python
# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2009 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@hotmail.com>
#
# Contact email: tomkralidis@hotmail.com
# =============================================================================

import StringIO
from owslib.etree import etree
from owslib.filter import *
from owslib import util
from owslib.ows import *

# default variables

outputformat = 'application/xml'
schema = 'http://schemas.opengis.net/csw/2.0.2/CSW-discovery.xsd'

namespaces = {
    None : 'http://www.opengis.net/cat/csw/2.0.2',
    'csw': 'http://www.opengis.net/cat/csw/2.0.2',
    'dc' : 'http://purl.org/dc/elements/1.1/',
    'dct': 'http://purl.org/dc/terms/',
    'gco': 'http://www.isotc211.org/2005/gco',
    'gmd': 'http://www.isotc211.org/2005/gmd',
    'gml': 'http://www.opengis.net/gml',
    'ogc': 'http://www.opengis.net/ogc',
    'ows': 'http://www.opengis.net/ows',
    'rim': 'urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0',
    'xs' : 'http://www.w3.org/2001/XMLSchema',
    'xs2': 'http://www.w3.org/XML/Schema',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}

schema_location = '%s %s' % (namespaces['csw'], schema)

class CatalogueServiceWeb:
    """ csw request class """
    def __init__(self, url, lang='en-US', version='2.0.2'):
        """

        Construct and process a GetCapabilities request

        Parameters
        ----------

        - url: the URL of the CSW
        - lang: the language (default is 'en-US')
        - version: version (default is '2.0.2')

        """

        self.url = url
        self.lang = lang
        self.version = version
        self.service = 'CSW'
        self.exceptionreport = None
        self.owscommon = OwsCommon('1.0.0')

        # construct request
        node0 = etree.Element(util.nspath('GetCapabilities', namespaces['csw']))
        node0.set('service', self.service)
        node0.set(util.nspath('schemaLocation', namespaces['xsi']), schema_location)
        tmp = etree.SubElement(node0, util.nspath('AcceptVersions', namespaces['ows']))
        etree.SubElement(tmp, util.nspath('Version', namespaces['ows'])).text = self.version
        tmp2 = etree.SubElement(node0, util.nspath('AcceptFormats', namespaces['ows']))
        etree.SubElement(tmp2, util.nspath('OutputFormat', namespaces['ows'])).text = outputformat
        self.request = util.xml2string(etree.tostring(node0))

        """

        self.request = <?xml version="1.0" encoding="ISO-8859-1"?>
<GetCapabilities xmlns="http://www.opengis.net/cat/csw/2.0.2" xmlns:ows="http://www.opengis.net/ows" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/cat/csw/2.0.2 http://schemas.opengis.net/csw/2.0.2/CSW-discovery.xsd" service="CSW">
   <ows:AcceptVersions>
      <ows:Version>2.0.2</ows:Version>
   </ows:AcceptVersions>
   <ows:AcceptFormats>
      <ows:OutputFormat>application/xml</ows:OutputFormat>
   </ows:AcceptFormats>
</GetCapabilities>

        """

        # invoke
        self.response = util.http_post(self.url, self.request, self.lang)

        # parse result
        self._capabilities = etree.parse(StringIO.StringIO(self.response))

        # check for exceptions
        self._isexception(self._capabilities, self.owscommon.namespace)

        if self.exceptionreport is None:
            # ServiceIdentification
            val = self._capabilities.find(util.nspath('ServiceIdentification', namespaces['ows']))
            self.identification=ServiceIdentification(val,self.owscommon.namespace)
            # ServiceProvider
            val = self._capabilities.find(util.nspath('ServiceProvider', namespaces['ows']))
            self.provider=ServiceProvider(val,self.owscommon.namespace)
            # ServiceOperations metadata 
            self.operations=[]
            for elem in self._capabilities.findall(util.nspath('OperationsMetadata/Operation', namespaces['ows'])):
                self.operations.append(OperationsMetadata(elem, self.owscommon.namespace))
    
            # FilterCapabilities
            val = self._capabilities.find(util.nspath('Filter_Capabilities', namespaces['ogc']))
            self.filters=FilterCapabilities(val)
 
    def describerecord(self, typename='csw:Record', format=outputformat):
        """

        Construct and process DescribeRecord request

        Parameters
        ----------

        - typename: the typename to describe (default is 'csw:Record')
        - format: the outputFormat (default is 'application/xml')
 
        """

        # construct request
        node0 = etree.Element(util.nspath('DescribeRecord', namespaces['csw']))
        node0.set('service', self.service)
        node0.set('version', self.version)
        node0.set('outputFormat', format)
        node0.set('schemaLanguage', namespaces['xs2'])
        node0.set(util.nspath('schemaLocation', namespaces['xsi']), schema_location)
        etree.SubElement(node0, util.nspath('TypeName', namespaces['csw'])).text = typename
        self.request = util.xml2string(etree.tostring(node0))

        # invoke
        self.response = util.http_post(self.url, self.request, self.lang)

        # parse result
        # TODO: process the XML Schema (you're on your own for now with self.response)

    def getdomain(self, dname, dtype='parameter'):
        """

        Construct and process a GetDomain request

        Parameters
        ----------

        - dname: the value of the Parameter or Property to query
        - dtype: whether to query a parameter (parameter) or property (property)

        """

        # construct request
        dtypename = 'ParameterName'
        node0 = etree.Element(util.nspath('GetDomain', namespaces['csw']))
        node0.set('service', self.service)
        node0.set('version', self.version)
        node0.set(util.nspath('schemaLocation', namespaces['xsi']), schema_location)
        if dtype == 'property':
            dtypename = 'PropertyName'
        etree.SubElement(node0, util.nspath(dtypename, namespaces['csw'])).text = dname
        self.request = util.xml2string(etree.tostring(node0))

        # invoke
        self.response = util.http_post(self.url, self.request, self.lang)

        # parse result
        self._values = etree.parse(StringIO.StringIO(self.response))

        # check for exceptions
        self._isexception(self._values, self.owscommon.namespace)

        if self.exceptionreport is None:
            self.results = {}

            val = self._values.find(util.nspath('DomainValues', namespaces['csw'])).attrib.get('type')
            self.results['type'] = util.testXMLValue(val, True)

            val = self._values.find(util.nspath('DomainValues/' + dtypename, namespaces['csw']))
            self.results[dtype] = util.testXMLValue(val)

            # get the list of values associated with the Domain
            self.results['values'] = []

            for f in self._values.findall(util.nspath('DomainValues/ListOfValues/Value', namespaces['csw'])):
                self.results['values'].append(util.testXMLValue(f))

    def getrecords(self, qtype=None, keyword='*', typenames='csw:Record', propertyname='AnyText', bbox=None, esn='full', sortby=None, schema=namespaces['csw'], format=outputformat, startposition=0, maxrecords=10):
        """

        Construct and process a  GetRecords request

        Parameters
        ----------

        - qtype: type of resource to query (i.e. service, dataset)
        - keyword: freetext keyword
        - typenames: the typeNames to query against (default is csw:Record)
        - propertyname: the PropertyName to Filter against 
        - bbox: the bounding box of the spatial query in the form [minx,miny,maxx,maxy]
        - esn: the ElementSetName 'full', 'brief' or 'summary' (default is 'full')
        - sortby: property to sort results on (default is 'dc:title')
        - schema: the outputSchema (default is 'http://www.opengis.net/cat/csw/2.0.2')
        - format: the outputFormat (default is 'application/xml')
        - startposition: requests a slice of the result set, starting at this position (default is 0)
        - maxrecords: the maximum number of records to return. No records are returned if 0 (default is 10)

        """

        # construct request
        node0 = etree.Element(util.nspath('GetRecords', namespaces['csw']))
        node0.set('outputSchema', schema)
        node0.set('outputFormat', format)
        node0.set('version', self.version)
        node0.set('resultType', 'results')
        node0.set('service', self.service)
        if startposition > 0:
            node0.set('startPosition', str(startposition))
        node0.set('maxRecords', str(maxrecords))
        node0.set(util.nspath('schemaLocation', namespaces['xsi']), schema_location)

        # decipher number of query parameters ( > 1 sets an 'And' Filter
        pcount = 0
        if qtype is not None:
            pcount += 1
        if keyword is not None:
            pcount += 1
        if bbox is not None:
            pcount += 1

        node1 = etree.SubElement(node0, util.nspath('Query', namespaces['csw']))
        node1.set('typeNames', typenames)
    
        etree.SubElement(node1, util.nspath('ElementSetName', namespaces['csw'])).text = esn

        # decipher if the query is for real
        if keyword is not None or bbox is not None or qtype is not None:    
            node2 = etree.SubElement(node1, util.nspath('Constraint', namespaces['csw']))
            node2.set('version', '1.1.0')
            node3 = etree.SubElement(node2, util.nspath('Filter', namespaces['ogc']))
            node4 = None

            # construct a Filter request
            flt   = FilterRequest()    
 
            if pcount > 1: # Filter should be And-ed
                node4 = etree.SubElement(node3, util.nspath('And', namespaces['ogc']))

            # set the query type if passed
            # TODO: need a smarter way to figure these out
            if qtype is not None:
                if node4 is not None:
                    flt.setpropertyisequalto(node4, 'dc:type', qtype)
                else:
                    flt.setpropertyisequalto(node3, 'dc:type', qtype)

            # set a bbox query if passed
            if bbox is not None:
                if node4 is not None:
                    flt.setbbox(node4, bbox)
                else:
                    flt.setbbox(node3, bbox)

            # set a keyword query if passed
            if keyword is not None:
                if node4 is not None:
                    flt.setpropertyislike(node4, propertyname, '%%%s%%' % keyword)
                else:
                    flt.setpropertyislike(node3, propertyname, '%%%s%%' % keyword)

        # set a sort if passed
        if sortby is not None:
            flt.setsortby(node1, sortby)
    
        self.request = util.xml2string(etree.tostring(node0))

        # invoke
        self.response = util.http_post(self.url, self.request, self.lang)

        # parse result 
        self._records = etree.parse(StringIO.StringIO(self.response))

        # check for exceptions
        self._isexception(self._capabilities, self.owscommon.namespace)
 
        if self.exceptionreport is None:
            self.results = {}
    
            # process search results attributes
            val = self._records.find(util.nspath('SearchResults', namespaces['csw'])).attrib.get('numberOfRecordsMatched')
            self.results['matches'] = int(util.testXMLValue(val, True))
            val = self._records.find(util.nspath('SearchResults', namespaces['csw'])).attrib.get('numberOfRecordsReturned')
            self.results['returned'] = int(util.testXMLValue(val, True))
            val = self._records.find(util.nspath('SearchResults', namespaces['csw'])).attrib.get('nextRecord')
            self.results['nextrecord'] = int(util.testXMLValue(val, True))
    
            # process list of matching records
            self.results['records'] = []
    
            for f in self._records.findall(util.nspath('SearchResults/' + self._setesnel(esn), namespaces['csw'])):
                self.results['records'].append(CswRecord(f))

    def getrecordbyid(self, id, esn='full', schema=namespaces['csw'], format=outputformat):
        """

        Construct and process a GetRecordById request

        Parameters
        ----------

        - id: the Id
        - esn: the ElementSetName 'full', 'brief' or 'summary' (default is 'full')
        - schema: the outputSchema (default is 'http://www.opengis.net/cat/csw/2.0.2')
        - format: the outputFormat (default is 'application/xml')

        """

        # construct request 
        node0 = etree.Element(util.nspath('GetRecordById', namespaces['csw']))
        node0.set('outputSchema', schema)
        node0.set('outputFormat', format)
        node0.set('version', self.version)
        node0.set('service', self.service)
        node0.set(util.nspath('schemaLocation', namespaces['xsi']), schema_location)
        etree.SubElement(node0, util.nspath('Id', namespaces['csw'])).text = id
        etree.SubElement(node0, util.nspath('ElementSetName', namespaces['csw'])).text = esn
        self.request = util.xml2string(etree.tostring(node0))

        # invoke
        self.response = util.http_post(self.url, self.request, self.lang)

        # parse result
        self._records = etree.parse(StringIO.StringIO(self.response))

        # check for exceptions
        self._isexception(self._capabilities, self.owscommon.namespace)
 
        if self.exceptionreport is None:
            self.results = {}

            self.results['records'] = []

            # process matching record
            val = self._records.find(util.nspath(self._setesnel(esn), namespaces['csw']))
            self.results['records'].append(CswRecord(val))

    def _setesnel(self, esn):
        """ Set the element name to parse depending on the ElementSetName requested """
        el = 'Record'
        if esn == 'brief':
            el = 'BriefRecord'
        if esn == 'summary':
            el = 'SummaryRecord'
        return el

    def _isexception(self, elem, namespace):
        val = elem.find(util.nspath('Exception', namespaces['ows']))
        if val is not None:
            self.exceptionreport = ExceptionReport(elem, namespace)
        else:
            self.exceptionreport = None

class CswRecord(object):
    """ Process csw:Record, csw:BriefRecord, csw:SummaryRecord """
    def __init__(self, record):
        val = record.find(util.nspath('identifier', namespaces['dc']))
        self.identifier = util.testXMLValue(val)

        val = record.find(util.nspath('type', namespaces['dc']))
        self.type = util.testXMLValue(val)

        val = record.find(util.nspath('title', namespaces['dc']))
        self.title = util.testXMLValue(val)

        val = record.find(util.nspath('abstract', namespaces['dct']))
        self.abstract = util.testXMLValue(val)

        val = record.find(util.nspath('URI', namespaces['dc']))
        self.uri = util.testXMLValue(val)

        val = record.find(util.nspath('modified', namespaces['dct']))
        self.modified = util.testXMLValue(val)

        val = record.find(util.nspath('creator', namespaces['dc']))
        self.creator = util.testXMLValue(val)

        val = record.find(util.nspath('publisher', namespaces['dc']))
        self.publisher = util.testXMLValue(val)

        val = record.find(util.nspath('contributor', namespaces['dc']))
        self.contributor = util.testXMLValue(val)

        val = record.find(util.nspath('contributor', namespaces['dc']))
        self.contributor = util.testXMLValue(val)

        val = record.find(util.nspath('language', namespaces['dc']))
        self.language = util.testXMLValue(val)

        val = record.find(util.nspath('source', namespaces['dc']))
        self.source = util.testXMLValue(val)

        val = record.find(util.nspath('format', namespaces['dc']))
        self.format = util.testXMLValue(val)

        self.subjects = []
        for i in record.findall(util.nspath('subject', namespaces['dc'])):
            self.subjects.append(util.testXMLValue(i))

        self.rights = []
        for i in record.findall(util.nspath('rights', namespaces['dc'])):
            self.rights.append(util.testXMLValue(i))

        val = record.find(util.nspath('BoundingBox', namespaces['ows']))
        if val is not None:
            self.bbox = BoundingBox(val, namespaces['ows'])
        else:
            self.bbox = None
