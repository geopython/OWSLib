#!/usr/bin/python
# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2009 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@hotmail.com>
#
# Contact email: tomkralidis@hotmail.com
# =============================================================================

from lxml import etree
from owslib import filter
from owslib import util

# default variables

outputformat = 'application/xml'
schema = 'http://schemas.opengis.net/csw/2.0.2/CSW-discovery.xsd'

namespaces = {
    None : 'http://www.opengis.net/cat/csw/2.0.2',
    'csw': 'http://www.opengis.net/cat/csw/2.0.2',
    'dc' : 'http://purl.org/dc/elements/1.1/',
    'dct': 'http://purl.org/dc/terms/',
    'gmd': 'http://www.isotc211.org/2005/gmd',
    'gml': 'http://www.opengis.net/gml',
    'ogc': 'http://www.opengis.net/ogc',
    'ows': 'http://www.opengis.net/ows',
    'rim': 'urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0',
    'xs' : 'http://www.w3.org/2001/XMLSchema',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}

schema_location = '%s %s' % (namespaces['csw'], schema)

class request:
    """ csw class """
    def __init__(self, url, lang='en-US', version='2.0.2'):
        """

        csw Constructor

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

    def fetch(self):
        self.response = util.http_post(self.url, self.request, self.lang)

    def GetCapabilities(self):
        """

        construct a GetCapabilities request

        Parameters
        ----------

        none
        
        """

        node0 = etree.Element(util.nspath('GetCapabilities', namespaces['csw']), nsmap=namespaces)
        node0.set('service', self.service)
        node0.set(util.nspath('schemaLocation', namespaces['xsi']), schema_location)
        tmp = etree.SubElement(node0, util.nspath('AcceptVersions', namespaces['ows']))
        etree.SubElement(tmp, util.nspath('Version', namespaces['ows'])).text = self.version
        tmp2 = etree.SubElement(node0, util.nspath('AcceptFormats', namespaces['ows']))
        etree.SubElement(tmp2, util.nspath('OutputFormat', namespaces['ows'])).text = outputformat
        self.request = util.xml2string(etree.tostring(node0, pretty_print=True))
    
    def DescribeRecord(self, typename='csw:Record', format=outputformat):
        """

        construct a DescribeRecord request

        Parameters
        ----------

        - typename: the typename to describe (default is 'csw:Record')
        - format: the outputFormat (default is 'application/xml')
 
        """

        node0 = etree.Element(util.nspath('DescribeRecord', namespaces['csw']), nsmap=namespaces)
        node0.set('service', self.service)
        node0.set('version', self.version)
        node0.set('outputFormat', format)
        node0.set('schemaLanguage', namespaces['xs'])
        node0.set(util.nspath('schemaLocation', namespaces['xsi']), schema_location)
        etree.SubElement(node0, util.nspath('TypeName', namespaces['csw'])).text = typename
        self.request = util.xml2string(etree.tostring(node0, pretty_print=True))
    
    def GetDomain(self, dname, dtype='parameter'):
        """

        construct a GetDomain request

        Parameters
        ----------

        - dname: the value of the Parameter or Property to query
        - dtype: whether to query a parameter (parameter) or property (property)

        """

        dtypename = 'ParameterName'
        node0 = etree.Element(util.nspath('GetDomain', namespaces['csw']), nsmap=namespaces)
        node0.set('service', self.service)
        node0.set('version', self.version)
        node0.set(util.nspath('schemaLocation', namespaces['xsi']), schema_location)
        if dtype == 'property':
            dtypename = 'PropertyName'
        etree.SubElement(node0, util.nspath(dtypename, namespaces['csw'])).text = dname
        self.request = util.xml2string(etree.tostring(node0, pretty_print=True))
     
    def GetRecords(self, qtype, keyword, bbox=None, esn='full', sortby=None, schema=namespaces['csw'], format=outputformat):
        """

        construct a GetRecords request

        Parameters
        ----------

        - qtype: type of resource to query (i.e. service, dataset)
        - keyword: freetext keyword
        - bbox: the bounding box of the spatial query in the form [minx,miny,maxx,maxy]
        - esn: the ElementSetName 'full', 'brief' or 'summary' (default is 'full')
        - sortby: property to sort results on (default is 'dc:title')
        - schema: the outputSchema (default is 'http://www.opengis.net/cat/csw/2.0.2')
        - format: the outputFormat (default is 'application/xml')

        """

        if schema is None:
            outputschema = namespaces['csw']
        else:
            outputschema = schema

        if schema == 'iso':
            outputschema = namespaces['gmd']
    
        node0 = etree.Element(util.nspath('GetRecords', namespaces['csw']), nsmap=namespaces)
        node0.set('outputSchema', outputschema)
        node0.set('outputFormat', format)
        node0.set('version', self.version)
        node0.set('resultType', 'results')
        node0.set('service', self.service)
        node0.set(util.nspath('schemaLocation', namespaces['xsi']), schema_location)
    
        pcount = 0
        if qtype is not None:
            pcount += 1
        if keyword is not None:
            pcount += 1
        if bbox is not None:
            pcount += 1

        node1 = etree.SubElement(node0, util.nspath('Query', namespaces['csw']))
        node1.set('typeNames', 'csw:Record')
    
        etree.SubElement(node1, util.nspath('ElementSetName', namespaces['csw'])).text = esn
    
        if keyword is not None or bbox is not None or qtype is not None:    
            node2 = etree.SubElement(node1, util.nspath('Constraint', namespaces['csw']))
            node2.set('version', '1.1.0')
            node3 = etree.SubElement(node2, util.nspath('Filter', namespaces['ogc']))
            node4 = None
            flt   = filter.request()    
            
            if pcount > 1:
                node4 = etree.SubElement(node3, util.nspath('And', namespaces['ogc']))
    
            if qtype is not None:
                if node4 is not None:
                    flt.PropertyIsEqualTo(node4, 'dc:type', qtype)
                else:
                    flt.PropertyIsEqualTo(node3, 'dc:type', qtype)
    
            if bbox is not None:
                if node4 is not None:
                    flt.BBOX(node4, bbox)
                else:
                    flt.BBOX(node3, bbox)
    
            if keyword is not None:
                if node4 is not None:
                    flt.PropertyIsLike(node4, 'AnyText', '%%%s%%' % keyword)
                else:
                    flt.PropertyIsLike(node3, 'AnyText', '%%%s%%' % keyword)

        if sortby is not None:
            flt.SortBy(node1, sortby)
    
        self.request = util.xml2string(etree.tostring(node0, pretty_print=True))
    
    def GetRecordById(self, id, esn='full', schema=namespaces['csw'], format=outputformat):
        """

        construct a GetRecordById request

        Parameters
        ----------

        - id: the Id
        - esn: the ElementSetName 'full', 'brief' or 'summary' (default is 'full')
        - schema: the outputSchema (default is 'http://www.opengis.net/cat/csw/2.0.2')
        - format: the outputFormat (default is 'application/xml')

        """
    
        node0 = etree.Element(util.nspath('GetRecordById', namespaces['csw']), nsmap=namespaces)
        node0.set('outputSchema', schema)
        node0.set('outputFormat', format)
        node0.set('version', self.version)
        node0.set('service', self.service)
        node0.set(util.nspath('schemaLocation', namespaces['xsi']), schema_location)
        etree.SubElement(node0, util.nspath('Id', namespaces['csw'])).text = id
        etree.SubElement(node0, util.nspath('ElementSetName', namespaces['csw'])).text = esn
        self.request = util.xml2string(etree.tostring(node0, pretty_print=True))
