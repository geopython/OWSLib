# Test generation of a WPS request from input arguments.
# The specific request involves a "wordcount" process submitted to the Emu WPS service
# (https://github.com/bird-house/emu).

from tests.utils import resource_file, compare_xml
from owslib.wps import WebProcessingService, WPSExecution, ComplexDataInput
from owslib.wps import ASYNC
from owslib.etree import etree


def test_wps_request8():
    # Process input/ouutput arguments
    processid = "wordcount"
    textdoc = ComplexDataInput("Alice was beginning to get very tired ...")
    inputs = [("text", textdoc), ]
    outputs = [("output", True), ]

    # Build XML request for WPS process execution
    execution = WPSExecution()
    requestElement = execution.buildRequest(processid, inputs, output=outputs, mode=ASYNC, lineage=True)
    request = etree.tostring(requestElement)

    # Compare to cached XML request
    _request = open(resource_file('wps_EmuExecuteRequest8.xml'), 'rb').read()
    assert compare_xml(request, _request) is True
