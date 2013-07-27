from owslib.wps import WebProcessingService, monitorExecution

verbose = True

# get multiple outputs
wps = WebProcessingService('http://rsg.pml.ac.uk/wps/generic.cgi', verbose=verbose)

processid = 'dummyprocess'
inputs = [("input1", '1'), ("input2", '2')]
# list of tuple (output identifier, asReference attribute)
outputs = [("output1",True), ("output2",False)]

execution = wps.execute(processid, inputs, output=outputs)
print execution.status

monitorExecution(execution)

for output in execution.processOutputs:
	print 'identifier=%s, dataType=%s, data=%s, reference=%s' % (output.identifier, output.dataType, output.data, output.reference) 
