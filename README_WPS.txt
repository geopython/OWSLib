USER GUIDE FOR USING THE WPS CLIENT API

Abstract
--------
The wps module of the OWSlib package provides client-side functionality for executing invocations to a remote Web Processing Server.

Disclaimer
----------
PLEASE NOTE: the owslib wps module should be considered in alpha state: it has been tested versus only one real WPS service, deployed by the USGS.
More extensive testing is needed and feedback is appreciated.

Installation (from branch)
------------

cd <YOUR WORKSPACE DIRECTORY>
svn co https://owslib.svn.sourceforge.net/svnroot/owslib/branches/wps
cd wps
(sudo) python setup.py install

Usage
-----

The module can be used to execute three types of requests versus a remote WPS endpoint: 

a) "GetCapabilities" 
	- use the method wps.getcapabilities(xml=None)
	- the optional keyword argument "xml" is used to avoid a real live request, and instead read the WPS capabilities document from a cached XML file
b) "DescribeProcess"
	- use the method wps.describeprocess(identifier, xml=None)
	- the optional keyword argument "xml" is used to avoid a real live request, and instead read the WPS process description document from a cached XML file
c) "Execute"
	- use the method wps.execute(identifier, inputs, request=None, response=None), which submits the job to the remote WPS server and returns a WPSExecution
	  object that can be used to periodically check the job status untill completion (or error)
	- the optional keyword argument "request" can be used to avoid re-building the request XML from input arguments, and instead submit a request from a 
	  pre-made XML file
	- alternatively, an "Execute" request can be built from input arguments by supplying a specific implementation of the super-class "FeatureCollection",
	  that implements the getXml() method to provide the FEATURE_COLLECTION input to the request. Currently, two such implementations are included in the
	  package:
	  	- "WFSFeatureCollection" can be used in conjunction with "WFSQuery" to define a FEATURE_COLLECTION retrieved from a live WFS server 
	  	   (see examples/wps-script.py for an example usage).
	  	- "GMLMultiPolygonFeatureCollection" can be used to define one or more polygons of (latitude, longitude) points.
	  	   (see examples/wps-script.py for an example usage).
	- the optional keyword argument "response" can be used to avoid submitting a real live request, and instead read the WPS execution response document
	  from a cached XML file (for debugging or testing purposes)
	  
	  
Examples
--------

The file examples/wps-script.py contains a real-world usage example that submits a "GetCapabilities", "DescribeProcess" and "Execute" request 
to the live USGS server. To run: 
	cd examples
	python wps-script.py
	
The file wps-client.py contains a command-line client that can be used to submit a "GetCapabilities" or "DescribeProcess" (currently not "Execute") 
request to an arbitratry WPS server. To run:
	cd examples
	wps-client.py -v -u http://cida.usgs.gov/climate/gdp/process/WebProcessingService -r GetCapabilities -x ../tests/USGSCapabilities.xml
	
The directory tests/ includes several doctest-style files wps_*.txt that show how to interactively submit a 
"GetCapabilities", "DescribeProcess" or "Execute" request, without making a live request but rather parsing the response of cached XML response documents. To run:
	cd tests
	python -m doctest wps_*.txt
	(or python -m doctest -v wps_*.txt for verbose output)

Also, the directory tests/ contains several examples of well-formed "Execute" requests (USGSExecuteRequest*.xml) that can be submitted 
to the live USGS WPS service.