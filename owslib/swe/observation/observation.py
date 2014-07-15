from owslib.util import nspath_eval, extract_time
from owslib.namespaces import Namespaces
from owslib.util import testXMLAttribute, testXMLValue  
from owslib.swe.common import Quantity
from datetime import datetime
from dateutil import parser 

def get_namespaces():                                                                                                                                                   
     ns = Namespaces()
     return ns.get_namespaces(["swe20", "xlink", "sos20", "om20", "gml32",
         "xsi", "wml2"])
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

        # This result type check will be replaced with specialised classes
        if (len(result_element) == 0):
            result_type = testXMLAttribute(element.find(nspv(
                "om20:result")), nspv("xsi:type")) 
        else:
            result_type = list(result_element)[0].tag

        WML2_MEASUREMENT_TS = '{http://www.opengis.net/waterml/2.0}MeasurementTimeseries'
        if result_type == WML2_MEASUREMENT_TS:
            result_element = element.find(nspv("om20:result/wml2:MeasurementTimeseries"))
            self.result = MeasurementTimeseries(result_element)
        if result_type.find('MeasureType') != -1:
            uom = testXMLAttribute(element.find(nspv(
                "om20:result")), "uom") 

            value_str = testXMLValue(element.find(nspv("om20:result")))
            try:
                value = float(value_str)
            except:
                raise ValueError("Error parsing measurement value")
            self.result = Measurement(value, uom)
            # print self.result


class OMResult(object):
    def __init__(self, element):
        pass

class Measurement(OMResult):
    def __init__(self, value, uom):
        super(Measurement, self).__init__(None)
        self.value = value
        self.uom = uom
    def __str__(self):
        return str(self.value) + "(" + self.uom + ")"


class Timeseries(OMResult):
    def __init__(self, element):
        super(Timeseries, self).__init__(element)

class MeasurementTimeseries(Timeseries):
    ''' A timeseries of measurements, with per-value metadata. '''
    def __init__(self, element):
        super(MeasurementTimeseries, self).__init__(element)

        self.defaultTVPMetadata = TVPMeasurementMetadata(
                element.find(nspv("wml2:defaultPointMetadata/wml2:DefaultTVPMeasurementMetadata")))

        elems = element.findall(nspv("wml2:point"))
        self.points = []
        for point in elems:
            #print point
            self.points.append(TimeValuePair(point))

    def _parse_metadata(self, element):
        ''' Parse metadata elements relating to timeseries:
            TS: baseTime, spacing, commentBlock, parameter
            MTS: startAnchor, endAnchor, cumulative, accAnchor/Length, maxGap
        '''
        pass

        
class TimeValuePair(object):
    def __init__(self, element):
        date_str = testXMLValue(element.find(nspv(
           "wml2:MeasurementTVP/wml2:time")))
        try:
            self.time = parser.parse(date_str) 
        except:
            raise ValueError("Error parsing datetime string: %s" % date_str)

        value_str = testXMLValue(element.find(nspv(
            "wml2:MeasurementTVP/wml2:value")))
        try:
            self.value = float(value_str)
        except:
            raise ValueError("Error parsing time series point value: %" %
                    value_str)
    def __str__(self):
        return str(self.time) + "," + str(self.value)

class TVPMetadata(object):
    def __init__(self, element):
        ''' Base time-value pair metadata. Still to do:
            - relatedObservation 
        '''
        self.quality = testXMLAttribute(element.find(nspv(
            "wml2:quality")), nspv("xlink:href"))
        self.nilReason = testXMLAttribute(element.find(nspv(
            "wml2:nilReason")), nspv("xlink:href")) 
        self.comment = testXMLValue(element.find(nspv(
            "wml2:comment")))
        self.qualifier = testXMLValue(element.find(nspv(
            "wml2:qualifier")), nspv("xlink:href"))
        self.processing = testXMLValue(element.find(nspv(
            "wml2:processing")), nspv("xlink:href"))
        self.source = testXMLValue(element.find(nspv(
            "wml2:source")), nspv("xlink:href"))

class TVPMeasurementMetadata(TVPMetadata):
    ''' Measurement specific metadata. Still to do:
        - aggregationDuration
    '''
    def __init__(self, element):
        super(TVPMeasurementMetadata, self).__init__(element)
        
        self.uom = testXMLAttribute(element.find(nspv(
            "wml2:uom")), "code")
        self.interpolationType = testXMLAttribute(element.find(nspv(
            "wml2:interpolationType")), nspv("xlink:href")) 
        self.censoredReason = testXMLAttribute(element.find(nspv(
            "wml2:censoredReason")), "xlink:href")

        accuracy = testXMLValue(element.find(nspv("wml2:accuracy")))
        if accuracy is not None:
            self.accuracy = Quantity()

class MeasurementTimeseriesDomainRange(Timeseries):
    def __init__(self, element):
        super(MeasurementTimseriesDomainRange, self, element).__init__()

class SOSGetObservationResponse(object):
    ''' The base response type from SOS2.0. Container for OM_Observation
    objects.
    '''
    def __init__(self, element):
        obs_data = element.findall(nspv("sos20:observationData"))
        self.observations = [] 
        for obs in obs_data:
            self.observations.append(OM_Observation(obs.find(nspv("om20:OM_Observation"))))
