USER GUIDE FOR USING THE WPS CLIENT API

Abstract
--------
The wps module of the OWSlib package provides client-side functionality for executing invocations to a remote Web Processing Server.

Disclaimer
----------
PLEASE NOTE: this module is in alpha state - more extensive testing is needed versus other WPS servers and processes.

Usage
-----

1) Inspect a WPS capabilities:

>>> from owslib.wps import WebProcessingService
>>> wps = WebProcessingService('http://cida.usgs.gov/climate/gdp/process/WebProcessingService')
>>> wps.getcapabilities()
>>> wps.identification.type
'WPS'
>>> wps.identification.title
'Geo Data Portal WPS Processing'
>>> wps.identification.abstract
'Geo Data Portal WPS Processing'

>>> for operation in wps.operations:
...     operation.name
... 
'GetCapabilities'
'DescribeProcess'
'Execute'

>>> for process in wps.processes:
...     process.title, process.identifier
... 
('Feature Coverage WCS Intersection', 'gov.usgs.cida.gdp.wps.algorithm.FeatureCoverageIntersectionAlgorithm')
('Feature Coverage OPeNDAP Intersection', 'gov.usgs.cida.gdp.wps.algorithm.FeatureCoverageOPeNDAPIntersectionAlgorithm')
('Feature Categorical Grid Coverage', 'gov.usgs.cida.gdp.wps.algorithm.FeatureCategoricalGridCoverageAlgorithm')
('Feature Weighted Grid Statistics', 'gov.usgs.cida.gdp.wps.algorithm.FeatureWeightedGridStatisticsAlgorithm')


2) Inspect a given WPS process:

>>> p = wps.describeprocess('gov.usgs.cida.gdp.wps.algorithm.FeatureWeightedGridStatisticsAlgorithm')

>>> p.identifier
'gov.usgs.cida.gdp.wps.algorithm.FeatureWeightedGridStatisticsAlgorithm'
>>> p.title
'Feature Weighted Grid Statistics'
>>> p.abstract
'This algorithm generates area weighted statistics of a gridded dataset are generated for cells in the retrieved grid....'

>>> for input in p.dataInputs:
...     input.identifier, input.title, input.dataType, input.minOccurs, input.maxOccurs
... 
('FEATURE_COLLECTION', 'Feature Collection', 'ComplexData', 1, 1)
('DATASET_URI', 'Dataset URI', 'anyURI', 1, 1)
('DATASET_ID', 'Dataset Identifier', 'string', 1, 2147483647)
('REQUIRE_FULL_COVERAGE', 'Require Full Coverage', 'boolean', 1, 1)
('TIME_START', 'Time Start', 'dateTime', 0, 1)
('TIME_END', 'Time End', 'dateTime', 0, 1)
('FEATURE_ATTRIBUTE_NAME', 'Feature Attribute Name', 'string', 1, 1)
('DELIMITER', 'Delimiter', 'string', 1, 1)
('STATISTICS', 'Statistics', 'string', 1, 7)
('GROUP_BY', 'Group By', 'string', 1, 1)
('SUMMARIZE_TIMESTEP', 'Summarize Timestep', 'boolean', 0, 1)
('SUMMARIZE_FEATURE_ATTRIBUTE', 'Summarize Feature Attribute', 'boolean', 0, 1)

>>> for output in p.processOutputs:
...     output.identifier, output.title, output.dataType
... 
('OUTPUT', 'Output File', 'ComplexData')

3) Request execution of a WPS process:

3a) submit a request from a pre-built XML file:
(process and inputs are defined in the XML file)

>>> processid = None
>>> inputs = []
>>> request = open('tests/USGSExecuteRequest1.xml','r').read()
>>> execution = wps.execute(processid, inputs, request=request)
>>> while execution.isComplete()==False:
...     execution.checkStatus(sleepSecs=3)
... 
>>> execution.isComplete()
True
>>> execution.getOutput(filepath='/tmp/output.csv')
Output written to file: /tmp/output.csv

3b) submit a request via command-line inputs:

