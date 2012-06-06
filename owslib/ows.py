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
from owslib.util import testXMLValue, testXMLAttribute, nspath_eval, xmltag_split, dict_union, extract_xml_list
from owslib.namespaces import OWSLibNamespaces

_ows_version = '1.0.0'

ns = OWSLibNamespaces()

def ns_ows(item):
    return nspath_eval(item,_ows_version)
    
class ServiceIdentification(object):
    """Initialize an OWS Common ServiceIdentification construct"""
    def __init__(self, infoset, ows_version='1.0.0'): 
        self._root = infoset
        global _ows_version
        _ows_version = ows_version

        self.title    = testXMLValue(self._root.find(ns_ows('ows:Title')))
        self.abstract = testXMLValue(self._root.find(ns_ows('ows:Abstract')))
        self.keywords = extract_xml_list(self._root.findall(ns_ows('ows:Keywords/ows:Keyword')))
        self.accessconstraints = testXMLValue(self._root.find(ns_ows('ows:AccessConstraints')))
        self.fees = testXMLValue(self._root.find(ns_ows('ows:Fees')))
        self.type = util.testXMLValue(self._root.find(ns_ows('ows:ServiceType')))
        self.service = self.type # LOOK: duplicate type as service here
        self.version = util.testXMLValue(self._root.find(ns_ows('ows:ServiceTypeVersion')))
        self.profile = util.testXMLValue(self._root.find(ns_ows('ows:Profile')))

class ServiceProvider(object):
    """Initialize an OWS Common ServiceProvider construct"""
    def __init__(self, element, ows_version='1.0.0'):
        self._root = element
        global _ows_version
        _ows_version = ows_version

        self.name = testXMLValue(self._root.find(ns_ows('ows:ProviderName')))
        self.url = testXMLAttribute(self._root.find(ns_ows("ows:ProviderSite")),nspath_eval('xlink:href'))
        self.contact = ServiceContact(self._root.find(ns_ows("ows:ServiceContact")),ows_version)

class ServiceContact(object):
    """Initialize an OWS Common ServiceContact construct"""
    def __init__(self, element, ows_version='1.0.0'):
        self._root = element
        global _ows_version
        _ows_version = ows_version
        
        self.name = testXMLValue(self._root.find(ns_ows('ows:IndividualName')))
        self.role = testXMLValue(self._root.find(ns_ows('ows:Role')))
        self.position = testXMLValue(self._root.find(ns_ows('ows:PositionName')))
        self.email = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:Address/ows:ElectronicMailAddress')))
        self.address = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:Address/ows:DeliveryPoint')))
        self.city = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:Address/ows:City')))
        self.region = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:Address/ows:AdministrativeArea')))
        self.postcode = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:Address/ows:PostalCode')))
        self.country = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:Address/ows:Country')))
        self.city = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:Address/ows:City')))
        self.phone = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:Phone/ows:Voice')))
        self.fax = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:Phone/ows:Facsimile')))
        self.hours = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:HoursOfService')))
        self.instructions = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:ContactInstructions')))
        self.organization = testXMLValue(self._root.find(ns_ows('ows:ContactPersonPrimary/ows:ContactOrganization')))
        self.url = testXMLAttribute(self._root.find(ns_ows("ows:ContactInfo/ows:nlineResource")),nspath_eval('xlink:href'))
   
class Operation(object):
    """Initialize an OWS Operation construct"""
    def __init__(self, element, ows_version='1.0.0'):
        self._root = element
        global _ows_version
        _ows_version = ows_version

        self.name = testXMLAttribute(self._root,'name')

        methods = []
        for verb in self._root.findall(ns_ows('ows:DCP/ows:HTTP/*')):
            url = testXMLAttribute(verb, nspath_eval('xlink:href'))
            methods.append((xmltag_split(verb.tag), {'url': url}))
        self.methods = dict(methods)

        parameters = []
        for parameter in self._root.findall(ns_ows('ows:Parameter')):
            parameters.append((testXMLAttribute(parameter,'name'), {'values': [i.text for i in parameter.findall(ns_ows('.//ows:Value'))]}))
        self.parameters = dict(parameters)

        constraints = []
        for constraint in self._root.findall(ns_ows('ows:Constraint')):
            constraints.append((testXMLAttribute(constraint,'name'), {'values': [i.text for i in constraint.findall(ns_ows('.//ows:Value'))]}))
        self.constraints = dict(constraints)


class OperationsMetadata(object):
    """Initialize an OWS OperationMetadata construct"""
    def __init__(self, element, ows_version='1.0.0'):
        self._root = element
        global _ows_version
        _ows_version = ows_version

        self.operations = {}

        # There can be parent parameters and constraints

        parameters = []
        for parameter in self._root.findall(ns_ows('ows:Parameter')):
            parameters.append((testXMLAttribute(parameter,'name'), {'values': [i.text for i in parameter.findall(ns_ows('.//ows:Value'))]}))
        parameters = dict(parameters)

        constraints = []
        for constraint in self._root.findall(ns_ows('ows:Constraint')):
            constraints.append((testXMLAttribute(constraint,'name'), {'values': [i.text for i in constraint.findall(ns_ows('.//ows:Value'))]}))
        constraints = dict(constraints)

        for op in self._root.findall(ns_ows('ows:Operation')):
            co = Operation(op, ows_version)
            # Parent objects get overriden by children elements
            co.parameters = dict_union(parameters, co.parameters)
            co.constraints = dict_union(constraints, co.constraints)
            self.operations[co.name] = co



class BoundingBox(object):
    """Initialize an OWS BoundingBox construct"""
    def __init__(self, elem, namespace=None): 
        global _ows_version
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
            
        if namespace is None:
            namespace = ns.get_versioned_namespace('ows', _ows_version)

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

    def __init__(self, elem, namespace=None):
        global _ows_version
        self.exceptions = []
        
        if namespace is None:
            namespace = ns.get_versioned_namespace('ows',_ows_version)
        
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
        self.msg = ','.join(map(lambda x: "%s - %s / %s" % (x['exceptionCode'], x['locator'], x['ExceptionText']), self.exceptions))
        self.xml = etree.tostring(elem.getroot())

    def __str__(self):
        return repr(self.msg)
