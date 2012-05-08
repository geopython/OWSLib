# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2008 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@hotmail.com>
#
# Contact email: tomkralidis@hotmail.com
# =============================================================================

"""
API for OGC Web Services Common (OWS) constructs and metadata.

OWS Common: http://www.opengeospatial.org/standards/common

Currently supports version 1.1.0 (06-121r3).
"""

from owslib.etree import etree
from owslib import crs, util
from owslib.util import testXMLValue, testXMLAttribute, nspath_eval, xmltag_split

OWS_NAMESPACE_1_0_0 = 'http://www.opengis.net/ows'
OWS_NAMESPACE_1_1_0 = 'http://www.opengis.net/ows/1.1'
OWS_NAMESPACE_2_0 = 'http://www.opengis.net/ows/2.0'
DEFAULT_OWS_NAMESPACE = OWS_NAMESPACE_1_1_0

namespaces = {
    'xlink' : 'http://www.w3.org/1999/xlink',
    'xsi'   : 'http://www.w3.org/2001/XMLSchema-instance',
    'ows'   : DEFAULT_OWS_NAMESPACE
}

class OwsCommon(object):
    """Initialize OWS Common object"""
    def __init__(self,version):
        self.version = version
        if version == '1.0.0':
            self.namespace = OWS_NAMESPACE_1_0_0
        else:
            self.namespace = OWS_NAMESPACE_1_1_0
        namespaces['ows'] = self.namespace
        DEFAULT_OWS_NAMESPACE = self.namespace
    
class ServiceIdentification(object):
    """Initialize an OWS Common ServiceIdentification construct"""
    def __init__(self, infoset, namespace=DEFAULT_OWS_NAMESPACE): 
        self._root = infoset

        self.title    = testXMLValue(self._root.find(nspath_eval('ows:Title', namespaces)))
        self.abstract = testXMLValue(self._root.find(nspath_eval('ows:Abstract', namespaces)))
        self.keywords = [f.text for f in self._root.findall(nspath_eval('ows:Keywords/ows:Keyword', namespaces))]
        self.accessconstraints = testXMLValue(self._root.find(nspath_eval('ows:AccessConstraints', namespaces)))
        self.fees = testXMLValue(self._root.find(nspath_eval('ows:Fees', namespaces)))
        self.type = util.testXMLValue(self._root.find(nspath_eval('ows:ServiceType', namespaces)))
        self.service = self.type # LOOK: duplicate type as service here
        self.version = util.testXMLValue(self._root.find(nspath_eval('ows:ServiceTypeVersion', namespaces)))
        self.profile = util.testXMLValue(self._root.find(nspath_eval('ows:Profile', namespaces)))

class ServiceProvider(object):
    """Initialize an OWS Common ServiceProvider construct"""
    def __init__(self, element, namespace=DEFAULT_OWS_NAMESPACE):
        self._root = element

        self.name = testXMLValue(self._root.find(nspath_eval('ows:ProviderName', namespaces)))
        self.url = testXMLAttribute(self._root.find(nspath_eval("ows:ProviderSite", namespaces)),nspath_eval('xlink:href', namespaces))
        self.contact = ServiceContact(self._root.find(nspath_eval("ows:ServiceContact", namespaces)))

class ServiceContact(object):
    """Initialize an OWS Common ServiceContact construct"""
    def __init__(self, element, namespace=DEFAULT_OWS_NAMESPACE):
        self._root = element
        
        self.name = testXMLValue(self._root.find(nspath_eval('ows:IndividualName', namespaces)))
        self.role = testXMLValue(self._root.find(nspath_eval('ows:Role', namespaces)))
        self.position = testXMLValue(self._root.find(nspath_eval('ows:PositionName', namespaces)))
        self.email = testXMLValue(self._root.find(nspath_eval('ows:ContactInfo/ows:Address/ows:ElectronicMailAddress', namespaces)))
        self.address = testXMLValue(self._root.find(nspath_eval('ows:ContactInfo/ows:Address/ows:DeliveryPoint', namespaces)))
        self.city = testXMLValue(self._root.find(nspath_eval('ows:ContactInfo/ows:Address/ows:City', namespaces)))
        self.region = testXMLValue(self._root.find(nspath_eval('ows:ContactInfo/ows:Address/ows:AdministrativeArea', namespaces)))
        self.postcode = testXMLValue(self._root.find(nspath_eval('ows:ContactInfo/ows:Address/ows:PostalCode', namespaces)))
        self.country = testXMLValue(self._root.find(nspath_eval('ows:ContactInfo/ows:Address/ows:Country', namespaces)))
        self.city = testXMLValue(self._root.find(nspath_eval('ows:ContactInfo/ows:Address/ows:City', namespaces)))
        self.phone = testXMLValue(self._root.find(nspath_eval('ows:ContactInfo/ows:Phone/ows:Voice', namespaces)))
        self.fax = testXMLValue(self._root.find(nspath_eval('ows:ContactInfo/ows:Phone/ows:Facsimile', namespaces)))
        self.hours = testXMLValue(self._root.find(nspath_eval('ows:ContactInfo/ows:HoursOfService', namespaces)))
        self.instructions = testXMLValue(self._root.find(nspath_eval('ows:ContactInfo/ows:ContactInstructions', namespaces)))
        self.organization = testXMLValue(self._root.find(nspath_eval('ows:ContactPersonPrimary/ows:ContactOrganization', namespaces)))
        self.url = testXMLAttribute(self._root.find(nspath_eval("ows:ContactInfo/ows:nlineResource", namespaces)),nspath_eval('xlink:href', namespaces))
   
