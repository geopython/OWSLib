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
from datetime import datetime
from owslib.swe.observation.waterml2 import MeasurementTimeseries

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

        result_element = element.find(nspv("om20:result"))

        # O&M supports various result types. It is recommended that the type
        # be specified in the om:type field; however this is not always done. 
        # Here we check the result element to determine the type to load
        if (len(result_element) == 0):
            self.result_type = testXMLAttribute(element.find(nspv(
                "om20:result")), nspv("xsi:type"))
        else:
            self.result_type = list(result_element)[0].tag

        self.result = element.find(nspv("om20:result"))

        '''
        self.WML2_MEASUREMENT_TS = '{http://www.opengis.net/waterml/2.0}MeasurementTimeseries'
        self.WML2_MEASUREMENT_DR = '{http://www.opengis.net/waterml-dr/2.0}MeasurementTimeseriesDomainRange'

        if result_type == self.WML2_MEASUREMENT_TS:
            result_element = element.find(nspv("om20:result/wml2:MeasurementTimeseries"))
            self.result = MeasurementTimeseries(result_element)
        elif result_type.find('MeasureType') != -1:
            uom = testXMLAttribute(element.find(nspv(
                "om20:result")), "uom")
            value_str = testXMLValue(element.find(nspv("om20:result")))
            try:
                value = float(value_str)
            except:
                raise ValueError("Error parsing measurement value")
            self.result = Measurement(value, uom)'''

    def get_result(self):
        ''' This will handle different result types using specialised
        observation types ''' 
        return self.result



class OMResult(object): 
    ''' Base class for different OM_Observation result types ''' 
    def __init__(self, element): 
        pass 

class Measurement(OMResult): 
    ''' A single measurement (value + uom) ''' 
    def __init__(self, value, uom): 
        super(Measurement, self).__init__(None) 
        self.value = value 
        self.uom = uom 
    def __str__(self): 
        return str(self.value) + "(" + self.uom + ")"  
