# Python doctest file to test generation of a WPS request from input arguments.
# The specific request involves a FeatureWeightedGridStatisticsAlgorithm process over a multi-polygon feature.

from tests.utils import resource_file, compare_xml
from owslib.wps import GMLMultiPolygonFeatureCollection, WebProcessingService, WPSExecution
from owslib.etree import etree


def test_wps_request3():
    # Supply process input arguments
    polygon = [(-102.8184, 39.5273), (-102.8184, 37.418), (-101.2363, 37.418),
               (-101.2363, 39.5273), (-102.8184, 39.5273)]
    featureCollection = GMLMultiPolygonFeatureCollection([polygon])
    processid = 'gov.usgs.cida.gdp.wps.algorithm.FeatureWeightedGridStatisticsAlgorithm'
    inputs = [("FEATURE_ATTRIBUTE_NAME", "the_geom"),
              ("DATASET_URI", "dods://igsarm-cida-thredds1.er.usgs.gov:8080/thredds/dodsC/dcp/conus_grid.w_meta.ncml"),
              ("DATASET_ID", "ccsm3_a1b_tmax"),
              ("TIME_START", "1960-01-01T00:00:00.000Z"),
              ("TIME_END", "1960-12-31T00:00:00.000Z"),
              ("REQUIRE_FULL_COVERAGE", "true"),
              ("DELIMITER", "COMMA"),
              ("STATISTICS", "MEAN"),
              ("STATISTICS", "MINIMUM"),
              ("STATISTICS", "MAXIMUM"),
              ("STATISTICS", "WEIGHT_SUM"),
              ("STATISTICS", "VARIANCE"),
              ("STATISTICS", "STD_DEV"),
              ("STATISTICS", "COUNT"),
              ("GROUP_BY", "STATISTIC"),
              ("SUMMARIZE_TIMESTEP", "false"),
              ("SUMMARIZE_FEATURE_ATTRIBUTE", "false"),
              ("FEATURE_COLLECTION", featureCollection)]
    output = "OUTPUT"
    # build XML request for WPS process execution
    execution = WPSExecution()
    requestElement = execution.buildRequest(processid, inputs, output=output)
    request = etree.tostring(requestElement)
    # Compare to cached XML request
    _request = open(resource_file('wps_USGSExecuteRequest3.xml'), 'rb').read()
    assert compare_xml(request, _request) is True
