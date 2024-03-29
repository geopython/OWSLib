"""
This example calls processes on a Emu WPS: https://github.com/bird-house/emu
"""

from owslib.wps import WebProcessingService, ComplexDataInput, monitorExecution

def multiple_outputs():
    print("\nmultiple outputs ...")
    
    # get multiple outputs
    wps = WebProcessingService('http://localhost:8094/wps')

    processid = 'dummyprocess'
    inputs = [("input1", '1'), ("input2", '2')]
    # list of tuple (output identifier, asReference attribute, mimeType attribute)
    # when asReference or mimeType is None - the wps service will use its default option
    outputs = [("output1",True,'some/mime-type'), ("output2",False,None)]

    execution = wps.execute(processid, inputs, output=outputs)
    monitorExecution(execution)

    # show status
    print('percent complete', execution.percentCompleted)
    print('status message', execution.statusMessage)

    # outputs
    for output in execution.processOutputs:
        print('identifier=%s, dataType=%s, data=%s, reference=%s' % (output.identifier, output.dataType, output.data, output.reference)) 

    # errors
    print(execution.status)
    for error in execution.errors:
            print(error.code, error.locator, error.text)

def complex_input_with_reference():
    """
    use ComplexDataInput with a reference to a document
    """
    
    print("\ncomplex_input_with_reference ...")

    wps = WebProcessingService('http://localhost:8094/wps')

    processid = 'wordcount'
    textdoc = ComplexDataInput("http://www.gutenberg.org/files/28885/28885-h/28885-h.htm")   # alice in wonderland
    inputs = [("text", textdoc)]
    # list of tuple (output identifier, asReference attribute, mimeType attribute)
    # when asReference or mimeType is None - the wps service will use its default option
    outputs = [("output",True,'some/mime-type')]

    execution = wps.execute(processid, inputs, output=outputs)
    monitorExecution(execution)

    # show status
    print('percent complete', execution.percentCompleted)
    print('status message', execution.statusMessage)

    for output in execution.processOutputs:
        print('identifier=%s, dataType=%s, data=%s, reference=%s' % (output.identifier, output.dataType, output.data, output.reference)) 

def complex_input_with_content():
    """
    use ComplexDataInput with a direct content
    """
    
    print("\ncomplex_input_with_content ...")
     
    wps = WebProcessingService('http://localhost:8094/wps')

    processid = 'wordcount'
    textdoc = ComplexDataInput("ALICE was beginning to get very tired ...")   # alice in wonderland
    inputs = [("text", textdoc)]
    # list of tuple (output identifier, asReference attribute, mimeType attribute)
    # when asReference or mimeType is None - the wps service will use its default option
    outputs = [("output",True,'some/mime-type')]

    execution = wps.execute(processid, inputs, output=outputs)
    monitorExecution(execution)

    # show status
    print('percent complete', execution.percentCompleted)
    print('status message', execution.statusMessage)

    for output in execution.processOutputs:
        print('identifier=%s, dataType=%s, data=%s, reference=%s' % (output.identifier, output.dataType, output.data, output.reference)) 

        
if __name__ == '__main__':
    # call the examples ...
    multiple_outputs()
    complex_input_with_reference()
    complex_input_with_content()


