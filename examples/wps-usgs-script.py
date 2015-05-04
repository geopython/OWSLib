# Example script that performs a set of (small) live requests versus the live USGS WPS service

from __future__ import absolute_import
from __future__ import print_function
from owslib.wps import WebProcessingService, WPSExecution, WFSFeatureCollection, WFSQuery, GMLMultiPolygonFeatureCollection, monitorExecution, printInputOutput
from owslib.util import dump

# instantiate WPS client
# setting verbose=True will print out all HTTP request and responses to standard output
verbose = False
wps = WebProcessingService('http://cida.usgs.gov/climate/gdp/process/WebProcessingService', verbose=verbose, skip_caps=True)

# 1) GetCapabilities
# Submits an HTTP GET "GetCapabilities" request to the WPS service and parses the HTTP response.

wps.getcapabilities()
# alternatively, read capabilities from XML file (no live request to WPS server)
#xml = open('../tests/USGSCapabilities.xml', 'rb').read() 
#wps.getcapabilities(xml=xml)
print('WPS Identification type: %s' % wps.identification.type)
print('WPS Identification title: %s' % wps.identification.title)
print('WPS Identification abstract: %s' % wps.identification.abstract)
for operation in wps.operations:
    print('WPS Operation: %s' % operation.name)
for process in wps.processes:
    print('WPS Process: identifier=%s title=%s' % (process.identifier, process.title))

# 2) DescribeProcess
# Submits an HTTP GET "DescribeProcess" request to the WPS service and parses the HTTP response

process = wps.describeprocess('gov.usgs.cida.gdp.wps.algorithm.FeatureWeightedGridStatisticsAlgorithm')
# alternatively, read process description from XML file (no live request to WPS server)
#xml = open('../tests/USGSDescribeProcess.xml', 'rb').read()
#process = wps.describeprocess('gov.usgs.cida.gdp.wps.algorithm.FeatureWeightedGridStatisticsAlgorithm', xml=xml)
print('WPS Process: identifier=%s' % process.identifier)
print('WPS Process: title=%s' % process.title)
print('WPS Process: abstract=%s' % process.abstract)
for input in process.dataInputs:
    print('Process input:')
    printInputOutput(input, indent='\t')
for output in process.processOutputs:
    print('Process output:')
    printInputOutput(output, indent='\t')

# 3a) Execute
# Submits an HTTP POST "Execute" process request to the WPS service, keeps checking the status of the request,
# and retrieves the output once the request terminates successfully (displaying any errors if found).
# This request uses a FEATURE_COLLECTION input obtained from a live WFS service.
#wfsUrl = "http://cida.usgs.gov/climate/gdp/proxy/http://igsarm-cida-gdp2.er.usgs.gov:8082/geoserver/wfs"
#query = WFSQuery("sample:CONUS_States", propertyNames=['the_geom',"STATE"], filters=["CONUS_States.508","CONUS_States.469"])
#featureCollection = WFSFeatureCollection(wfsUrl, query)
polygon = [(-102.8184, 39.5273), (-102.8184, 37.418), (-101.2363, 37.418), (-101.2363, 39.5273), (-102.8184, 39.5273)]
featureCollection = GMLMultiPolygonFeatureCollection( [polygon] )
processid = 'gov.usgs.cida.gdp.wps.algorithm.FeatureWeightedGridStatisticsAlgorithm'
inputs = [ ("FEATURE_ATTRIBUTE_NAME","the_geom"),
           ("DATASET_URI", "dods://cida.usgs.gov/qa/thredds/dodsC/derivatives/derivative-days_above_threshold.pr.ncml"),
           ("DATASET_ID", "ensemble_b1_pr-days_above_threshold"),
           ("TIME_START","2010-01-01T00:00:00.000Z"),
           ("TIME_END","2011-01-01T00:00:00.000Z"),
           ("REQUIRE_FULL_COVERAGE","false"),
           ("DELIMITER","COMMA"),
           ("STATISTICS","MEAN"),
           ("GROUP_BY","STATISTIC"),
           ("SUMMARIZE_TIMESTEP","false"),
           ("SUMMARIZE_FEATURE_ATTRIBUTE","false"),
           ("FEATURE_COLLECTION", featureCollection)
          ]
output = "OUTPUT"
execution = wps.execute(processid, inputs, output = "OUTPUT")
# alternatively, submit a pre-made request specified in an XML file
#request = open('../tests/wps_USGSExecuteRequest1.xml','rb').read()
#execution = wps.execute(None, [], request=request)

# The monitorExecution() function can be conveniently used to wait for the process termination
# It will eventually write the process output to the specified file, or to the file specified by the server.
monitorExecution(execution)    
'''    
# 3b) Execute
# Submits an HTTP POST "Execute" process request to the WPS service, keeps checking the status of the request,
# and retrieves the output once the request terminates successfully (displaying any errors if found).
# This request uses a FEATURE_COLLECTION input defined as a GML (lat, lon) polygon.

polygon = [(-102.8184, 39.5273), (-102.8184, 37.418), (-101.2363, 37.418), (-101.2363, 39.5273), (-102.8184, 39.5273)]
featureCollection = GMLMultiPolygonFeatureCollection( [polygon] )
processid = 'gov.usgs.cida.gdp.wps.algorithm.FeatureWeightedGridStatisticsAlgorithm'
inputs =  [ ("FEATURE_ATTRIBUTE_NAME","the_geom"),
            ("DATASET_URI", "dods://igsarm-cida-thredds1.er.usgs.gov:8080/thredds/dodsC/dcp/conus_grid.w_meta.ncml"),
            ("DATASET_ID", "ccsm3_a1b_tmax"),
            ("TIME_START","1960-01-01T00:00:00.000Z"),
            ("TIME_END","1960-12-31T00:00:00.000Z"),
            ("REQUIRE_FULL_COVERAGE","true"),
            ("DELIMITER","COMMA"),
            ("STATISTICS","MEAN"),
            ("STATISTICS","MINIMUM"),
            ("STATISTICS","MAXIMUM"),
            ("STATISTICS","WEIGHT_SUM"),
            ("STATISTICS","VARIANCE"),
            ("STATISTICS","STD_DEV"),
            ("STATISTICS","COUNT"),
            ("GROUP_BY","STATISTIC"),
            ("SUMMARIZE_TIMESTEP","false"),
            ("SUMMARIZE_FEATURE_ATTRIBUTE","false"),
            ("FEATURE_COLLECTION", featureCollection)
           ]
output = "OUTPUT"
execution = wps.execute(processid, inputs, output = "OUTPUT")
# alternatively, submit a pre-made request specified in an XML file
#request = open('../tests/wps_USGSExecuteRequest3.xml','rb').read()
#execution = wps.execute(None, [], request=request)
monitorExecution(execution)    
'''
