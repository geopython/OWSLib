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
from owslib import fes
from owslib.util import nspath_eval, xml2string, testXMLValue, http_post, setrootelement
from owslib import ows
from owslib.iso import MD_Metadata
from owslib.fgdc import Metadata
from owslib.dif import DIF
from owslib.namespaces import OWSLibNamespaces

# default variables

outputformat = 'application/xml'
schema = 'http://schemas.opengis.net/csw/2.0.2/CSW-discovery.xsd'

ns = OWSLibNamespaces()

schema_location = '%s %s' % (ns.get_namespace('csw'), schema)

_ows_version = '1.0.0'

def nsp_ows(item):
    return nspath_eval(item,_ows_version)
def nsp(item):
    return nspath_eval(item)

class CatalogueServiceWeb:
    """ csw request class """
    def __init__(self, url, lang='en-US', version='2.0.2', timeout=10, skip_caps=False):
        """

        Construct and process a GetCapabilities request

        Parameters
        ----------

        - url: the URL of the CSW
        - lang: the language (default is 'en-US')
        - version: version (default is '2.0.2')
        - timeout: timeout in seconds
        - skip_caps: whether to skip GetCapabilities processing on init (default is False)

        """

        self.url = url
        self.lang = lang
        self.version = version
        self.timeout = timeout
        self.service = 'CSW'
        self.exceptionreport = None

        if not skip_caps:  # process GetCapabilities
            # construct request
            nsmap = {
                'csw' : ns.get_namespace('csw'),
                'ows' : ns.get_versioned_namespace('ows',_ows_version),
                'xsi' : ns.get_namespace('xsi'),
            }

            node0 = setrootelement('csw:GetCapabilities', nsmap)

            node0.set('service', self.service)
            node0.set(nsp('xsi:schemaLocation'), schema_location)

            tmp = etree.SubElement(node0, nsp_ows('ows:AcceptVersions'))
            etree.SubElement(tmp, nsp_ows('ows:Version')).text = self.version
            tmp2 = etree.SubElement(node0, nsp_ows('ows:AcceptFormats'))
            etree.SubElement(tmp2, nsp_ows('ows:OutputFormat')).text = outputformat
            self.request = xml2string(etree.tostring(node0))
    
            self._invoke()
    
            if self.exceptionreport is None:
                # ServiceIdentification
                val = self._exml.find(nsp_ows('ows:ServiceIdentification'))
                self.identification=ows.ServiceIdentification(val,ns.get_versioned_namespace('ows', _ows_version))
                # ServiceProvider
                val = self._exml.find(nsp_ows('ows:ServiceProvider'))
                self.provider=ows.ServiceProvider(val)
                # ServiceOperations metadata 
                op = self._exml.find(nsp_ows('ows:OperationsMetadata'))
                self.operations = ows.OperationsMetadata(op, ns.get_versioned_namespace('ows', _ows_version)).operations
        
                # FilterCapabilities
                val = self._exml.find(nsp('ogc:Filter_Capabilities'))
                self.filters=fes.FilterCapabilities(val)
 
    def describerecord(self, typename='csw:Record', format=outputformat):
        """

        Construct and process DescribeRecord request

        Parameters
        ----------

        - typename: the typename to describe (default is 'csw:Record')
        - format: the outputFormat (default is 'application/xml')
 
        """

        # construct request

        nsmap = {
                'csw' : ns.get_namespace('csw'),
                'xsi' : ns.get_namespace('xsi'),
            }

        node0 = setrootelement('csw:DescribeRecord', nsmap)
        node0.set('outputFormat', format)
        node0.set('schemaLanguage',ns.get_namespace('xs2'))
        node0.set('service', self.service)
        node0.set('version', self.version)
        node0.set(nsp('xsi:schemaLocation'), schema_location)
        etree.SubElement(node0, nsp('csw:TypeName')).text = typename
        self.request = xml2string(etree.tostring(node0))

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

        nsmap = {
                'csw' : ns.get_namespace('csw'),
                'xsi' : ns.get_namespace('xsi'),
            }

        node0 = setrootelement('csw:GetDomain', nsmap)
        node0.set('service', self.service)
        node0.set('version', self.version)
        node0.set(nsp('xsi:schemaLocation'), schema_location)
        if dtype == 'property':
            dtypename = 'PropertyName'
        etree.SubElement(node0, nsp('csw:%s' % dtypename)).text = dname
        self.request = xml2string(etree.tostring(node0))

        self._invoke()

        if self.exceptionreport is None:
            self.results = {}

            val = self._exml.find(nsp('csw:DomainValues')).attrib.get('type')
            self.results['type'] = testXMLValue(val, True)

            val = self._exml.find(nsp('csw:DomainValues/csw:%s' % dtypename))
            self.results[dtype] = testXMLValue(val)
            # get the list of values associated with the Domain
            self.results['values'] = []

            for f in self._exml.findall(nsp('csw:DomainValues/csw:ListOfValues/csw:Value')):
                self.results['values'].append(testXMLValue(f))

    def getrecords(self, qtype=None, keywords=[], typenames='csw:Record', propertyname='csw:AnyText', bbox=None, esn='summary', sortby=None, outputschema=None, format=outputformat, startposition=0, maxrecords=10, cql=None, xml=None):
        """

        Construct and process a  GetRecords request

        Parameters
        ----------

        - qtype: type of resource to query (i.e. service, dataset)
        - keywords: list of keywords
        - typenames: the typeNames to query against (default is csw:Record)
        - propertyname: the PropertyName to Filter against 
        - bbox: the bounding box of the spatial query in the form [minx,miny,maxx,maxy]
        - esn: the ElementSetName 'full', 'brief' or 'summary' (default is 'summary')
        - sortby: property to sort results on (default is 'dc:title')
        - outputschema: the outputSchema (default is 'http://www.opengis.net/cat/csw/2.0.2')
        - format: the outputFormat (default is 'application/xml')
        - startposition: requests a slice of the result set, starting at this position (default is 0)
        - maxrecords: the maximum number of records to return. No records are returned if 0 (default is 10)
        - cql: common query language text.  Note this overrides bbox, qtype, keywords
        - xml: raw XML request.  Note this overrides all other options
        """

        if outputschema is None:
            outputschema = ns.get_namespace('csw')

        if xml is not None:
            self.request = xml
            e=etree.fromstring(xml)
            val = e.find(nsp('csw:Query/csw:ElementSetName'))
            if val is not None:
                esn = testXMLValue(val)
        else:
            # construct request

            nsmap = {
                'xsi' : ns.get_namespace('xsi'),
                'ogc' : ns.get_namespace('ogc'),
                'dif' : ns.get_namespace('dif'),
                'ows' : ns.get_versioned_namespace('ows', _ows_version),
                'fgdc': ns.get_namespace('fgdc'),
                'gmd' : ns.get_namespace('gmd'),
                'csw' : ns.get_namespace('csw')
            }

            node0 = setrootelement('csw:GetRecords', nsmap)
            node0.set('outputSchema', outputschema)
            node0.set('outputFormat', format)
            node0.set('version', self.version)
            node0.set('resultType', 'results')
            node0.set('service', self.service)
            if startposition > 0:
                node0.set('startPosition', str(startposition))
            node0.set('maxRecords', str(maxrecords))
            node0.set(nsp('xsi:schemaLocation'), schema_location)
    
            node1 = etree.SubElement(node0, nsp('csw:Query'))
            node1.set('typeNames', typenames)
        
            etree.SubElement(node1, nsp('csw:ElementSetName')).text = esn
    
            self._setconstraint(node1, qtype, propertyname, keywords, bbox, cql)
    
            if sortby is not None:
                fes.setsortby(node1, sortby)
    
            self.request = xml2string(etree.tostring(node0))

        self._invoke()
 
        if self.exceptionreport is None:
            self.results = {}
    
            # process search results attributes
            val = self._exml.find(nsp('csw:SearchResults')).attrib.get('numberOfRecordsMatched')
            self.results['matches'] = int(testXMLValue(val, True))
            val = self._exml.find(nsp('csw:SearchResults')).attrib.get('numberOfRecordsReturned')
            self.results['returned'] = int(testXMLValue(val, True))
            val = self._exml.find(nsp('csw:SearchResults')).attrib.get('nextRecord')
            self.results['nextrecord'] = int(testXMLValue(val, True))
    
            # process list of matching records
            self.records = {}

            self._parserecords(outputschema, esn)

    def getrecordbyid(self, id=[], esn='full', outputschema=None, format=outputformat):
        """

        Construct and process a GetRecordById request

        Parameters
        ----------

        - id: the list of Ids
        - esn: the ElementSetName 'full', 'brief' or 'summary' (default is 'full')
        - outputschema: the outputSchema (default is 'http://www.opengis.net/cat/csw/2.0.2')
        - format: the outputFormat (default is 'application/xml')

        """

        if outputschema is None:
            outputschema = ns.get_namespace('csw')

        nsmap = {
            'csw' : ns.get_namespace('csw'),
            'xsi' : ns.get_namespace('xsi')
        }   

        # construct request 
        node0 = setrootelement('csw:GetRecordById', nsmap)
        node0.set('outputFormat', format)
        node0.set('outputSchema', outputschema)
        node0.set('service', self.service)
        node0.set('version', self.version)
        node0.set(nsp('xsi:schemaLocation'), schema_location)
        for i in id:
            etree.SubElement(node0, nsp('csw:Id')).text = i
        etree.SubElement(node0, nsp('csw:ElementSetName')).text = esn
        self.request = xml2string(etree.tostring(node0))

        self._invoke()
 
        if self.exceptionreport is None:
            self.results = {}
            self.records = {}
            self._parserecords(outputschema, esn)

    def transaction(self, ttype=None, typename='csw:Record', record=None, propertyname=None, propertyvalue=None, bbox=None, keywords=[], cql=None, identifier=None):
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
        - identifier: record identifier.  Note this overrides bbox, qtype, keywords, cql

        """

        # construct request
        node0 = setrootelement('csw:Transaction')
        node0.set('version', self.version)
        node0.set('service', self.service)
        node0.set(nsp('xsi:schemaLocation'), schema_location)

        validtransactions = ['insert', 'update', 'delete']

        if ttype not in validtransactions:  # invalid transaction
            raise RuntimeError, 'Invalid transaction \'%s\'.' % ttype

        node1 = etree.SubElement(node0, nsp('csw:%s' % ttype.capitalize()))

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
                    node2 = etree.SubElement(node1, nsp('csw:RecordProperty'))
                    etree.SubElement(node2, nsp('csw:Name')).text = propertyname
                    etree.SubElement(node2, nsp('csw:Value')).text = propertyvalue
                    self._setconstraint(node1, qtype, propertyname, keywords, bbox, cql, identifier)

        if ttype == 'delete':
            self._setconstraint(node1, None, propertyname, keywords, bbox, cql, identifier)
        self.request = xml2string(etree.tostring(node0))

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
        node0 = setrootelement('csw:Harvest')
        node0.set('version', self.version)
        node0.set('service', self.service)
        node0.set(nsp('xsi:schemaLocation'), schema_location)
        etree.SubElement(node0, nsp('csw:Source')).text = source
        etree.SubElement(node0, nsp('csw:ResourceType')).text = resourcetype
        if resourceformat is not None:
            etree.SubElement(node0, nsp('csw:ResourceFormat')).text = resourceformat
        if harvestinterval is not None:
            etree.SubElement(node0, nsp('csw:HarvestInterval')).text = harvestinterval
        if responsehandler is not None:
            etree.SubElement(node0, nsp('csw:ResponseHandler')).text = responsehandler
       
        self.request = xml2string(etree.tostring(node0))

        self._invoke()
        self.results = {}

        if self.exceptionreport is None:
            val = self._exml.find(nsp('csw:Acknowledgement'))
            if testXMLValue(val) is not None:
                ts = val.attrib.get('timeStamp')
                self.timestamp = testXMLValue(ts, True)
                id = val.find(nsp('csw:RequestId'))
                self.id = testXMLValue(id) 
            else:
                self._parsetransactionsummary()
                self._parseinsertresult()

    def _parseinsertresult(self):
        self.results['insertresults'] = []
        for i in self._exml.findall(nsp('csw:InsertResult')):
            for j in i.findall(nsp('csw:BriefRecord/dc:identifier')):
                self.results['insertresults'].append(testXMLValue(j))

    def _parserecords(self, outputschema, esn):
        if outputschema == ns.get_namespace('gmd'): # iso 19139
            for i in self._exml.findall('.//'+nsp('gmd:MD_Metadata')):
                val = i.find(nsp('gmd:fileIdentifier/gco:CharacterString'))
                identifier = self._setidentifierkey(testXMLValue(val))
                self.records[identifier] = MD_Metadata(i)
        elif outputschema == ns.get_namespace('fgdc'): # fgdc csdgm
            for i in self._exml.findall('.//metadata'):
                val = i.find('idinfo/datasetid')
                identifier = self._setidentifierkey(testXMLValue(val))
                self.records[identifier] = Metadata(i)
        elif outputschema == ns.get_namespace('dif'): # nasa dif
            for i in self._exml.findall('.//'+nsp('dif:DIF')):
                val = i.find(nsp('dif:Entry_ID'))
                identifier = self._setidentifierkey(testXMLValue(val))
                self.records[identifier] = DIF(i)
        else: # process default
            for i in self._exml.findall('.//'+nsp('csw:%s' % self._setesnel(esn))):
                val = i.find(nsp('dc:identifier'))
                identifier = self._setidentifierkey(testXMLValue(val))
                self.records[identifier] = CswRecord(i)

    def _parsetransactionsummary(self):
        val = self._exml.find(nsp('csw:TransactionSummary'))
        if val is not None:
            rid = val.attrib.get('requestId')
            self.results['requestid'] = testXMLValue(rid, True)
            ts = val.find(nsp('csw:totalInserted'))
            self.results['inserted'] = int(testXMLValue(ts))
            ts = val.find(nsp('csw:totalUpdated'))
            self.results['updated'] = int(testXMLValue(ts))
            ts = val.find(nsp('csw:totalDeleted'))
            self.results['deleted'] = int(testXMLValue(ts))

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

    def _setconstraint(self, parent, qtype=None, propertyname='csw:AnyText', keywords=[], bbox=None, cql=None, identifier=None):
        if keywords or bbox is not None or qtype is not None or cql is not None or identifier is not None:
            node0 = etree.SubElement(parent, nsp('csw:Constraint'))
            node0.set('version', '1.1.0')

            if identifier is not None:  # set identifier filter, overrides all other parameters
                flt = fes.FilterRequest()
                node0.append(flt.set(identifier=identifier))
            elif cql is not None:  # send raw CQL query
                # CQL passed, overrides all other parameters
                node1 = etree.SubElement(node0, nsp('csw:CqlText'))
                node1.text = cql
            else:  # construct a Filter request
                flt = fes.FilterRequest()
                node0.append(flt.set(qtype=qtype, keywords=keywords, propertyname=propertyname,bbox=bbox))

    def _invoke(self):
        # do HTTP request
        self.response = http_post(self.url, self.request, self.lang, self.timeout)

        # parse result see if it's XML
        self._exml = etree.parse(StringIO.StringIO(self.response))

        # it's XML.  Attempt to decipher whether the XML response is CSW-ish """
        valid_xpaths = [
            nsp_ows('ows:ExceptionReport'),
            nsp('csw:Capabilities'),
            nsp('csw:DescribeRecordResponse'),
            nsp('csw:GetDomainResponse'),
            nsp('csw:GetRecordsResponse'),
            nsp('csw:GetRecordByIdResponse'),
            nsp('csw:HarvestResponse'),
            nsp('csw:TransactionResponse')
        ]

        if self._exml.getroot().tag not in valid_xpaths:
            raise RuntimeError, 'Document is XML, but not CSW-ish'

        # check if it's an OGC Exception
        val = self._exml.find(nsp_ows('ows:Exception'))
        if val is not None:
            raise ows.ExceptionReport(self._exml, ns.get_versioned_namespace('ows',_ows_version))
        else:
            self.exceptionreport = None

    def get_operation_by_name(self, name): 
        """
            Return a Operation item by name, case insensitive
        """
        for item in self.operations.keys():
            if item.lower() == name.lower():
                return self.operations[item]
        raise KeyError, "No Operation named %s" % name

