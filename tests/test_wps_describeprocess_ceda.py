from tests.utils import resource_file
from owslib.wps import WebProcessingService


def test_wps_describeprocess_ceda():
    # Initialize WPS client
    wps = WebProcessingService('http://ceda-wps2.badc.rl.ac.uk/wps', skip_caps=True)
    # Execute fake invocation of DescribeProcess operation by parsing cached response from CEDA service
    xml = open(resource_file('wps_CEDADescribeProcess.xml'), 'rb').read()
    process = wps.describeprocess('Doubleit', xml=xml)
    # Check process description
    assert process.identifier == 'DoubleIt'
    assert process.title == 'Doubles the input number and returns value'
    assert process.abstract == 'This is test process used to demonstrate how the WPS and the WPS User Interface work. The process accepts an integer or floating point number and returns some XML containing the input number double.'  # NOQA
    # Check process inputs
    # Example Input:
    #   identifier=NumberToDouble, title=NumberToDouble, abstract=NumberToDouble, data type=LiteralData
    #   Any value allowed
    #   Default Value: None
    #   minOccurs=1, maxOccurs=-1
    for input in process.dataInputs:
        assert input.identifier == 'NumberToDouble'
        assert input.dataType == 'LiteralData'
    # Example Output:
    #   identifier=OutputXML, title=OutputXML, abstract=OutputXML, data type=ComplexData
    #   Supported Value: mimeType=text/XML, encoding=UTF-8, schema=NONE
    #   Default Value: None
    #   reference=None, mimeType=None
    # Check process outputs
    for output in process.processOutputs:
        assert output.identifier == 'OutputXML'
        assert output.dataType == 'ComplexData'
