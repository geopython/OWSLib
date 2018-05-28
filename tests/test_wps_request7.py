# Test generation of a WPS request from input arguments.
# The specific request involves a "wordcount" process submitted to the Emu WPS service
# (https://github.com/bird-house/emu).

from tests.utils import resource_file, compare_xml
from owslib.wps import WebProcessingService, WPSExecution, ComplexDataInput
from owslib.wps import SYNC
from owslib.etree import etree


def test_wps_request7():
    # Process input/ouutput arguments
    processid = "wordcount"
    textdoc = ComplexDataInput("http://emu.readthedocs.org/en/latest/index.html")
    inputs = [("text", textdoc), ]
    outputs = [("output", True)]

    # Build XML request for WPS process execution, sync request
    execution = WPSExecution()
    requestElement = execution.buildRequest(processid, inputs, output=outputs, mode=SYNC, lineage=False)
    request = etree.tostring(requestElement)

    # Compare to cached XML request
    _request = open(resource_file('wps_EmuExecuteRequest7.xml'), 'rb').read()
    print(request)
    assert compare_xml(request, _request) is True
