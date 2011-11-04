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
from owslib import util

OWS_NAMESPACE_1_0_0 = 'http://www.opengis.net/ows'
OWS_NAMESPACE_1_1_0 = 'http://www.opengis.net/ows/1.1'
OWS_NAMESPACE_2_0 = 'http://www.opengis.net/ows/2.0'
XSI_NAMESPACE       = 'http://www.w3.org/2001/XMLSchema-instance'
XLINK_NAMESPACE     = 'http://www.w3.org/1999/xlink'

DEFAULT_OWS_NAMESPACE=OWS_NAMESPACE_1_1_0     #Use this as default for OWSCommon objects

class OwsCommon(object):
    """Initialize OWS Common object"""
    def __init__(self,version):
        self.version = version
        if version == '1.0.0':
            self.namespace = OWS_NAMESPACE_1_0_0
        else:
            self.namespace = OWS_NAMESPACE_1_1_0
    
class ServiceIdentification(object):
    """Initialize an OWS Common ServiceIdentification construct"""
    def __init__(self,infoset,namespace=DEFAULT_OWS_NAMESPACE): 
        self._root = infoset

        val = self._root.find(util.nspath('Title', namespace))
        self.title = util.testXMLValue(val)

        val = self._root.find(util.nspath('Abstract', namespace))
        self.abstract = util.testXMLValue(val)

        self.keywords = [f.text for f in self._root.findall(util.nspath('Keywords/Keyword', namespace))]

        val = self._root.find(util.nspath('AccessConstraints', namespace))
        self.accessconstraints = util.testXMLValue(val)

        val = self._root.find(util.nspath('Fees', namespace))
        self.fees = util.testXMLValue(val)

        val = self._root.find(util.nspath('ServiceType', namespace))
        self.type = util.testXMLValue(val)
        self.service=self.type #alternative? keep both?discuss

        val = self._root.find(util.nspath('ServiceTypeVersion', namespace))
        self.version = util.testXMLValue(val)

        val = self._root.find(util.nspath('Profile', namespace))
        self.profile = util.testXMLValue(val)

class ServiceProvider(object):
    """Initialize an OWS Common ServiceProvider construct"""
    def __init__(self, infoset,namespace=DEFAULT_OWS_NAMESPACE):
        self._root = infoset
        val = self._root.find(util.nspath('ProviderName', namespace))
        self.name = util.testXMLValue(val)
        self.contact = ServiceContact(infoset, namespace)
        val = self._root.find(util.nspath('ProviderSite', namespace))
        if val is not None:
            urlattrib=val.attrib[util.nspath('href', XLINK_NAMESPACE)]
            self.url = util.testXMLValue(urlattrib, True)
        else:
            self.url =None

class ServiceContact(object):
    """Initialize an OWS Common ServiceContact construct"""
    def __init__(self, infoset,namespace=DEFAULT_OWS_NAMESPACE):
        self._root = infoset
        val = self._root.find(util.nspath('ProviderName', namespace))
        self.name = util.testXMLValue(val)
        
        self.organization=util.testXMLValue(self._root.find(util.nspath('ContactPersonPrimary/ContactOrganization', namespace)))
        
        val = self._root.find(util.nspath('ProviderSite', namespace))
        if val is not None:
            self.site = util.testXMLValue(val.attrib.get(util.nspath('href', XLINK_NAMESPACE)), True)
        else:
            self.site = None

        val = self._root.find(util.nspath('ServiceContact/Role', namespace))
        self.role = util.testXMLValue(val)

        val = self._root.find(util.nspath('ServiceContact/IndividualName', namespace))
        self.name = util.testXMLValue(val)
    
        val = self._root.find(util.nspath('ServiceContact/PositionName', namespace))
        self.position = util.testXMLValue(val)
 
        val = self._root.find(util.nspath('ServiceContact/ContactInfo/Phone/Voice', namespace))
        self.phone = util.testXMLValue(val)
    
        val = self._root.find(util.nspath('ServiceContact/ContactInfo/Phone/Facsimile', namespace))
        self.fax = util.testXMLValue(val)
    
        val = self._root.find(util.nspath('ServiceContact/ContactInfo/Address/DeliveryPoint', namespace))
        self.address = util.testXMLValue(val)
    
        val = self._root.find(util.nspath('ServiceContact/ContactInfo/Address/City', namespace))
        self.city = util.testXMLValue(val)
    
        val = self._root.find(util.nspath('ServiceContact/ContactInfo/Address/AdministrativeArea', namespace))
        self.region = util.testXMLValue(val)
    
        val = self._root.find(util.nspath('ServiceContact/ContactInfo/Address/PostalCode', namespace))
        self.postcode = util.testXMLValue(val)

        val = self._root.find(util.nspath('ServiceContact/ContactInfo/Address/Country', namespace))
        self.country = util.testXMLValue(val)
    
        val = self._root.find(util.nspath('ServiceContact/ContactInfo/Address/ElectronicMailAddress', namespace))
        self.email = util.testXMLValue(val)

        val = self._root.find(util.nspath('ServiceContact/ContactInfo/OnlineResource', namespace))
        if val is not None:
            self.url = util.testXMLValue(val.attrib.get(util.nspath('href', XLINK_NAMESPACE)), True)
        else:
            self.url = None

        val = self._root.find(util.nspath('ServiceContact/ContactInfo/HoursOfService', namespace))
        self.hours = util.testXMLValue(val)
    
        val = self._root.find(util.nspath('ServiceContact/ContactInfo/ContactInstructions', namespace))
        self.instructions = util.testXMLValue(val)
   
class OperationsMetadata(object):
    """Initialize an OWS OperationMetadata construct"""
    def __init__(self,elem,namespace=DEFAULT_OWS_NAMESPACE):
        self.name = elem.attrib['name']
        self.formatOptions = ['text/xml']
        methods = []
        for verb in elem.findall(util.nspath('DCP/HTTP/*', namespace)):
            methods.append((verb.tag, {'url': verb.attrib[util.nspath('href', XLINK_NAMESPACE)]}))
        self.methods = dict(methods)

class BoundingBox(object):
    """Initialize an OWS BoundingBox construct"""
    def __init__(self, elem, namespace=DEFAULT_OWS_NAMESPACE): 
        self.minx = None
        self.miny = None
        self.maxx = None
        self.maxy = None

        val = elem.attrib.get('crs')
        self.crs = util.testXMLValue(val, True)

        val = elem.attrib.get('dimensions')
        self.dimensions = util.testXMLValue(val, True)

        val = elem.find(util.nspath('LowerCorner', namespace))
        tmp = util.testXMLValue(val)
        if tmp is not None:
            xy = tmp.split()
            if len(xy) > 1:
                self.minx, self.miny = xy[0], xy[1] 

        val = elem.find(util.nspath('UpperCorner', namespace))
        tmp = util.testXMLValue(val)
        if tmp is not None:
            xy = tmp.split()
            if len(xy) > 1:
                self.maxx, self.maxy = xy[0], xy[1]

class ExceptionReport(object):
    """Initialize an OWS ExceptionReport construct"""
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