'''
>>> from owslib.wps import WFSFeatureCollection
>>> processid = 'gov.usgs.cida.gdp.wps.algorithm.FeatureWeightedGridStatisticsAlgorithm'
>>> wfsUrl = "http://igsarm-cida-gdp2.er.usgs.gov:8082/geoserver/wfs"
>>> query = Query("sample:CONUS_States", propertyNames=['the_geom',"STATE"], filters=["CONUS_States.508","CONUS_States.469"])
>>> featureCollection = WFSFeatureCollection(wfsUrl, query)

>>> inputs = [ ("FEATURE_ATTRIBUTE_NAME","STATE"),
...            ("DATASET_URI","dods://igsarm-cida-thredds1.er.usgs.gov:8080/thredds/dodsC/dcp/conus_grid.w_meta.ncml"),
...            ("DATASET_ID","ccsm3_a1b_tmax"),           
...            #("DATASET_URI","dods://hydra.fsl.noaa.gov/thredds/dodsC/oc_gis_downscaling/sresb1/ncar_ccsm3_0.1/Prcp/ncar_ccsm3_0.1.sresb1.monthly.Prcp.1950.nc"),
...            #("DATASET_ID","Prcp"),
...            ("TIME_START","1960-01-01T00:00:00.000Z"),
...            ("TIME_END","1960-12-31T00:00:00.000Z"),
...            ("REQUIRE_FULL_COVERAGE","true"),
...            ("DELIMITER","COMMA"),
...            ("STATISTICS","MEAN"),
...            ("STATISTICS","MINIMUM"),
...            ("STATISTICS","MAXIMUM"),
...            ("STATISTICS","WEIGHT_SUM"),
...            ("STATISTICS","VARIANCE"),
...            ("STATISTICS","STD_DEV"),
...            ("STATISTICS","COUNT"),
...            ("GROUP_BY","STATISTIC"),
...            ("SUMMARIZE_TIMESTEP","true"),
...            ("SUMMARIZE_FEATURE_ATTRIBUTE","true"),
...            ("FEATURE_COLLECTION", featureCollection)
...           ]
>>> execution = wps.execute(processid, inputs)
>>> while execution.isComplete()==False:
...     execution.checkStatus(sleepSecs=3)
... 
>>> execution.isComplete()
True
>>> execution.status
>>> execution.getOutput(filepath='/tmp/output.csv')
Output written to file: /tmp/output.csv

3ab) In case there are exceptions:
>>> execution.status
'Exception'
>>> for exception in execution.errors:
...     exception.code, exception.text
... 
('InvalidParameterValue', 'Specified process identifier does not exist')
('JAVA_StackTrace', 'org.n52.wps.server.request.ExecuteRequest.validate:414\norg.n52.wps.server.request.ExecuteRequest.<init>:109\norg.n52.wps.server.handler.RequestHandler.<init>:228\norg.n52.wps.server.WebProcessingService.doPost:277\njavax.servlet.http.HttpServlet.service:637\norg.n52.wps.server.WebProcessingService.service:300\njavax.servlet.http.HttpServlet.service:717\norg.apache.catalina.core.ApplicationFilterChain.internalDoFilter:290\norg.apache.catalina.core.ApplicationFilterChain.doFilter:206\ngov.usgs.cida.gdp.servlet.ResponseURLFilter.doFilter:49\norg.apache.catalina.core.ApplicationFilterChain.internalDoFilter:235\norg.apache.catalina.core.ApplicationFilterChain.doFilter:206\norg.apache.catalina.core.StandardWrapperValve.invoke:233\norg.apache.catalina.core.StandardContextValve.invoke:191\norg.apache.catalina.core.StandardHostValve.invoke:127\norg.apache.catalina.valves.ErrorReportValve.invoke:102\norg.apache.catalina.core.StandardEngineValve.invoke:109\norg.apache.catalina.connector.CoyoteAdapter.service:298\norg.apache.coyote.http11.Http11AprProcessor.process:861\norg.apache.coyote.http11.Http11AprProtocol$Http11ConnectionHandler.process:579\norg.apache.tomcat.util.net.AprEndpoint$SocketWithOptionsProcessor.run:2056\njava.util.concurrent.ThreadPoolExecutor$Worker.runTask:886\njava.util.concurrent.ThreadPoolExecutor$Worker.run:908\njava.lang.Thread.run:619\n')
('JAVA_RootCause', '')


