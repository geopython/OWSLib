# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2009 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@hotmail.com>
#
# Contact email: tomkralidis@hotmail.com
# =============================================================================

""" CSW request and response processor """

import StringIO
import random
from owslib.etree import etree
from owslib.filter import *
from owslib import util
from owslib.ows import *
from owslib.iso import *
from owslib.fgdc import *
from owslib.dif import *

# default variables

outputformat = 'application/xml'
schema = 'http://schemas.opengis.net/csw/2.0.2/CSW-discovery.xsd'

namespaces = {
    None : 'http://www.opengis.net/cat/csw/2.0.2',
    'csw': 'http://www.opengis.net/cat/csw/2.0.2',
    'dc' : 'http://purl.org/dc/elements/1.1/',
    'dct': 'http://purl.org/dc/terms/',
    'dif': 'http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/',
    'fgdc': 'http://www.fgdc.gov',
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
    def __init__(self, url, lang='en-US', version='2.0.2', timeout=10):
        """

        Construct and process a GetCapabilities request

        Parameters
        ----------

        - url: the URL of the CSW
        - lang: the language (default is 'en-US')
        - version: version (default is '2.0.2')
        - timeout: timeout in seconds

        """

        self.url = url
        self.lang = lang
        self.version = version
        self.timeout = timeout
        self.service = 'CSW'
        self.exceptionreport = None
        self.owscommon = OwsCommon('1.0.0')

        # construct request
        node0 = etree.Element(util.nspath_eval('csw:GetCapabilities', namespaces))
        node0.set('service', self.service)
        node0.set(util.nspath_eval('xsi:schemaLocation', namespaces), schema_location)
        tmp = etree.SubElement(node0, util.nspath_eval('ows:AcceptVersions', namespaces))
        etree.SubElement(tmp, util.nspath_eval('ows:Version', namespaces)).text = self.version
        tmp2 = etree.SubElement(node0, util.nspath_eval('ows:AcceptFormats', namespaces))
        etree.SubElement(tmp2, util.nspath_eval('ows:OutputFormat', namespaces)).text = outputformat
        self.request = util.xml2string(etree.tostring(node0))

        self._invoke()

        if self.exceptionreport is None:
            # ServiceIdentification
            val = self._exml.find(util.nspath_eval('ows:ServiceIdentification', namespaces))
            self.identification=ServiceIdentification(val,self.owscommon.namespace)
            # ServiceProvider
            val = self._exml.find(util.nspath_eval('ows:ServiceProvider', namespaces))
            self.provider=ServiceProvider(val,self.owscommon.namespace)
            # ServiceOperations metadata 
            self.operations=[]
            for elem in self._exml.findall(util.nspath_eval('ows:OperationsMetadata/ows:Operation', namespaces)):
                self.operations.append(OperationsMetadata(elem, self.owscommon.namespace))
    
            # FilterCapabilities
            val = self._exml.find(util.nspath_eval('ogc:Filter_Capabilities', namespaces))
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
        node0 = etree.Element(util.nspath_eval('csw:DescribeRecord', namespaces))
        node0.set('service', self.service)
        node0.set('version', self.version)
        node0.set('outputFormat', format)
        node0.set('schemaLanguage', namespaces['xs2'])
        node0.set(util.nspath_eval('xsi:schemaLocation', namespaces), schema_location)
        etree.SubElement(node0, util.nspath_eval('csw:TypeName', namespaces)).text = typename
        self.request = util.xml2string(etree.tostring(node0))

        self._invoke()

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
        node0 = etree.Element(util.nspath_eval('csw:GetDomain', namespaces))
        node0.set('service', self.service)
        node0.set('version', self.version)
        node0.set(util.nspath_eval('xsi:schemaLocation', namespaces), schema_location)
        if dtype == 'property':
            dtypename = 'PropertyName'
        etree.SubElement(node0, util.nspath_eval('csw:%s' % dtypename, namespaces)).text = dname
        self.request = util.xml2string(etree.tostring(node0))

        self._invoke()

        if self.exceptionreport is None:
            self.results = {}

            val = self._exml.find(util.nspath_eval('csw:DomainValues', namespaces)).attrib.get('type')
            self.results['type'] = util.testXMLValue(val, True)

            val = self._exml.find(util.nspath_eval('csw:DomainValues/csw:%s' % dtypename, namespaces))
            self.results[dtype] = util.testXMLValue(val)

            # get the list of values associated with the Domain
            self.results['values'] = []

            for f in self._exml.findall(util.nspath_eval('csw:DomainValues/csw:ListOfValues/csw:Value', namespaces)):
                self.results['values'].append(util.testXMLValue(f))

    def getrecords(self, qtype=None, keywords=[], typenames='csw:Record', propertyname='csw:AnyText', bbox=None, esn='full', sortby=None, outputschema=namespaces['csw'], format=outputformat, startposition=0, maxrecords=10, cql=None, xml=None):
        """

        Construct and process a  GetRecords request

        Parameters
        ----------

        - qtype: type of resource to query (i.e. service, dataset)
        - keywords: list of keywords
        - typenames: the typeNames to query against (default is csw:Record)
        - propertyname: the PropertyName to Filter against 
        - bbox: the bounding box of the spatial query in the form [minx,miny,maxx,maxy]
        - esn: the ElementSetName 'full', 'brief' or 'summary' (default is 'full')
        - sortby: property to sort results on (default is 'dc:title')
        - outputschema: the outputSchema (default is 'http://www.opengis.net/cat/csw/2.0.2')
        - format: the outputFormat (default is 'application/xml')
        - startposition: requests a slice of the result set, starting at this position (default is 0)
        - maxrecords: the maximum number of records to return. No records are returned if 0 (default is 10)
        - cql: common query language text.  Note this overrides bbox, qtype, keywords
        - xml: raw XML request.  Note this overrides all other options

        """

        if xml is not None:
            self.request = xml
            e=etree.fromstring(xml)
            val = e.find(util.nspath_eval('csw:Query/csw:ElementSetName', namespaces))
            if val is not None:
                esn = util.testXMLValue(val)

        else:
            # construct request
            node0 = etree.Element(util.nspath_eval('csw:GetRecords', namespaces))
            node0.set('xmlns:ows', namespaces['ows'])
            node0.set('outputSchema', outputschema)
            node0.set('outputFormat', format)
            node0.set('version', self.version)
            node0.set('resultType', 'results')
            node0.set('service', self.service)
            if startposition > 0:
                node0.set('startPosition', str(startposition))
            node0.set('maxRecords', str(maxrecords))
            node0.set(util.nspath_eval('xsi:schemaLocation', namespaces), schema_location)
    
            node1 = etree.SubElement(node0, util.nspath_eval('csw:Query', namespaces))
            node1.set('typeNames', typenames)
        
            etree.SubElement(node1, util.nspath_eval('csw:ElementSetName', namespaces)).text = esn
    
            self._setconstraint(node1, qtype, propertyname, keywords, bbox, cql)
    
            if sortby is not None:
                setsortby(node1, sortby)
    
            self.request = util.xml2string(etree.tostring(node0))

        self._invoke()
 
        if self.exceptionreport is None:
            self.results = {}
    
            # process search results attributes
            val = self._exml.find(util.nspath_eval('csw:SearchResults', namespaces)).attrib.get('numberOfRecordsMatched')
            self.results['matches'] = int(util.testXMLValue(val, True))
            val = self._exml.find(util.nspath_eval('csw:SearchResults', namespaces)).attrib.get('numberOfRecordsReturned')
            self.results['returned'] = int(util.testXMLValue(val, True))
            val = self._exml.find(util.nspath_eval('csw:SearchResults', namespaces)).attrib.get('nextRecord')
            self.results['nextrecord'] = int(util.testXMLValue(val, True))
    
            # process list of matching records
            self.records = {}

            self._parserecords(outputschema, esn)

    def getrecordbyid(self, id=[], esn='full', outputschema=namespaces['csw'], format=outputformat):
        """

        Construct and process a GetRecordById request

        Parameters
        ----------

        - id: the list of Ids
        - esn: the ElementSetName 'full', 'brief' or 'summary' (default is 'full')
        - outputschema: the outputSchema (default is 'http://www.opengis.net/cat/csw/2.0.2')
        - format: the outputFormat (default is 'application/xml')

        """

        # construct request 
        node0 = etree.Element(util.nspath_eval('csw:GetRecordById', namespaces))
        node0.set('outputSchema', outputschema)
        node0.set('outputFormat', format)
        node0.set('version', self.version)
        node0.set('service', self.service)
        node0.set(util.nspath_eval('xsi:schemaLocation', namespaces), schema_location)
        for i in id:
            etree.SubElement(node0, util.nspath_eval('csw:Id', namespaces)).text = i
        etree.SubElement(node0, util.nspath_eval('csw:ElementSetName', namespaces)).text = esn
        self.request = util.xml2string(etree.tostring(node0))

        self._invoke()
 
        if self.exceptionreport is None:
            self.results = {}
            self.records = {}
            self._parserecords(outputschema, esn)

    def transaction(self, ttype=None, typename='csw:Record', record=None, propertyname=None, propertyvalue=None, bbox=None, keywords=[], cql=None):
        """

        Construct and process a Transaction request

        Parameters
        ----------

        - ttype: the type of transaction 'insert, 'update', 'delete'
        - typename: the typename to describe (default is 'csw:Record')
        - record: the XML record to insert
        - propertyname: the RecordProperty/PropertyName to Filter against
        - propertyvalue: the RecordProperty Value to Filter against (for updates)
        - bbox: the bounding box of the spatial query in the form [minx,miny,maxx,maxy]
        - keywords: list of keywords
        - cql: common query language text.  Note this overrides bbox, qtype, keywords

        """

        # construct request
        node0 = etree.Element(util.nspath_eval('csw:Transaction', namespaces))
        node0.set('version', self.version)
        node0.set('service', self.service)
        node0.set(util.nspath_eval('xsi:schemaLocation', namespaces), schema_location)

        validtransactions = ['insert', 'update', 'delete']

        if ttype not in validtransactions:  # invalid transaction
            raise RuntimeError, 'Invalid transaction \'%s\'.' % ttype

        node1 = etree.SubElement(node0, util.nspath_eval('csw:%s' % ttype.capitalize(), namespaces))

        if ttype != 'update':  
            node1.set('typeName', typename)

        if ttype == 'insert':
            if record is None:
                raise RuntimeError, 'Nothing to insert.'
            node1.append(etree.fromstring(record))
 
        if ttype == 'update':
            if record is not None:
                node1.append(etree.fromstring(record))
            else:
                if propertyname is not None and propertyvalue is not None:
                    node2 = etree.SubElement(node1, util.nspath_eval('csw:RecordProperty', namespaces))
                    etree.SubElement(node2, util.nspath_eval('csw:Name', namespaces)).text = propertyname
                    etree.SubElement(node2, util.nspath_eval('csw:Value', namespaces)).text = propertyvalue
                    self._setconstraint(node1, qtype, propertyname, keywords, bbox, cql)

        if ttype == 'delete':
            self._setconstraint(node1, None, propertyname, keywords, bbox, cql)

        self.request = util.xml2string(etree.tostring(node0))

        self._invoke()
        self.results = {}

        if self.exceptionreport is None:
            self._parsetransactionsummary()
            self._parseinsertresult()

    def harvest(self, source, resourcetype, resourceformat=None, harvestinterval=None, responsehandler=None):
        """

        Construct and process a Harvest request

        Parameters
        ----------

        - source: a URI to harvest
        - resourcetype: namespace identifying the type of resource
        - resourceformat: MIME type of the resource
        - harvestinterval: frequency of harvesting, in ISO8601
        - responsehandler: endpoint that CSW should responsd to with response

        """

        # construct request
        node0 = etree.Element(util.nspath_eval('csw:Harvest', namespaces))
        node0.set('version', self.version)
        node0.set('service', self.service)
        node0.set(util.nspath_eval('xsi:schemaLocation', namespaces), schema_location)
        etree.SubElement(node0, util.nspath_eval('csw:Source', namespaces)).text = source
        etree.SubElement(node0, util.nspath_eval('csw:ResourceType', namespaces)).text = resourcetype
        if resourceformat is not None:
            etree.SubElement(node0, util.nspath_eval('csw:ResourceFormat', namespaces)).text = resourceformat
        if harvestinterval is not None:
            etree.SubElement(node0, util.nspath_eval('csw:HarvestInterval', namespaces)).text = harvestinterval
        if responsehandler is not None:
            etree.SubElement(node0, util.nspath_eval('csw:ResponseHandler', namespaces)).text = responsehandler
       
        self.request = util.xml2string(etree.tostring(node0))

        self._invoke()
        self.results = {}

        if self.exceptionreport is None:
            val = self._exml.find(util.nspath_eval('csw:Acknowledgement', namespaces))
            if util.testXMLValue(val) is not None:
                ts = val.attrib.get('timeStamp')
                self.timestamp = util.testXMLValue(ts, True)
                id = val.find(util.nspath_eval('csw:RequestId', namespaces))
                self.id = util.testXMLValue(id) 
            else:
                self._parsetransactionsummary()
                self._parseinsertresult()

    def _parseinsertresult(self):
        self.results['inserted'] = []
        for i in self._exml.findall(util.nspath_eval('csw:InsertResult', namespaces)):
            for j in i.findall(util.nspath_eval('csw:BriefRecord/dc:identifier', namespaces)):
                self.results['inserted'].append(util.testXMLValue(j))

    def _parserecords(self, outputschema, esn):
        if outputschema == namespaces['gmd']: # iso 19139
            for i in self._exml.findall('.//'+util.nspath_eval('gmd:MD_Metadata', namespaces)):
                val = i.find(util.nspath_eval('gmd:fileIdentifier/gco:CharacterString', namespaces))
                identifier = self._setidentifierkey(util.testXMLValue(val))
                self.records[identifier] = MD_Metadata(i)
        elif outputschema == namespaces['fgdc']: # fgdc csdgm
            for i in self._exml.findall('.//metadata'):
                val = i.find('idinfo/datasetid')
                identifier = self._setidentifierkey(util.testXMLValue(val))
                self.records[identifier] = Metadata(i)
        # CSWs define the dif namespace with the trailing '/' as an
        # outputSchema, but actual responses indeed define it with '/' as an outputSchema
        # this is an interoperability issue to be resolved
        # [:-1] is a workaround for now
        elif outputschema == namespaces['dif'][:-1]: # nasa dif, strip the trailing '/' for now
            for i in self._exml.findall('.//'+util.nspath_eval('dif:DIF', namespaces)):
                val = i.find(util.nspath_eval('dif:Entry_ID', namespaces))
                identifier = self._setidentifierkey(util.testXMLValue(val))
                self.records[identifier] = DIF(i)
        else: # process default
            for i in self._exml.findall('.//'+util.nspath_eval('csw:%s' % self._setesnel(esn), namespaces)):
                val = i.find(util.nspath_eval('dc:identifier', namespaces))
                identifier = self._setidentifierkey(util.testXMLValue(val))
                self.records[identifier] = CswRecord(i)

    def _parsetransactionsummary(self):
        val = self._exml.find(util.nspath_eval('csw:TransactionSummary', namespaces))
        if val is not None:
            id = val.attrib.get('requestId')
            self.results['requestid'] = util.testXMLValue(id, True)
            ts = val.find(util.nspath_eval('csw:totalInserted', namespaces))
            self.results['inserted'] = util.testXMLValue(ts)
            ts = val.find(util.nspath_eval('csw:totalUpdated', namespaces))
            self.results['updated'] = util.testXMLValue(ts)
            ts = val.find(util.nspath_eval('csw:totalDeleted', namespaces))
            self.results['deleted'] = util.testXMLValue(ts)

    def _setesnel(self, esn):
        """ Set the element name to parse depending on the ElementSetName requested """
        el = 'Record'
        if esn == 'brief':
            el = 'BriefRecord'
        if esn == 'summary':
            el = 'SummaryRecord'
        return el

    def _setidentifierkey(self, el):
        if el is None: 
            return 'owslib_random_%i' % random.randint(1,65536)
        else:
            return el

    def _setconstraint(self, parent, qtype=None, propertyname='csw:AnyText', keywords=[], bbox=None, cql=None):
        #if keywords or bbox is not None or qtype is not None or cql is not None:
        if keywords or bbox is not None or qtype is not None or cql is not None:
            node0 = etree.SubElement(parent, util.nspath_eval('csw:Constraint', namespaces))
            node0.set('version', '1.1.0')

            if cql is not None:  # send raw CQL query
                import warnings
                warnings.warn('CQL passed (overrides all other parameters', UserWarning)
                node1 = etree.SubElement(node0, util.nspath_eval('csw:CqlText', namespaces))
                node1.text = cql
            else:  # construct a Filter request
                flt = FilterRequest()
                node0.append(flt.set(qtype=qtype, keywords=keywords, propertyname=propertyname,bbox=bbox))

    def _invoke(self):
        # do HTTP request
        self.response = util.http_post(self.url, self.request, self.lang, self.timeout)

        # parse result see if it's XML
        self._exml = etree.parse(StringIO.StringIO(self.response))

        # it's XML.  Attempt to decipher whether the XML response is CSW-ish """
        valid_xpaths = [
            util.nspath_eval('ows:ExceptionReport', namespaces),
            util.nspath_eval('csw:Capabilities', namespaces),
            util.nspath_eval('csw:DescribeRecordResponse', namespaces),
            util.nspath_eval('csw:GetDomainResponse', namespaces),
            util.nspath_eval('csw:GetRecordsResponse', namespaces),
            util.nspath_eval('csw:GetRecordByIdResponse', namespaces),
            util.nspath_eval('csw:HarvestResponse', namespaces),
            util.nspath_eval('csw:TransactionResponse', namespaces)
        ]

        if self._exml.getroot().tag not in valid_xpaths:
            raise RuntimeError, 'Document is XML, but not CSW-ish'

        # check if it's an OGC Exception
        val = self._exml.find(util.nspath_eval('ows:Exception', namespaces))
        if val is not None:
            self.exceptionreport = ExceptionReport(self._exml, self.owscommon.namespace)
        else:
            self.exceptionreport = None

class CswRecord(object):
    """ Process csw:Record, csw:BriefRecord, csw:SummaryRecord """
    def __init__(self, record):

        if hasattr(record, 'getroot'):  # standalone document
            self.xml = etree.tostring(md.getroot())
        else:  # part of a larger document
            self.xml = etree.tostring(record)

        # some CSWs return records with multiple identifiers based on 
        # different schemes.  Use the first dc:identifier value to set
        # self.identifier, and set self.identifiers as a list of dicts
        val = record.find(util.nspath_eval('dc:identifier', namespaces))
        self.identifier = util.testXMLValue(val)

        self.identifiers = []
        for i in record.findall(util.nspath_eval('dc:identifier', namespaces)):
            d = {}
            d['scheme'] = i.attrib.get('scheme')
            d['identifier'] = i.text
            self.identifiers.append(d)

        val = record.find(util.nspath_eval('dc:type', namespaces))
        self.type = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dc:title', namespaces))
        self.title = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dct:alternative', namespaces))
        self.alternative = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dct:isPartOf', namespaces))
        self.ispartof = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dct:abstract', namespaces))
        self.abstract = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dc:date', namespaces))
        self.date = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dct:created', namespaces))
        self.created = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dct:issued', namespaces))
        self.issued = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dc:relation', namespaces))
        self.relation = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dc:temporal', namespaces))
        self.temporal = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dc:URI', namespaces))
        self.uri = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dct:modified', namespaces))
        self.modified = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dc:creator', namespaces))
        self.creator = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dc:publisher', namespaces))
        self.publisher = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dc:coverage', namespaces))
        self.coverage = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dc:contributor', namespaces))
        self.contributor = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dc:language', namespaces))
        self.language = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dc:source', namespaces))
        self.source = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dct:rightsHolder', namespaces))
        self.rightsholder = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dct:accessRights', namespaces))
        self.accessrights = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dct:license', namespaces))
        self.license = util.testXMLValue(val)

        val = record.find(util.nspath_eval('dc:format', namespaces))
        self.format = util.testXMLValue(val)

        self.subjects = []
        for i in record.findall(util.nspath_eval('dc:subject', namespaces)):
            self.subjects.append(util.testXMLValue(i))

        self.rights = []
        for i in record.findall(util.nspath_eval('dc:rights', namespaces)):
            self.rights.append(util.testXMLValue(i))

        val = record.find(util.nspath_eval('dct:spatial', namespaces))
        self.spatial = util.testXMLValue(val)

        val = record.find(util.nspath_eval('ows:BoundingBox', namespaces))
        if val is not None:
            self.bbox = BoundingBox(val, namespaces['ows'])
        else:
            self.bbox = None
