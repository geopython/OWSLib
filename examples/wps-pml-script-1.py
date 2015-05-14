# Example script that performs a set of (small) live requests versus the live PML WPS service

from __future__ import absolute_import
from __future__ import print_function
from owslib.wps import WebProcessingService, monitorExecution

# instantiate WPS client
verbose = False
wps = WebProcessingService('http://rsg.pml.ac.uk/wps/generic.cgi', verbose=verbose, skip_caps=True)

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
process = wps.describeprocess('reprojectImage')
print('WPS Process: identifier=%s' % process.identifier)
print('WPS Process: title=%s' % process.title)
print('WPS Process: abstract=%s' % process.abstract)
for input in process.dataInputs:
    print('Process input: identifier=%s, data type=%s, minOccurs=%d, maxOccurs=%d' % (input.identifier, input.dataType, input.minOccurs, input.maxOccurs))
for output in process.processOutputs:
    print('Process output: identifier=%s, data type=%s' % (output.identifier, output.dataType))
    
# 3a) Execute
# GET request: http://rsg.pml.ac.uk/wps/generic.cgi?request=Execute&service=wps&version=1.0.0&identifier=reprojectImage&datainputs=[inputImage=http://rsg.pml.ac.uk/wps/testdata/elev_srtm_30m.img;outputSRS=EPSG:4326]&responsedocument=outputImage=@asreference=true
processid = "reprojectImage"
inputs = [ ("inputImage","http://rsg.pml.ac.uk/wps/testdata/elev_srtm_30m.img"),
           ("outputSRS", "EPSG:4326") ]
output = "outputImage"
execution = wps.execute(processid, inputs, output)

monitorExecution(execution)
        
# 3b) Execute
# GET request: http://rsg.pml.ac.uk/wps/generic.cgi?request=Execute&service=WPS&version=1.0.0&identifier=reprojectCoords&datainputs=[coords=http://rsg.pml.ac.uk/wps/testdata/coords.txt;outputSRS=EPSG:32630;inputSRS=EPSG:4326]
processid = "reprojectCoords"
inputs = [ ("coords","http://rsg.pml.ac.uk/wps/testdata/coords.txt"),
           ("outputSRS", "EPSG:32630"),
           ("inputSRS","EPSG:4326") ]
execution = wps.execute(processid, inputs)

monitorExecution(execution)
