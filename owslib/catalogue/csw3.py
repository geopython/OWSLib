# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2021 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

""" CSW 3.0.0 request and response processor """

import inspect
import warnings
from io import BytesIO
import random
from urllib.parse import urlencode

from owslib.etree import etree
from owslib import fes2
from owslib import util
from owslib import ows
from owslib.iso import MD_Metadata, FC_FeatureCatalogue
from owslib.fgdc import Metadata
from owslib.dif import DIF
from owslib.gm03 import GM03
from owslib.namespaces import Namespaces
from owslib.util import cleanup_namespaces, bind_url, add_namespaces, OrderedDict, Authentication, openURL, http_post

# default variables
outputformat = 'application/xml'


def get_namespaces():
    n = Namespaces()
    return n.get_namespaces()


namespaces = get_namespaces()
schema = 'http://schemas.opengis.net/cat/csw/3.0/cswAll.xsd'
schema_location = '%s %s' % (namespaces['csw30'], schema)


class CatalogueServiceWeb(object):
    """ csw request class """
    def __init__(self, url, lang='en-US', version='3.0.0', timeout=10, skip_caps=False,
                 username=None, password=None, auth=None, headers=None):
        """

        Construct and process a GetCapabilities request

        Parameters
        ----------

        - url: the URL of the CSW
        - lang: the language (default is 'en-US')
        - version: version (default is '3.0.0')
        - timeout: timeout in seconds
        - skip_caps: whether to skip GetCapabilities processing on init (default is False)
        - username: username for HTTP basic authentication
        - password: password for HTTP basic authentication
        - auth: instance of owslib.util.Authentication
        - headers: HTTP headers to send with requests

        """
        if auth:
            if username:
                auth.username = username
            if password:
                auth.password = password
        self.url = util.clean_ows_url(url)
        self.lang = lang
        self.version = version
        self.timeout = timeout
        self.auth = auth or Authentication(username, password)
        self.headers = headers
        self.service = 'CSW'
        self.exceptionreport = None
        self.owscommon = ows.OwsCommon('2.0.0')

        if not skip_caps:  # process GetCapabilities
            # construct request

            data = {'service': self.service, 'version': self.version, 'request': 'GetCapabilities'}

            self.request = urlencode(data)

            self._invoke()

            if self.exceptionreport is None:
                self.updateSequence = self._exml.getroot().attrib.get('updateSequence')

                # ServiceIdentification
                val = self._exml.find(util.nspath_eval('ows200:ServiceIdentification', namespaces))
                if val is not None:
                    self.identification = ows.ServiceIdentification(val, self.owscommon.namespace)
                else:
                    self.identification = None
                # ServiceProvider
                val = self._exml.find(util.nspath_eval('ows200:ServiceProvider', namespaces))
                if val is not None:
                    self.provider = ows.ServiceProvider(val, self.owscommon.namespace)
                else:
                    self.provider = None
                # ServiceOperations metadata
                self.operations = []
                for elem in self._exml.findall(util.nspath_eval('ows200:OperationsMetadata/ows200:Operation', namespaces)):  # noqa
                    self.operations.append(ows.OperationsMetadata(elem, self.owscommon.namespace))
                self.constraints = {}
                for elem in self._exml.findall(util.nspath_eval('ows200:OperationsMetadata/ows200:Constraint', namespaces)):  # noqa
                    self.constraints[elem.attrib['name']] = ows.Constraint(elem, self.owscommon.namespace)
                self.parameters = {}
                for elem in self._exml.findall(util.nspath_eval('ows200:OperationsMetadata/ows200:Parameter', namespaces)):  # noqa
                    self.parameters[elem.attrib['name']] = ows.Parameter(elem, self.owscommon.namespace)

                # FilterCapabilities
                val = self._exml.find(util.nspath_eval('fes:Filter_Capabilities', namespaces))
                self.filters = fes2.FilterCapabilities(val)

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
        node0 = self._setrootelement('csw30:GetDomain')
        node0.set('service', self.service)
        node0.set('version', self.version)
        node0.set(util.nspath_eval('xsi:schemaLocation', namespaces), schema_location)
        if dtype == 'property':
            dtypename = 'ValueReference'
        else:
            dtypename = 'ParameterName'

        etree.SubElement(node0, util.nspath_eval('csw30:%s' % dtypename, namespaces)).text = dname

        self.request = node0

        self._invoke()

        if self.exceptionreport is None:
            self.results = {}

            val = self._exml.find(util.nspath_eval('csw30:DomainValues', namespaces)).attrib.get('type')
            self.results['type'] = util.testXMLValue(val, True)

            val = self._exml.find(util.nspath_eval('csw30:DomainValues/csw30:%s' % dtypename, namespaces))
            self.results[dtype] = util.testXMLValue(val)

            # get the list of values associated with the Domain
            self.results['values'] = []

            for f in self._exml.findall(util.nspath_eval('csw30:DomainValues/csw30:ListOfValues/csw30:Value', namespaces)):  # noqa
                self.results['values'].append(util.testXMLValue(f))

    def getrecordbyid(self, id=[], esn='full', outputschema=namespaces['csw30'], format=outputformat):
        """

        Construct and process a GetRecordById request

        Parameters
        ----------

        - id: the list of Ids
        - esn: the ElementSetName 'full', 'brief' or 'summary' (default is 'full')
        - outputschema: the outputSchema (default is 'http://www.opengis.net/cat/csw/3.0.0')
        - format: the outputFormat (default is 'application/xml')

        """

        # construct request
        data = {
            'service': self.service,
            'version': self.version,
            'request': 'GetRecordById',
            'outputFormat': format,
            'outputSchema': outputschema,
            'elementsetname': esn,
            'id': ','.join(id),
        }

        self.request = urlencode(data)

        self._invoke()

        if self.exceptionreport is None:
            self.results = {}
            self.records = OrderedDict()
            self._parserecords(outputschema, esn)

    def getrecords(self, constraints=[], sortby=None, typenames='csw30:Record', esn='summary',
                   outputschema=namespaces['csw30'], format=outputformat, startposition=0,
                   maxrecords=10, cql=None, xml=None, distributedsearch=False, hopcount=2,
                   federatedcatalogues=[]):
        """

        Construct and process a  GetRecords request

        Parameters
        ----------

        - constraints: the list of constraints (OgcExpression from owslib.fes2 module)
        - sortby: an OGC SortBy object (SortBy from owslib.fes2 module)
        - typenames: the typeNames to query against (default is csw30:Record)
        - esn: the ElementSetName 'full', 'brief' or 'summary' (default is 'summary')
        - outputschema: the outputSchema (default is 'http://www.opengis.net/cat/csw/3.0.0')
        - format: the outputFormat (default is 'application/xml')
        - startposition: requests a slice of the result set, starting at this position (default is 0)
        - maxrecords: the maximum number of records to return. No records are returned if 0 (default is 10)
        - cql: common query language text.  Note this overrides bbox, qtype, keywords
        - xml: raw XML request.  Note this overrides all other options
        - distributedsearch: `bool` of whether to trigger distributed search
        - hopcount: number of message hops before search is terminated (default is 1)
        - federatedcatalogues: list of CSW 3 URLs

        """

        if xml is not None:
            if isinstance(xml, bytes):
                startswith_xml = xml.startswith(b'<')
            else:  # str
                startswith_xml = xml.startswith('<')

            if startswith_xml:
                self.request = etree.fromstring(xml)
                val = self.request.find(util.nspath_eval('csw30:Query/csw30:ElementSetName', namespaces))
                if val is not None:
                    esn = util.testXMLValue(val)
                val = self.request.attrib.get('outputSchema')
                if val is not None:
                    outputschema = util.testXMLValue(val, True)
            else:
                self.request = xml
        else:
            # construct request
            node0 = self._setrootelement('csw30:GetRecords')
            node0.set('outputSchema', outputschema)
            node0.set('outputFormat', format)
            node0.set('version', self.version)
            node0.set('service', self.service)
            if startposition > 0:
                node0.set('startPosition', str(startposition))
            node0.set('maxRecords', str(maxrecords))
            node0.set(util.nspath_eval('xsi:schemaLocation', namespaces), schema_location)

            if distributedsearch:
                node00 = etree.SubElement(node0, util.nspath_eval('csw30:DistributedSearch', namespaces),
                                          hopCount=str(hopcount), clientId='owslib',
                                          distributedSearchId='owslib-request')

                if federatedcatalogues:
                    for fc in federatedcatalogues:
                        etree.SubElement(node00, util.nspath_eval('csw30:federatedCatalogues', namespaces),
                                         catalogueURL=fc)

            node1 = etree.SubElement(node0, util.nspath_eval('csw30:Query', namespaces))
            node1.set('typeNames', typenames)

            etree.SubElement(node1, util.nspath_eval('csw30:ElementSetName', namespaces)).text = esn

            if any([len(constraints) > 0, cql is not None]):
                node2 = etree.SubElement(node1, util.nspath_eval('csw30:Constraint', namespaces))
                node2.set('version', '1.1.0')
                flt = fes2.FilterRequest()
                if len(constraints) > 0:
                    node2.append(flt.setConstraintList(constraints))
                # Now add a CQL filter if passed in
                elif cql is not None:
                    etree.SubElement(node2, util.nspath_eval('csw30:CqlText', namespaces)).text = cql

            if sortby is not None and isinstance(sortby, fes2.SortBy):
                node1.append(sortby.toXML())

            self.request = node0

        self._invoke()

        if self.exceptionreport is None:
            self.results = {}

            # process search results attributes
            val = self._exml.find(
                util.nspath_eval('csw30:SearchResults', namespaces)).attrib.get('numberOfRecordsMatched')
            self.results['matches'] = int(util.testXMLValue(val, True))
            val = self._exml.find(
                util.nspath_eval('csw30:SearchResults', namespaces)).attrib.get('numberOfRecordsReturned')
            self.results['returned'] = int(util.testXMLValue(val, True))
            val = self._exml.find(util.nspath_eval('csw30:SearchResults', namespaces)).attrib.get('nextRecord')
            if val is not None:
                self.results['nextrecord'] = int(util.testXMLValue(val, True))
            else:
                warnings.warn("""CSW Server did not supply a nextRecord value (it is optional), so the client
                should page through the results in another way.""")
                # For more info, see:
                # https://github.com/geopython/OWSLib/issues/100
                self.results['nextrecord'] = None

            # process list of matching records
            self.records = OrderedDict()

            self._parserecords(outputschema, esn)

    def transaction(self, ttype=None, typename='csw30:Record', record=None, propertyname=None, propertyvalue=None,
                    bbox=None, keywords=[], cql=None, identifier=None):
        """

        Construct and process a Transaction request

        Parameters
        ----------

        - ttype: the type of transaction 'insert, 'update', 'delete'
        - typename: the typename to describe (default is 'csw30:Record')
        - record: the XML record to insert
        - propertyname: the RecordProperty/PropertyName to Filter against
        - propertyvalue: the RecordProperty Value to Filter against (for updates)
        - bbox: the bounding box of the spatial query in the form [minx,miny,maxx,maxy]
        - keywords: list of keywords
        - cql: common query language text.  Note this overrides bbox, qtype, keywords
        - identifier: record identifier.  Note this overrides bbox, qtype, keywords, cql

        """

        # construct request
        node0 = self._setrootelement('csw30:Transaction')
        node0.set('version', self.version)
        node0.set('service', self.service)
        node0.set(util.nspath_eval('xsi:schemaLocation', namespaces), schema_location)

        validtransactions = ['insert', 'update', 'delete']

        if ttype not in validtransactions:  # invalid transaction
            raise RuntimeError('Invalid transaction \'%s\'.' % ttype)

        node1 = etree.SubElement(node0, util.nspath_eval('csw30:%s' % ttype.capitalize(), namespaces))

        if ttype != 'update':
            node1.set('typeName', typename)

        if ttype == 'insert':
            if record is None:
                raise RuntimeError('Nothing to insert.')
            node1.append(etree.fromstring(record))

        if ttype == 'update':
            if record is not None:
                node1.append(etree.fromstring(record))
            else:
                if propertyname is not None and propertyvalue is not None:
                    node2 = etree.SubElement(node1, util.nspath_eval('csw30:RecordProperty', namespaces))
                    etree.SubElement(node2, util.nspath_eval('csw30:Name', namespaces)).text = propertyname
                    etree.SubElement(node2, util.nspath_eval('csw30:Value', namespaces)).text = propertyvalue
                    self._setconstraint(node1, None, propertyname, keywords, bbox, cql, identifier)

        if ttype == 'delete':
            self._setconstraint(node1, None, propertyname, keywords, bbox, cql, identifier)

        self.request = node0

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
        node0 = self._setrootelement('csw30:Harvest')
        node0.set('version', self.version)
        node0.set('service', self.service)
        node0.set(util.nspath_eval('xsi:schemaLocation', namespaces), schema_location)
        etree.SubElement(node0, util.nspath_eval('csw30:Source', namespaces)).text = source
        etree.SubElement(node0, util.nspath_eval('csw30:ResourceType', namespaces)).text = resourcetype
        if resourceformat is not None:
            etree.SubElement(node0, util.nspath_eval('csw30:ResourceFormat', namespaces)).text = resourceformat
        if harvestinterval is not None:
            etree.SubElement(node0, util.nspath_eval('csw30:HarvestInterval', namespaces)).text = harvestinterval
        if responsehandler is not None:
            etree.SubElement(node0, util.nspath_eval('csw30:ResponseHandler', namespaces)).text = responsehandler

        self.request = node0

        self._invoke()
        self.results = {}

        if self.exceptionreport is None:
            val = self._exml.find(util.nspath_eval('csw30:Acknowledgement', namespaces))
            if util.testXMLValue(val) is not None:
                ts = val.attrib.get('timeStamp')
                self.timestamp = util.testXMLValue(ts, True)
                id = val.find(util.nspath_eval('csw30:RequestId', namespaces))
                self.id = util.testXMLValue(id)
            else:
                self._parsetransactionsummary()
                self._parseinsertresult()

    def get_operation_by_name(self, name):
        """Return a named operation"""
        for item in self.operations:
            if item.name.lower() == name.lower():
                return item
        raise KeyError("No operation named %s" % name)

    def getService_urls(self, service_string=None):
        """

        Return easily identifiable URLs for all service types

        Parameters
        ----------

        - service_string: a URI to lookup

        """

        urls = []
        for key, rec in list(self.records.items()):
            # create a generator object, and iterate through it until the match is found
            # if not found, gets the default value (here "none")
            url = next((d['url'] for d in rec.references if d['scheme'] == service_string), None)
            if url is not None:
                urls.append(url)
        return urls

    def _parseinsertresult(self):
        self.results['insertresults'] = []
        for i in self._exml.findall('.//' + util.nspath_eval('csw30:InsertResult', namespaces)):
            for j in i.findall(util.nspath_eval('csw30:BriefRecord/dc:identifier', namespaces)):
                self.results['insertresults'].append(util.testXMLValue(j))

    def _parserecords(self, outputschema, esn):
        if outputschema == namespaces['gmd']:  # iso 19139
            for i in self._exml.findall('.//' + util.nspath_eval('gmd:MD_Metadata', namespaces)) or \
                    self._exml.findall('.//' + util.nspath_eval('gmi:MI_Metadata', namespaces)):
                val = i.find(util.nspath_eval('gmd:fileIdentifier/gco:CharacterString', namespaces))
                identifier = self._setidentifierkey(util.testXMLValue(val))
                self.records[identifier] = MD_Metadata(i)
            for i in self._exml.findall('.//' + util.nspath_eval('gfc:FC_FeatureCatalogue', namespaces)):
                identifier = self._setidentifierkey(util.testXMLValue(i.attrib['uuid'], attrib=True))
                self.records[identifier] = FC_FeatureCatalogue(i)
        elif outputschema == namespaces['fgdc']:  # fgdc csdgm
            for i in self._exml.findall('.//metadata'):
                val = i.find('idinfo/datasetid')
                identifier = self._setidentifierkey(util.testXMLValue(val))
                self.records[identifier] = Metadata(i)
        elif outputschema == namespaces['dif']:  # nasa dif
            for i in self._exml.findall('.//' + util.nspath_eval('dif:DIF', namespaces)):
                val = i.find(util.nspath_eval('dif:Entry_ID', namespaces))
                identifier = self._setidentifierkey(util.testXMLValue(val))
                self.records[identifier] = DIF(i)
        elif outputschema == namespaces['gm03']:  # GM03
            for i in self._exml.findall('.//' + util.nspath_eval('gm03:TRANSFER', namespaces)):
                val = i.find(util.nspath_eval('gm03:fileIdentifier', namespaces))
                identifier = self._setidentifierkey(util.testXMLValue(val))
                self.records[identifier] = GM03(i)
        else:  # process default
            for i in self._exml.findall('.//' + util.nspath_eval('csw30:%s' % self._setesnel(esn), namespaces)):
                val = i.find(util.nspath_eval('dc:identifier', namespaces))
                identifier = self._setidentifierkey(util.testXMLValue(val))
                self.records[identifier] = Csw30Record(i)

    def _parsetransactionsummary(self):
        val = self._exml.find(util.nspath_eval('csw30:TransactionResponse/csw30:TransactionSummary', namespaces))
        if val is not None:
            rid = val.attrib.get('requestId')
            self.results['requestid'] = util.testXMLValue(rid, True)
            ts = val.find(util.nspath_eval('csw30:totalInserted', namespaces))
            self.results['inserted'] = int(util.testXMLValue(ts))
            ts = val.find(util.nspath_eval('csw30:totalUpdated', namespaces))
            self.results['updated'] = int(util.testXMLValue(ts))
            ts = val.find(util.nspath_eval('csw30:totalDeleted', namespaces))
            self.results['deleted'] = int(util.testXMLValue(ts))

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
            return 'owslib_random_%i' % random.randint(1, 65536)
        else:
            return el

    def _setrootelement(self, el):
        return etree.Element(util.nspath_eval(el, namespaces), nsmap=namespaces)

    def _setconstraint(self, parent, qtype=None, propertyname='csw30:AnyText', keywords=[], bbox=None, cql=None,
                       identifier=None):
        if keywords or bbox is not None or qtype is not None or cql is not None or identifier is not None:
            node0 = etree.SubElement(parent, util.nspath_eval('csw30:Constraint', namespaces))
            node0.set('version', '1.1.0')

            if identifier is not None:  # set identifier filter, overrides all other parameters
                flt = fes2.FilterRequest()
                node0.append(flt.set(identifier=identifier))
            elif cql is not None:  # send raw CQL query
                # CQL passed, overrides all other parameters
                node1 = etree.SubElement(node0, util.nspath_eval('csw30:CqlText', namespaces))
                node1.text = cql
            else:  # construct a Filter request
                flt = fes2.FilterRequest()
                node0.append(flt.set(qtype=qtype, keywords=keywords, propertyname=propertyname, bbox=bbox))

    def _invoke(self):
        # do HTTP request

        request_url = self.url

        # Get correct URL based on Operation list.

        # If skip_caps=True, then self.operations has not been set, so use
        # default URL.
        if hasattr(self, 'operations'):
            try:
                op = self.get_operation_by_name('getrecords')
                if isinstance(self.request, str):  # GET KVP
                    get_verbs = [x for x in op.methods if x.get('type').lower() == 'get']
                    request_url = get_verbs[0].get('url')
                else:
                    post_verbs = [x for x in op.methods if x.get('type').lower() == 'post']
                    if len(post_verbs) > 1:
                        # Filter by constraints.  We must match a PostEncoding of "XML"
                        for pv in post_verbs:
                            for const in pv.get('constraints'):
                                if const.name.lower() == 'postencoding':
                                    values = [v.lower() for v in const.values]
                                    if 'xml' in values:
                                        request_url = pv.get('url')
                                        break
                        else:
                            # Well, just use the first one.
                            request_url = post_verbs[0].get('url')
                    elif len(post_verbs) == 1:
                        request_url = post_verbs[0].get('url')
            except Exception:  # no such luck, just go with request_url
                pass

        if isinstance(self.request, str):  # GET KVP
            self.request = '%s%s' % (bind_url(request_url), self.request)
            headers_ = {'Accept': outputformat}
            if self.headers:
                headers_.update(self.headers)
            self.response = openURL(
                self.request, None, 'Get', timeout=self.timeout, auth=self.auth, headers=headers_
            ).read()
        else:
            self.request = cleanup_namespaces(self.request)
            # Add any namespaces used in the "typeNames" attribute of the
            # csw30:Query element to the query's xml namespaces.
            for query in self.request.findall(util.nspath_eval('csw30:Query', namespaces)):
                ns = query.get("typeNames", None)
                if ns is not None:
                    # Pull out "gmd" from something like "gmd:MD_Metadata" from the list
                    # of typenames
                    ns_keys = [x.split(':')[0] for x in ns.split(' ')]
                    self.request = add_namespaces(self.request, ns_keys)
            self.request = add_namespaces(self.request, 'fes')

            self.request = util.element_to_string(self.request, encoding='utf-8')

            self.response = http_post(request_url, self.request, self.lang, self.timeout,
                                      auth=self.auth, headers=self.headers).content

        # parse result see if it's XML
        self._exml = etree.parse(BytesIO(self.response))

        # it's XML.  Attempt to decipher whether the XML response is CSW-ish """
        valid_xpaths = [
            util.nspath_eval('ows200:ExceptionReport', namespaces),
            util.nspath_eval('csw30:Capabilities', namespaces),
            util.nspath_eval('csw30:DescribeRecordResponse', namespaces),
            util.nspath_eval('csw30:GetDomainResponse', namespaces),
            util.nspath_eval('csw30:GetRecordsResponse', namespaces),
            util.nspath_eval('csw30:GetRecordByIdResponse', namespaces),
            util.nspath_eval('csw30:HarvestResponse', namespaces),
            util.nspath_eval('csw30:TransactionResponse', namespaces),
            util.nspath_eval('csw30:Record', namespaces)
        ]

        if self._exml.getroot().tag not in valid_xpaths:
            raise RuntimeError('Document is XML, but not CSW-ish')

        # check if it's an OGC Exception
        val = self._exml.find(util.nspath_eval('ows200:Exception', namespaces))
        if val is not None:
            raise ows.ExceptionReport(self._exml, self.owscommon.namespace)
        else:
            self.exceptionreport = None