class CswRecord(object):
    """ Process csw:Record, csw:BriefRecord, csw:SummaryRecord """
    def __init__(self, record):

        if hasattr(record, 'getroot'):  # standalone document
            self.xml = etree.tostring(record.getroot())
        else:  # part of a larger document
            self.xml = etree.tostring(record)

        # some CSWs return records with multiple identifiers based on 
        # different schemes.  Use the first dc:identifier value to set
        # self.identifier, and set self.identifiers as a list of dicts
        val = record.find(nsp('dc:identifier'))
        self.identifier = testXMLValue(val)

        self.identifiers = []
        for i in record.findall(nsp('dc:identifier')):
            d = {}
            d['scheme'] = i.attrib.get('scheme')
            d['identifier'] = i.text
            self.identifiers.append(d)

        val = record.find(nsp('dc:type'))
        self.type = testXMLValue(val)

        val = record.find(nsp('dc:title'))
        self.title = testXMLValue(val)

        val = record.find(nsp('dct:alternative'))
        self.alternative = testXMLValue(val)

        val = record.find(nsp('dct:isPartOf'))
        self.ispartof = testXMLValue(val)

        val = record.find(nsp('dct:abstract'))
        self.abstract = testXMLValue(val)

        val = record.find(nsp('dc:date'))
        self.date = testXMLValue(val)

        val = record.find(nsp('dct:created'))
        self.created = testXMLValue(val)

        val = record.find(nsp('dct:issued'))
        self.issued = testXMLValue(val)

        val = record.find(nsp('dc:relation'))
        self.relation = testXMLValue(val)

        val = record.find(nsp('dc:temporal'))
        self.temporal = testXMLValue(val)

        self.uris = []  # list of dicts
        for i in record.findall(nsp('dc:URI')):
            uri = {}
            uri['protocol'] = testXMLValue(i.attrib.get('protocol'), True)
            uri['name'] = testXMLValue(i.attrib.get('name'), True)
            uri['description'] = testXMLValue(i.attrib.get('description'), True)
            uri['url'] = testXMLValue(i)

            self.uris.append(uri)

        self.references = []  # list of dicts
        for i in record.findall(nsp('dct:references')):
            ref = {}
            ref['scheme'] = testXMLValue(i.attrib.get('scheme'), True)
            ref['url'] = testXMLValue(i)

            self.references.append(ref)

        val = record.find(nsp('dct:modified'))
        self.modified = testXMLValue(val)

        val = record.find(nsp('dc:creator'))
        self.creator = testXMLValue(val)

        val = record.find(nsp('dc:publisher'))
        self.publisher = testXMLValue(val)

        val = record.find(nsp('dc:coverage'))
        self.coverage = testXMLValue(val)

        val = record.find(nsp('dc:contributor'))
        self.contributor = testXMLValue(val)

        val = record.find(nsp('dc:language'))
        self.language = testXMLValue(val)

        val = record.find(nsp('dc:source'))
        self.source = testXMLValue(val)

        val = record.find(nsp('dct:rightsHolder'))
        self.rightsholder = testXMLValue(val)

        val = record.find(nsp('dct:accessRights'))
        self.accessrights = testXMLValue(val)

        val = record.find(nsp('dct:license'))
        self.license = testXMLValue(val)

        val = record.find(nsp('dc:format'))
        self.format = testXMLValue(val)

        self.subjects = []
        for i in record.findall(nsp('dc:subject')):
            self.subjects.append(testXMLValue(i))

        self.rights = []
        for i in record.findall(nsp('dc:rights')):
            self.rights.append(testXMLValue(i))

        val = record.find(nsp('dct:spatial'))
        self.spatial = testXMLValue(val)

        val = record.find(nsp_ows('ows:BoundingBox'))
        if val is not None:
            self.bbox = ows.BoundingBox(val,ns.get_versioned_namespace('ows', _ows_version))
        else:
            self.bbox = None
