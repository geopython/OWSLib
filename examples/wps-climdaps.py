from owslib.wps import WebProcessingService, monitorExecution

verbose = True

# get multiple outputs
wps = WebProcessingService('http://rsg.pml.ac.uk/wps/generic.cgi', verbose=verbose)

processid = 'dummyprocess'
inputs = [("input1", '1'), ("input2", '2')]
# list of tuple (output identifier, asReference attribute)
outputs = [("output1", True), ("output2", False)]

execution = wps.execute(processid, inputs, output=outputs)
print execution.status
# show status
print 'percent complete', execution.percentCompleted
print 'status message', execution.statusMessage

monitorExecution(execution)

for output in execution.processOutputs:
    print 'identifier=%s, dataType=%s, data=%s, reference=%s' % (output.identifier, output.dataType, output.data, output.reference)

# get errors
inputs = [("input1", '1'), ("input2", '3')]
execution = wps.execute(processid, inputs, output=outputs)
monitorExecution(execution)
print execution.status
for error in execution.errors:
    print error.code, error.locator, error.text
