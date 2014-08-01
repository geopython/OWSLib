# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2014 Pete Taylor
#
# Authors : Pete Taylor <peterataylor@gmail.com>
#
# Contact email: peterataylor@gmail.com
# =============================================================================

from owslib.util import nspath_eval, extract_time
from owslib.namespaces import Namespaces
from owslib.util import testXMLAttribute, testXMLValue

def get_namespaces():
    ns = Namespaces()
    return ns.get_namespaces(["swe20", "xlink", "sos20", "om20", "gml32",
        "xsi"])
namespaces = get_namespaces()

def nspv(path):
    return nspath_eval(path, namespaces)

class TimePeriod(object):
    ''' Basic class for gml TimePeriod '''
    def __init__(self, start, end):
        self.start = start
        self.end = end
    def __str__(self):
        return ("start: " + str(self.start) + " " +
                "end: " + str(self.end))

class OM_Observation(object):
    ''' The base OM_Observation type, of which there may be many
    specialisations, e.g. MesaurementObservation, SWE Observation, WML2 etc.
    Currently assumes that many properties are xlink only (not inline).
    '''
    def __init__(self, element):
        self.type = testXMLAttribute(element.find(nspv(
            "om20:type")), nspv("xlink:href"))

        self.featureOfInterest = testXMLAttribute(element.find(nspv(
            "om20:featureOfInterest")), nspv("xlink:href"))

        self.observedProperty = testXMLAttribute(element.find(nspv(
            "om20:observedProperty")), nspv("xlink:href"))

        self.procedure = testXMLAttribute(element.find(nspv(
            "om20:procedure")), nspv("xlink:href"))

        ''' Determine if phenom time is instant or a period. This
            depend on the type of observation -- this could be split out '''
        instant_element = element.find(nspv(
            "om20:phenomenonTime/gml32:TimeInstant"))

        if instant_element is not None:
            self.phenomenonTime = extract_time(instant_element)
        else:
            start = extract_time(element.find(nspv(
                "om20:phenomenonTime/gml32:TimePeriod/gml32:beginPosition")))
            end = extract_time(element.find(nspv(
                "om20:phenomenonTime/gml32:TimePeriod/gml32:endPosition")))
            self.phenomenonTime = TimePeriod(start, end)

        self.resultTime = extract_time(element.find(nspv(
            "om20:resultTime/gml32:TimeInstant/gml32:timePosition")))

        self.result = element.find(nspv("om20:result"))

    def get_result(self):
        ''' This will handle different result types using specialised
        observation types '''
        return self.result

class MeasurementObservation(OM_Observation):
    ''' Specialised observation type that has a measurement (value + uom)
    as result type
    '''
    def __init__(self, element):
        super(MeasurementObservation, self).__init__(element)
        self._parse_result()

    def _parse_result(self):
        ''' Parse the result property, extracting the value
        and unit of measure '''
        if self.result is not None:
            uom = testXMLAttribute(self.result, "uom")
            value_str = testXMLValue(self.result)
            try:
                value = float(value_str)
            except:
                raise ValueError("Error parsing measurement value")
            self.result = Measurement(value, uom)

    def get_result(self):
        return self.result

class Result(object): 
    ''' Base class for different OM_Observation result types '''
    def __init__(self, element):
        pass

class Measurement(Result): 
    ''' A single measurement (value + uom) '''
    def __init__(self, value, uom):
        super(Measurement, self).__init__(None)
        self.value = value
        self.uom = uom
    def __str__(self):
        return str(self.value) + "(" + self.uom + ")"
