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
from owslib import crs
from owslib.util import testXMLValue, testXMLAttribute, nspath_eval, nspath, xmltag_split, dict_union, extract_xml_list
from owslib.namespaces import OWSLibNamespaces

_ows_version = '1.0.0'

ns = OWSLibNamespaces()

def nsp(element_tag, namespace=None):
    if namespace is None:
        namespace = ns.get_versioned_namespace('ows', _ows_version)
    return nspath(element_tag, namespace=namespace)
    
class ServiceIdentification(object):
    """Initialize an OWS Common ServiceIdentification construct"""
    def __init__(self, element, namespace=None):
        self._root = element

        self.title    = testXMLValue(self._root.find(nsp('Title', namespace)))
        self.abstract = testXMLValue(self._root.find(nsp('Abstract', namespace)))
        self.keywords = extract_xml_list(self._root.findall(nsp('Keywords/Keyword', namespace)))
        self.accessconstraints = testXMLValue(self._root.find(nsp('AccessConstraints', namespace)))
        self.fees = testXMLValue(self._root.find(nsp('Fees', namespace)))
        self.type = testXMLValue(self._root.find(nsp('ServiceType', namespace)))
        self.service = self.type # LOOK: duplicate type as service here
        self.version = testXMLValue(self._root.find(nsp('ServiceTypeVersion', namespace)))
        self.profile = testXMLValue(self._root.find(nsp('Profile', namespace)))

class ServiceProvider(object):
    """Initialize an OWS Common ServiceProvider construct"""
    def __init__(self, element, namespace=None):
        self._root = element

        self.name = testXMLValue(self._root.find(nsp('ProviderName', namespace)))
        self.url = testXMLAttribute(self._root.find(nsp("ProviderSite", namespace)),nspath_eval('xlink:href'))
        self.contact = ServiceContact(self._root.find(nsp("ServiceContact", namespace)), namespace)

class ServiceContact(object):
    """Initialize an OWS Common ServiceContact construct"""
    def __init__(self, element, namespace=None):
        self._root = element
        
        self.name = testXMLValue(self._root.find(nsp('IndividualName', namespace)))
        self.role = testXMLValue(self._root.find(nsp('Role', namespace)))
        self.position = testXMLValue(self._root.find(nsp('PositionName', namespace)))
        self.email = testXMLValue(self._root.find(nsp('ContactInfo/Address/ElectronicMailAddress', namespace)))
        self.address = testXMLValue(self._root.find(nsp('ContactInfo/Address/DeliveryPoint', namespace)))
        self.city = testXMLValue(self._root.find(nsp('ContactInfo/Address/City', namespace)))
        self.region = testXMLValue(self._root.find(nsp('ContactInfo/Address/AdministrativeArea', namespace)))
        self.postcode = testXMLValue(self._root.find(nsp('ContactInfo/Address/PostalCode', namespace)))
        self.country = testXMLValue(self._root.find(nsp('ContactInfo/Address/Country', namespace)))
        self.city = testXMLValue(self._root.find(nsp('ContactInfo/Address/City', namespace)))
        self.phone = testXMLValue(self._root.find(nsp('ContactInfo/Phone/Voice', namespace)))
        self.fax = testXMLValue(self._root.find(nsp('ContactInfo/Phone/Facsimile', namespace)))
        self.hours = testXMLValue(self._root.find(nsp('ContactInfo/HoursOfService', namespace)))
        self.instructions = testXMLValue(self._root.find(nsp('ContactInfo/ContactInstructions', namespace)))
        self.organization = testXMLValue(self._root.find(nsp('ContactPersonPrimary/ContactOrganization', namespace)))
        self.url = testXMLAttribute(self._root.find(nsp("ContactInfo/OnlineResource", namespace)),nspath_eval('xlink:href'))

class Operation(object):
    """Initialize an OWS Operation construct"""
    def __init__(self, element, namespace=None):
        self._root = element

        self.name = testXMLAttribute(self._root,'name')

        methods = []
        for verb in self._root.findall(nsp('DCP/HTTP/*', namespace)):
            url = testXMLAttribute(verb, nspath_eval('xlink:href'))
            methods.append((xmltag_split(verb.tag), {'url': url}))
        self.methods = dict(methods)

        parameters = []
        for parameter in self._root.findall(nsp('Parameter', namespace)):
            parameters.append((testXMLAttribute(parameter,'name'), {'values': [i.text for i in parameter.findall('.//' + nsp('Value', namespace))]}))
        self.parameters = dict(parameters)

        constraints = []
        for constraint in self._root.findall(nsp('Constraint', namespace)):
            constraints.append((testXMLAttribute(constraint,'name'), {'values': [i.text for i in constraint.findall('.//' + nsp('Value', namespace))]}))
        self.constraints = dict(constraints)


class OperationsMetadata(object):
    """Initialize an OWS OperationMetadata construct"""
    def __init__(self, element, namespace=None):
        self._root = element

        self.operations = {}

        # There can be parent parameters and constraints

        parameters = []
        for parameter in self._root.findall(nsp('Parameter', namespace)):
            parameters.append((testXMLAttribute(parameter,'name'), {'values': [i.text for i in parameter.findall('.//' + nsp('Value', namespace))]}))
        parameters = dict(parameters)

        constraints = []
        for constraint in self._root.findall(nsp('Constraint', namespace)):
            constraints.append((testXMLAttribute(constraint,'name'), {'values': [i.text for i in constraint.findall('.//' + nsp('Value', namespace))]}))
        constraints = dict(constraints)

        for op in self._root.findall(nsp('Operation', namespace)):
            co = Operation(op, namespace)
            # Parent objects get overriden by children elements
            co.parameters = dict_union(parameters, co.parameters)
            co.constraints = dict_union(constraints, co.constraints)
            self.operations[co.name] = co



class BoundingBox(object):
    """Initialize an OWS BoundingBox construct"""
    def __init__(self, elem, namespace=None): 
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
            self.dimensions = int(testXMLValue(val, True))
        else:  # assume 2
            self.dimensions = 2

        val = elem.find(nsp('LowerCorner', namespace))
        tmp = testXMLValue(val)
        if tmp is not None:
            xy = tmp.split()
            if len(xy) > 1:
                if self.crs is not None and self.crs.axisorder == 'yx':
                    self.minx, self.miny = xy[1], xy[0] 
                else:
                    self.minx, self.miny = xy[0], xy[1]

        val = elem.find(nspath('UpperCorner', namespace))
        tmp = testXMLValue(val)
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
        self.exceptions = []

        for i in elem.findall(nsp('Exception', namespace)):
            tmp = {}
            val = i.attrib.get('exceptionCode')
            tmp['exceptionCode'] = testXMLValue(val, True)
            val = i.attrib.get('locator')
            tmp['locator'] = testXMLValue(val, True)
            val = i.find(nsp('ExceptionText', namespace))
            tmp['ExceptionText'] = testXMLValue(val)
            self.exceptions.append(tmp)

        # set topmost stacktrace as return message
        self.code = self.exceptions[0]['exceptionCode']
        self.locator = self.exceptions[0]['locator']
        self.msg = ','.join(map(lambda x: "%s - %s / %s" % (x['exceptionCode'], x['locator'], x['ExceptionText']), self.exceptions))
        self.xml = etree.tostring(elem.getroot())

    def __str__(self):
        return repr(self.msg)