class OperationsMetadata(object):
    """Initialize an OWS OperationMetadata construct"""
    def __init__(self, element, namespace=DEFAULT_OWS_NAMESPACE):
        self._root = element

        self.name = testXMLAttribute(self._root,'name')
        self.formatOptions = ['text/xml'] # LOOK: What is this?
        
        methods = []
        for verb in self._root.findall(nspath_eval('ows:DCP/ows:HTTP/ows:*', namespaces)):
            url = testXMLAttribute(verb, nspath_eval('xlink:href', namespaces))
            methods.append((xmltag_split(verb.tag), {'url': url}))
        self.methods = dict(methods)

        # LOOK: ows:AllowedValues/ows:Value or just ows:Value
        parameters = []
        for parameter in self._root.findall(nspath_eval('ows:Parameter', namespaces)):
            parameters.append((testXMLAttribute(parameter,'name'), {'values': [i.text for i in parameter.findall(nspath_eval('ows:Value', namespaces))]}))
        self.parameters = dict(parameters)

        # LOOK: ows:AllowedValues/ows:Value or just ows:Value
        constraints = []
        for constraint in self._root.findall(nspath_eval('ows:Constraint', namespaces)):
            constraints.append((testXMLAttribute(constraint,'name'), {'values': [i.text for i in constraint.findall(nspath_eval('ows:Value', namespaces))]}))
        self.constraints = dict(constraints)

class BoundingBox(object):
    """Initialize an OWS BoundingBox construct"""
    def __init__(self, elem, namespace=DEFAULT_OWS_NAMESPACE): 
        self.minx = None
        self.miny = None
        self.maxx = None
        self.maxy = None

        val = elem.attrib.get('crs')
        if val is not None:
            self.crs = crs.Crs(val)
        else:
            self.crs = None

        val = elem.attrib.get('dimensions')
        if val is not None:
            self.dimensions = int(util.testXMLValue(val, True))
        else:  # assume 2
            self.dimensions = 2

        val = elem.find(util.nspath('LowerCorner', namespace))
        tmp = util.testXMLValue(val)
        if tmp is not None:
            xy = tmp.split()
            if len(xy) > 1:
                if self.crs is not None and self.crs.axisorder == 'yx':
                    self.minx, self.miny = xy[1], xy[0] 
                else:
                    self.minx, self.miny = xy[0], xy[1]

        val = elem.find(util.nspath('UpperCorner', namespace))
        tmp = util.testXMLValue(val)
        if tmp is not None:
            xy = tmp.split()
            if len(xy) > 1:
                if self.crs is not None and self.crs.axisorder == 'yx':
                    self.maxx, self.maxy = xy[1], xy[0]
                else:
                    self.maxx, self.maxy = xy[0], xy[1]

class ExceptionReport(Exception):
    """OWS ExceptionReport"""

    def __init__(self, elem, namespace=DEFAULT_OWS_NAMESPACE):
        self.exceptions = []
        for i in elem.findall(util.nspath('Exception', namespace)):
            tmp = {}
            val = i.attrib.get('exceptionCode')
            tmp['exceptionCode'] = util.testXMLValue(val, True)
            val = i.attrib.get('locator')
            tmp['locator'] = util.testXMLValue(val, True)
            val = i.find(util.nspath('ExceptionText', namespace))
            tmp['ExceptionText'] = util.testXMLValue(val)
            self.exceptions.append(tmp)

        # set topmost stacktrace as return message
        self.code = self.exceptions[0]['exceptionCode']
        self.locator = self.exceptions[0]['locator']
        self.msg = self.exceptions[0]['ExceptionText']
        self.xml = etree.tostring(elem.getroot())

    def __str__(self):
        return repr(self.msg)
