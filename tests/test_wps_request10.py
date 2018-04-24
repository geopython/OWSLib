# Test generation of a WPS request from input arguments.
# The specific request involves a FeatureWeightedGridStatisticsAlgorithm process over a WFS feature.

from tests.utils import resource_file, compare_xml
from owslib.wps import WPSExecution, WFSFeatureCollection, WFSQuery
from owslib.etree import etree


def test_wps_request10():
    # Supply process input arguments
    wfsUrl = "http://igsarm-cida-gdp2.er.usgs.gov:8082/geoserver/wfs"
    query = WFSQuery("sample:CONUS_States", propertyNames=['the_geom', "STATE"],
                     filters=["CONUS_States.508", "CONUS_States.469"])
    method = 'POST'
    featureCollection = WFSFeatureCollection(wfsUrl, query, wfsMethod=method)
    processid = 'gov.usgs.cida.gdp.wps.algorithm.FeatureWeightedGridStatisticsAlgorithm'
    inputs = [("FEATURE_ATTRIBUTE_NAME", "STATE"),
              ("DATASET_URI", "dods://igsarm-cida-thredds1.er.usgs.gov:8080/thredds/dodsC/dcp/conus_grid.w_meta.ncml"),
              ("DATASET_ID", "ccsm3_a1b_tmax"),
              ("DATASET_ID", "ccsm3_a1b_pr"),
              ("DATASET_ID", "ccsm3_a1fi_tmax"),
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
              ("SUMMARIZE_TIMESTEP", "true"),
              ("SUMMARIZE_FEATURE_ATTRIBUTE", "true"),
              ("FEATURE_COLLECTION", featureCollection)
              ]
    output = "OUTPUT"

    # build XML request for WPS process execution
    execution = WPSExecution()
    requestElement = execution.buildRequest(processid, inputs, output=output)
    request = etree.tostring(requestElement)

    # Compare to cached XML request
    _request = open(resource_file('wps_USGSExecuteRequest4.xml'), 'rb').read()
    assert compare_xml(request, _request) is True
