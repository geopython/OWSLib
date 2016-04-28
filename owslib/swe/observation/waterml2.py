# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2014 Pete Taylor
#
# Authors : Pete Taylor <peterataylor@gmail.com>
#
# Contact email: peterataylor@gmail.com
# =============================================================================
from owslib.util import nspath_eval
from owslib.namespaces import Namespaces
from owslib.util import testXMLAttribute, testXMLValue
from owslib.swe.common import Quantity
from dateutil import parser
from owslib.swe.observation.om import OM_Observation, Result


def get_namespaces():
    ns = Namespaces()
    return ns.get_namespaces(["swe20", "xlink", "sos20", "om20", "gml32",
                              "xsi", "wml2"])
namespaces = get_namespaces()


def nspv(path):
    return nspath_eval(path, namespaces)


class MeasurementTimeseriesObservation(OM_Observation):
    ''' A timeseries observation that has a measurement timeseries as
    result. An implementation of the WaterML2
    MeasurementTimeseriesObservation. '''
    def __init__(self, element):
        super(MeasurementTimeseriesObservation, self).__init__(element)
        self._parse_result()

    def _parse_result(self):
        ''' Parse the result element of the observation type '''
        if self.result is not None:
            result = self.result.find(nspv(
                     "wml2:MeasurementTimeseries"))
            self.result = MeasurementTimeseries(result)

    def get_result(self):
        return self.result


class Timeseries(Result):
    ''' Generic time-series class '''
    def __init__(self, element):
        super(Timeseries, self).__init__(element)


class MeasurementTimeseries(Timeseries):
    ''' A WaterML2.0 timeseries of measurements, with per-value metadata. '''
    def __init__(self, element):
        super(MeasurementTimeseries, self).__init__(element)

        self.defaultTVPMetadata = TVPMeasurementMetadata(element.find(
            nspv("wml2:defaultPointMetadata/wml2:DefaultTVPMeasurementMetadata")))

        elems = element.findall(nspv("wml2:point"))
        self.points = []
        for point in elems:
            self.points.append(TimeValuePair(point))

    def __iter__(self):
        for point in self.points:
            yield point

    def __len__(self):
        return len(self.points)

    def _parse_metadata(self, element):
        ''' Parse metadata elements relating to timeseries:
            TS: baseTime, spacing, commentBlock, parameter
            MTS: startAnchor, endAnchor, cumulative, accAnchor/Length, maxGap
        '''
        pass


class TimeValuePair(object):
    ''' A time-value pair as specified by WaterML2.0
        Currently no support for tvp metadata.
    '''
    def __init__(self, element):
        date_str = testXMLValue(
            element.find(nspv("wml2:MeasurementTVP/wml2:time")))
        try:
            self.datetime = parser.parse(date_str)
        except:
            raise ValueError("Error parsing datetime string: %s" % date_str)

        value_str = testXMLValue(element.find(nspv(
            "wml2:MeasurementTVP/wml2:value")))
        try:
            self.value = float(value_str)
        except:
            self.value = float('nan')

    def __str__(self):
        return str(self.datetime) + "," + str(self.value)


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
        self.qualifier = testXMLAttribute(element.find(nspv(
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
            self.accuracy = Quantity(element)


class MeasurementTimeseriesDomainRange(Timeseries):
    ''' Class to implement domain range timeseries encoding '''
    def __init__(self, element):
        super(MeasurementTimeseriesDomainRange, self, element).__init__()


class MonitoringPoint(object):
    ''' A WaterML2.0 Monitoring Point, which is a specialised O&M SamplingPoint
    '''
    def __init__(self, element):
        pass