class Csw30Record(object):
    """ Process csw30:Record, csw30:BriefRecord, csw30:SummaryRecord """
    def __init__(self, record):

        if hasattr(record, 'getroot'):  # standalone document
            self.xml = etree.tostring(record.getroot())
        else:  # part of a larger document
            self.xml = etree.tostring(record)

        # check to see if Dublin Core record comes from
        # rdf:RDF/rdf:Description container
        # (child content model is identical)
        self.rdf = False
        rdf = record.find(util.nspath_eval('rdf:Description', namespaces))
        if rdf is not None:
            self.rdf = True
            record = rdf

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

        val = record.find(util.nspath_eval('dct:temporal', namespaces))
        self.temporal = util.testXMLValue(val)

        self.uris = []  # list of dicts
        for i in record.findall(util.nspath_eval('dc:URI', namespaces)):
            uri = {}
            uri['protocol'] = util.testXMLValue(i.attrib.get('protocol'), True)
            uri['name'] = util.testXMLValue(i.attrib.get('name'), True)
            uri['description'] = util.testXMLValue(i.attrib.get('description'), True)
            uri['url'] = util.testXMLValue(i)

            self.uris.append(uri)

        self.references = []  # list of dicts
        for i in record.findall(util.nspath_eval('dct:references', namespaces)):
            ref = {}
            ref['scheme'] = util.testXMLValue(i.attrib.get('scheme'), True)
            ref['url'] = util.testXMLValue(i)

            self.references.append(ref)

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

        val = record.find(util.nspath_eval('ows200:BoundingBox', namespaces))
        if val is not None:
            self.bbox = ows.BoundingBox(val, namespaces['ows'])
        else:
            self.bbox = None

        val = record.find(util.nspath_eval('ows200:WGS84BoundingBox', namespaces))
        if val is not None:
            self.bbox_wgs84 = ows.WGS84BoundingBox(val, namespaces['ows'])
        else:
            self.bbox_wgs84 = None
