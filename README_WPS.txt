USER GUIDE FOR USING THE WPS CLIENT API

Abstract
--------
The wps module of the OWSlib package provides client-side functionality for executing invocations to a remote Web Processing Server.

Disclaimer
----------
PLEASE NOTE: the owslib wps module should be considered in beta state: it has been tested versus only a handful of WPS services (deployed by the USGS, BADC and PML).
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
	- identifier is the process identifier, retrieved from the list obtained from a previous "GetCapabilities" invocation
	- the optional keyword argument "xml" is used to avoid a real live request, and instead read the WPS process description document from a cached XML file
	
c) "Execute"
	- use the method wps.execute(identifier, inputs, output=None, request=None, response=None), 
	  which submits the job to the remote WPS server and returns a WPSExecution object that can be used to periodically check the job status until completion 
	  (or error)
	
	- the optional keyword argument "request" can be used to avoid re-building the request XML from input arguments, and instead submit a request from a 
	  pre-made XML file
	
	- alternatively, an "Execute" request can be built from input arguments by supplying the "identifier", "inputs" and "output" arguments to the execute() method.
		- "identifier" is the mandatory process identifier
		- "inputs" is a dictionary of (key,value) pairs where:
			- key is a named input parameter
			- value is either a string, or any python object that supports a getXml() method
			  In particular, a few classes are included in the package to support a FeatuteCollection input:
	  			- "WFSFeatureCollection" can be used in conjunction with "WFSQuery" to define a FEATURE_COLLECTION retrieved from a live WFS server.
	  			- "GMLMultiPolygonFeatureCollection" can be used to define one or more polygons of (latitude, longitude) points.
	  	- "output" is an optional output identifier to be included in the ResponseForm section of the request.
	  	
	- the optional keyword argument "response" can be used to avoid submitting a real live request, and instead read the WPS execution response document
	  from a cached XML file (for debugging or testing purposes)
	- the convenience module function monitorExecution() can be used to periodically check the status of a remote running job, and eventually download the output
	  either to a named file, or to a file specified by the server.
	  
	  
Examples
--------

The files examples/wps-usgs-script.py, examples/wps-pml-script-1.py and examples/wps-pml-script-2.py contain real-world usage examples 
that submits a "GetCapabilities", "DescribeProcess" and "Execute" requests to the live USGS and PML servers. To run: 
	cd examples
	python wps-usgs-script.py
	python wps-pml-script-1.py
	python wps-pml-script-2.py
	
The file wps-client.py contains a command-line client that can be used to submit a "GetCapabilities", "DescribeProcess" or "Execute"
request to an arbitratry WPS server. For example, you can run it as follows:
	cd examples
	To prints out usage and example invocations: wps-client -help
	To execute a (fake) WPS invocation: 
		wps-client.py -v -u http://cida.usgs.gov/climate/gdp/process/WebProcessingService -r GetCapabilities -x ../tests/USGSCapabilities.xml
	
The directory tests/ includes several doctest-style files wps_*.txt that show how to interactively submit a 
"GetCapabilities", "DescribeProcess" or "Execute" request, without making a live request but rather parsing the response of cached XML response documents. To run:
	cd tests
	python -m doctest wps_*.txt
	(or python -m doctest -v wps_*.txt for verbose output)

Also, the directory tests/ contains several examples of well-formed "Execute" requests:
	- The files USGSExecuteRequest*.xml contain requests that can be submitted to the live USGS WPS service.
	- The files PMLExecuteRequest*.xml contain requests that can be submitted to the live PML WPS service.