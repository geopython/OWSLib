# Example script that performs a set of (small) live requests versus the live CEDA WPS service

from __future__ import absolute_import
from __future__ import print_function
from owslib.wps import WebProcessingService, WPSExecution, WFSFeatureCollection, WFSQuery, GMLMultiPolygonFeatureCollection, monitorExecution, ComplexData, printInputOutput
from owslib.util import dump

verbose = True
wps = WebProcessingService('http://ceda-wps2.badc.rl.ac.uk/wps', verbose=verbose)

# 1) GetCapabilities
# GET request: http://ceda-wps2.badc.rl.ac.uk/wps?Service=WPS&Request=GetCapabilities&Format=text/xml
wps.getcapabilities()

print('WPS Identification type: %s' % wps.identification.type)
print('WPS Identification title: %s' % wps.identification.title)
print('WPS Identification abstract: %s' % wps.identification.abstract)
for operation in wps.operations:
    print('WPS Operation: %s' % operation.name)
for process in wps.processes:
    print('WPS Process: identifier=%s title=%s' % (process.identifier, process.title))
    
# 2) DescribeProcess
# GET request: http://ceda-wps2.badc.rl.ac.uk/wps?identifier=DoubleIt&version=1.0.0&request=DescribeProcess&service=WPS
process = wps.describeprocess('DoubleIt')
print('WPS Process: identifier=%s' % process.identifier)
print('WPS Process: title=%s' % process.title)
print('WPS Process: abstract=%s' % process.abstract)
for input in process.dataInputs:
    print('Process input:')
    printInputOutput(input, indent='\t')
for output in process.processOutputs:
    print('Process output:')
    printInputOutput(output, indent='\t')

# 3) Execute
# POST request:
# Note: not working, requires openid login ?
#processid = "DoubleIt"
#inputs = [ ("NumberToDouble","1") ]
#output = "OutputXML"
#execution = wps.execute(processid, inputs, output)

#monitorExecution(execution)
