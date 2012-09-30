import cgi
import pytz
from owslib.etree import etree
from datetime import datetime
from urllib import urlencode
from owslib import ows
from owslib.crs import Crs
from owslib.filter import FilterCapabilities
from owslib.util import openURL, testXMLValue, testXMLAttribute, nspath_eval, nspath, extract_time
from owslib.namespaces import OWSLibNamespaces

def nsp(text):
    return nspath_eval(text)

ns = OWSLibNamespaces()

_ows_namespace = ns.get_versioned_namespace('ows','1.1.0')

def nsp_ows(text, namespace=None):
    if namespace is None:
        namespace = _ows_namespace
    return nspath(text, namespace)

class SensorObservationService(object):
    """
        Abstraction for OGC Sensor Observation Service (SOS).

        Implements ISensorObservationService.
    """

    def __getitem__(self,id):
        ''' check contents dictionary to allow dict like access to service observational offerings'''
        if name in self.__getattribute__('contents').keys():
            return self.__getattribute__('contents')[id]
        else:
            raise KeyError, "No Observational Offering with id: %s" % id

    def __init__(self, url, version='1.0.0', xml=None, username=None, password=None):
        """Initialize."""
        self.url = url
        self.username = username
        self.password = password
        self.version = version
        self._capabilities = None

        # Authentication handled by Reader
        reader = SosCapabilitiesReader(
                version=self.version, url=self.url, username=self.username, password=self.password
                )
        if xml:  # read from stored xml
            self._capabilities = reader.read_string(xml)
        else:  # read from server
            self._capabilities = reader.read(self.url)

        # Avoid building metadata if the response is an Exception
        se = self._capabilities.find(nsp_ows('ExceptionReport'))
        if se is not None: 
            raise ows.ExceptionReport(se) 

        # build metadata objects
        self._build_metadata()

    def _build_metadata(self):
        """ 
            Set up capabilities metadata objects
        """
        # ows:ServiceIdentification metadata
        service_id_element = self._capabilities.find(nsp_ows('ServiceIdentification'))
        self.identification = ows.ServiceIdentification(service_id_element, _ows_namespace)
        
        # ows:ServiceProvider metadata
        service_provider_element = self._capabilities.find(nsp_ows('ServiceProvider'))
        self.provider = ows.ServiceProvider(service_provider_element, _ows_namespace)
            
        # ows:OperationsMetadata metadata
        op = self._capabilities.find(nsp_ows('OperationsMetadata'))
        self.operations = ows.OperationsMetadata(op, _ows_namespace).operations
          
        # sos:FilterCapabilities
        filters = self._capabilities.find(nsp('sos:Filter_Capabilities'))
        self.filters = FilterCapabilities(filters)

        # sos:Contents metadata
        self.contents = {}
        self.offerings = []
        for offering in self._capabilities.findall(nsp('sos:Contents/sos:ObservationOfferingList/sos:ObservationOffering')):
            off = SosObservationOffering(offering)
            self.contents[off.id] = off
            self.offerings.append(off)

    def describe_sensor(self,   outputFormat=None,
                                procedure=None,
                                method='Get',
                                **kwargs):

        base_url = self.get_operation_by_name('DescribeSensor').methods[method]['url']        
        request = {'service': 'SOS', 'version': self.version, 'request': 'DescribeSensor'}

        # Required Fields
        assert isinstance(outputFormat, str)
        request['outputFormat'] = outputFormat

        assert isinstance(procedure, str)
        request['procedure'] = procedure

        # Optional Fields
        if kwargs:
            for kw in kwargs:
                request[kw]=kwargs[kw]
       
        data = urlencode(request)        

        response = openURL(base_url, data, method, username=self.username, password=self.password).read()
        tr = etree.fromstring(response)

        if tr.tag == nsp_ows("ExceptionReport"):
            raise ows.ExceptionReport(etree.ElementTree(element=tr), _ows_namespace)

        return response

    def get_observation(self,   responseFormat=None,
                                offerings=None,
                                observedProperties=None,
                                eventTime=None,
                                method='Get',
                                **kwargs):
        """
        Parameters
        ----------
        format : string
            Output format. Provide one that is available for all offerings
        method : string
            Optional. HTTP DCP method name: Get or Post.  Must
        **kwargs : extra arguments
            anything else e.g. vendor specific parameters
        """

        base_url = self.get_operation_by_name('GetObservation').methods[method]['url']        
        request = {'service': 'SOS', 'version': self.version, 'request': 'GetObservation'}

        # Required Fields
        assert isinstance(offerings, list) and len(offerings) > 0
        request['offering'] = ','.join(offerings)

        assert isinstance(observedProperties, list) and len(observedProperties) > 0
        request['observedproperty'] = ','.join(observedProperties)

        assert isinstance(responseFormat, str)
        request['responseFormat'] = responseFormat


        # Optional Fields
        if eventTime is not None:
            request['eventTime'] = eventTime

        if kwargs:
            for kw in kwargs:
                request[kw]=kwargs[kw]

        data = urlencode(request)        

        response = openURL(base_url, data, method, username=self.username, password=self.password).read()
        tr = etree.fromstring(response)

        if tr.tag == nsp_ows("ExceptionReport"):
            raise ows.ExceptionReport(etree.ElementTree(element=tr), _ows_namespace)

        return response

    def get_operation_by_name(self, name): 
        """
            Return a Operation item by name, case insensitive
        """
        for item in self.operations.keys():
            if item.lower() == name.lower():
                return self.operations[item]
        raise KeyError, "No Operation named %s" % name

