#!/usr/bin/python
# -*- coding: ISO-8859-15 -*-
# =============================================================================
#
# Authors : Luca Cinquini
#
# =============================================================================

import sys
import getopt
import os
from owslib.wps import WebProcessingService

def usage():
    print  """
    
Usage: %s [parameters]

Required Parameters
-------------------

    -u, --url=[URL] the base URL of the WPS
    -r, --request=[REQUEST] the request (GetCapabilities, DescribeProcess)

Optional Parameters
-------------------

    -x, --xml=[XML] path to an XML file containing the WPS response document (for debugging, prevents invocation of actual service)
    -v, --verbose set flag for verbose output

Request Specific Parameters
---------------------------

    DescribeProcess
    -i, --identifier=[ID] process identifier (required)

Examples
--------
wps-client.py -v -u http://cida.usgs.gov/climate/gdp/process/WebProcessingService -r GetCapabilities -x ../tests/USGSCapabilities.xml
wps-client.py --verbose --url=http://cida.usgs.gov/climate/gdp/process/WebProcessingService --request=GetCapabilities --xml=../tests/USGSCapabilities.xml

wps-client.py -v -u http://cida.usgs.gov/climate/gdp/process/WebProcessingService -r DescribeProcess -x ../tests/USGSDescribeProcess.xml -i gov.usgs.cida.gdp.wps.algorithm.FeatureWeightedGridStatisticsAlgorithm
wps-client.py --verbose --url http://cida.usgs.gov/climate/gdp/process/WebProcessingService --request DescribeProcess --xml ../tests/USGSDescribeProcess.xml --identifier gov.usgs.cida.gdp.wps.algorithm.FeatureWeightedGridStatisticsAlgorithm

""" % sys.argv[0]
    
# check args
if len(sys.argv) == 1:
    usage()
    sys.exit(1)
    
print 'ARGV      :', sys.argv[1:]
    
try:
    options, remainder = getopt.getopt(sys.argv[1:], 'u:r:x:i:v', ['url=', 'request=', 'xml=', 'identifier=', 'verbose'])
except getopt.GetoptError, err:
    print str(err)
    usage()
    sys.exit(2)
    
print 'OPTIONS   :', options

url = None
request = None
identifier = None
xml = None
verbose = False

for opt, arg in options:
    if opt in ('-u', '--url'):
        url = arg
    elif opt in ('-r', '--request'):
        request = arg
    elif opt in ('-x', '--xml'):
        xml = open(arg, 'r').read()
    elif opt in ('-i', '--identifier'):
        identifier = arg
    elif opt in ('-v', '--verbose'):
        verbose = True
    else:
        assert False, 'Unhandled option'
   
# required arguments for all requests     
if request is None or url is None:
    usage()
    sys.exit(3)
        
# instantiate client
wps = WebProcessingService(url, verbose=verbose)

if request == 'GetCapabilities':
    wps.getcapabilities(xml=xml)
    
elif request == 'DescribeProcess':
    if identifier is None:
        usage()
        sys.exit(4)
    wps.describeprocess(identifier, xml=xml)