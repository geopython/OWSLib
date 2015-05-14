#!/usr/bin/python
# -*- coding: ISO-8859-15 -*-
# =============================================================================
#
# Authors : Luca Cinquini
#
# =============================================================================

from __future__ import absolute_import
from __future__ import print_function
import sys
import getopt
import os
from owslib.wps import WebProcessingService, monitorExecution

def usage():
    print("""
    
Usage: %s [parameters]

Common Parameters for all request types
-------------------

    -u, --url=[URL] the base URL of the WPS - required
    -r, --request=[REQUEST] the request type (GetCapabilities, DescribeProcess, Execute) - required 
    -v, --verbose set flag for verbose output - optional (defaults to False)    

Request Specific Parameters
---------------------------

    DescribeProcess
        -i, --identifier=[ID] process identifier - required
    Execute
        -x, --xml XML file containing pre-made request to be submitted - required

Examples
--------
python wps-client.py -u http://cida.usgs.gov/climate/gdp/process/WebProcessingService -r GetCapabilities
python wps-client.py --verbose --url=http://cida.usgs.gov/climate/gdp/process/WebProcessingService --request=GetCapabilities
python wps-client.py -u http://ceda-wps2.badc.rl.ac.uk/wps -r GetCapabilities
python wps-client.py -u http://rsg.pml.ac.uk/wps/generic.cgi -r GetCapabilities
python wps-client.py -u http://rsg.pml.ac.uk/wps/vector.cgi -r GetCapabilities

python wps-client.py -u http://cida.usgs.gov/climate/gdp/process/WebProcessingService -r DescribeProcess -i gov.usgs.cida.gdp.wps.algorithm.FeatureWeightedGridStatisticsAlgorithm
python wps-client.py --verbose --url http://cida.usgs.gov/climate/gdp/process/WebProcessingService --request DescribeProcess --identifier gov.usgs.cida.gdp.wps.algorithm.FeatureWeightedGridStatisticsAlgorithm
python wps-client.py -u http://ceda-wps2.badc.rl.ac.uk/wps -r DescribeProcess -i DoubleIt
python wps-client.py -u http://rsg.pml.ac.uk/wps/generic.cgi -r DescribeProcess -i reprojectCoords
python wps-client.py -u http://rsg.pml.ac.uk/wps/vector.cgi -r DescribeProcess -i v.mkgrid

python wps-client.py -u http://cida.usgs.gov/climate/gdp/process/WebProcessingService -r Execute -x ../tests/wps_USGSExecuteRequest1.xml
python wps-client.py --verbose --url http://cida.usgs.gov/climate/gdp/process/WebProcessingService --request Execute --xml ../tests/wps_USGSExecuteRequest1.xml
python wps-client.py -u http://rsg.pml.ac.uk/wps/generic.cgi -r Execute -x ../tests/wps_PMLExecuteRequest4.xml 
python wps-client.py -u http://rsg.pml.ac.uk/wps/generic.cgi -r Execute -x ../tests/wps_PMLExecuteRequest5.xml 
python wps-client.py -u http://rsg.pml.ac.uk/wps/vector.cgi -r Execute -x ../tests/wps_PMLExecuteRequest6.xml 

""" % sys.argv[0])
    
# check args
if len(sys.argv) == 1:
    usage()
    sys.exit(1)
    
print('ARGV      :', sys.argv[1:])
    
try:
    options, remainder = getopt.getopt(sys.argv[1:], 'u:r:x:i:v', ['url=', 'request=', 'xml=', 'identifier=', 'verbose'])
except getopt.GetoptError as err:
    print(str(err))
    usage()
    sys.exit(2)
    
print('OPTIONS   :', options)

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
        xml = open(arg, 'rb').read()
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
wps = WebProcessingService(url, verbose=verbose, skip_caps=True)

if request == 'GetCapabilities':
    wps.getcapabilities()
    print('WPS Identification type: %s' % wps.identification.type)
    print('WPS Identification title: %s' % wps.identification.title)
    print('WPS Identification abstract: %s' % wps.identification.abstract)
    for operation in wps.operations:
        print('WPS Operation: %s' % operation.name)
    for process in wps.processes:
        print('WPS Process: identifier=%s title=%s' % (process.identifier, process.title))
    
elif request == 'DescribeProcess':
    if identifier is None:
        print('\nERROR: missing mandatory "-i (or --identifier)" argument')
        usage()
        sys.exit(4)
    process = wps.describeprocess(identifier)
    print('WPS Process: identifier=%s' % process.identifier)
    print('WPS Process: title=%s' % process.title)
    print('WPS Process: abstract=%s' % process.abstract)
    for input in process.dataInputs:
        print('Process input: identifier=%s, data type=%s, minOccurs=%d, maxOccurs=%d' % (input.identifier, input.dataType, input.minOccurs, input.maxOccurs))
    for output in process.processOutputs:
        print('Process output: identifier=%s, data type=%s' % (output.identifier, output.dataType))
        
elif request == 'Execute':
    if xml is None:
        print('\nERROR: missing mandatory "-x (or --xml)" argument')
        usage()
        sys.exit(5)
    execution = wps.execute(None, [], request=xml)
    monitorExecution(execution)
    
else:
    print('\nERROR: Unknown request type')
    usage()
    sys.exit(6)