class SosObservationOffering(object):
    def __init__(self, element):
        self._root = element

        self.id = testXMLAttribute(self._root,nsp('gml:id'))
        self.description = testXMLValue(self._root.find(nsp('gml:description')))
        self.name = testXMLValue(self._root.find(nsp('gml:name')))
        self.srs = Crs(testXMLValue(self._root.find(nsp('gml:srsName'))))

        # LOOK: Check on GML boundedBy to make sure we handle all of the cases
        # gml:boundedBy
        try:
            envelope = self._root.find(nsp('gml:boundedBy/gml:Envelope'))
            lower_left_corner = testXMLValue(envelope.find(nsp('gml:lowerCorner'))).split(" ")
            upper_right_corner = testXMLValue(envelope.find(nsp('gml:upperCorner'))).split(" ")
            # (left, bottom, right, top) in self.bbox_srs units
            self.bbox = (float(lower_left_corner[1]), float(lower_left_corner[0]), float(upper_right_corner[1]), float(upper_right_corner[0]))
            self.bbox_srs = Crs(testXMLAttribute(envelope,'srsName'))
        except Exception:
            self.bbox = None
            self.bbox_srs = None

        # LOOK: Support all gml:TimeGeometricPrimitivePropertyType
        # Right now we are just supporting gml:TimePeriod
        # sos:Time
        begin_position_element = self._root.find(nsp('sos:time/gml:TimePeriod/gml:beginPosition'))
        self.begin_position = extract_time(begin_position_element)
        end_position_element = self._root.find(nsp('sos:time/gml:TimePeriod/gml:endPosition'))
        self.end_position = extract_time(end_position_element)

        self.result_model = testXMLValue(self._root.find(nsp('sos:resultModel')))

        self.procedures = []
        for proc in self._root.findall(nsp('sos:procedure')):
            self.procedures.append(testXMLAttribute(proc,nsp('xlink:href')))

        # LOOK: Support swe:Phenomenon here
        # this includes compound properties
        self.observed_properties = []
        for op in self._root.findall(nsp('sos:observedProperty')):
            self.observed_properties.append(testXMLAttribute(op,nsp('xlink:href')))

        self.features_of_interest = []
        for fot in self._root.findall(nsp('sos:featureOfInterest')):
            self.features_of_interest.append(testXMLAttribute(fot,nsp('xlink:href')))

        self.response_formats = []
        for rf in self._root.findall(nsp('sos:responseFormat')):
            self.response_formats.append(testXMLValue(rf))

        self.response_modes = []
        for rm in self._root.findall(nsp('sos:responseMode')):
            self.response_modes.append(testXMLValue(rm))

    def __str__(self):
        return 'Offering id: %s, name: %s' % (self.id, self.name)
        
class SosCapabilitiesReader(object):
    def __init__(self, version="1.0.0", url=None, username=None, password=None):
        self.version = version
        self.url = url
        self.username = username
        self.password = password

    def capabilities_url(self, service_url):
        """
            Return a capabilities url
        """
        qs = []
        if service_url.find('?') != -1:
            qs = cgi.parse_qsl(service_url.split('?')[1])

        params = [x[0] for x in qs]

        if 'service' not in params:
            qs.append(('service', 'SOS'))
        if 'request' not in params:
            qs.append(('request', 'GetCapabilities'))
        if 'version' not in params:
            qs.append(('version', self.version))

        urlqs = urlencode(tuple(qs))
        return service_url.split('?')[0] + '?' + urlqs

    def read(self, service_url):
        """
            Get and parse a WMS capabilities document, returning an
            elementtree instance

            service_url is the base url, to which is appended the service,
            version, and request parameters
        """
        getcaprequest = self.capabilities_url(service_url)
        spliturl=getcaprequest.split('?')
        u = openURL(spliturl[0], spliturl[1], method='Get', username=self.username, password=self.password)
        return etree.fromstring(u.read())

    def read_string(self, st):
        """
            Parse a SOS capabilities document, returning an elementtree instance

            st should be an XML capabilities document
        """
        if not isinstance(st, str):
            raise ValueError("String must be of type string, not %s" % type(st))
        return etree.fromstring(st)

