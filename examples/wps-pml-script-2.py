# Example script that performs a set of (small) live requests versus the live PML WPS service

from __future__ import absolute_import
from __future__ import print_function
from owslib.wps import WebProcessingService, monitorExecution

# instantiate WPS client
verbose = False
wps = WebProcessingService('http://rsg.pml.ac.uk/wps/vector.cgi', verbose=verbose, skip_caps=True)

# 1) GetCapabilities
wps.getcapabilities()
print('WPS Identification type: %s' % wps.identification.type)
print('WPS Identification title: %s' % wps.identification.title)
print('WPS Identification abstract: %s' % wps.identification.abstract)
for operation in wps.operations:
    print('WPS Operation: %s' % operation.name)
for process in wps.processes:
    print('WPS Process: identifier=%s title=%s' % (process.identifier, process.title))
    
# 2) DescribeProcess
process = wps.describeprocess('v.net.path')
# alternatively, read process description from XML file (no live request to WPS server)
#xml = open('../tests/USGSDescribeProcess.xml', 'rb').read()
#process = wps.describeprocess('gov.usgs.cida.gdp.wps.algorithm.FeatureWeightedGridStatisticsAlgorithm', xml=xml)
print('WPS Process: identifier=%s' % process.identifier)
print('WPS Process: title=%s' % process.title)
print('WPS Process: abstract=%s' % process.abstract)
for input in process.dataInputs:
    print('Process input: identifier=%s, data type=%s, minOccurs=%d, maxOccurs=%d' % (input.identifier, input.dataType, input.minOccurs, input.maxOccurs))
for output in process.processOutputs:
    print('Process output: identifier=%s, data type=%s' % (output.identifier, output.dataType))
    
# 3) Execute
# GET request: http://rsg.pml.ac.uk/wps/vector.cgi?request=execute&service=WPS&version=1.0.0&identifier=v.net.path&datainputs=[input=http://rsg.pml.ac.uk/wps/example/graph.gml;file=1%20-960123.1421801624%204665723.56559387%20-101288.65106088226%205108200.011823481]
processid = "v.net.path"
inputs = [ ("input","http://rsg.pml.ac.uk/wps/example/graph.gml"),
           ("file","1 -960123.1421801624 4665723.56559387 -101288.65106088226 5108200.011823481")]
execution = wps.execute(processid, inputs)
monitorExecution(execution)
