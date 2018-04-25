# Test generation of a WPS request from input arguments.
# The specific request involves a "helloworld" process submitted to the Emu WPS service
# (https://github.com/bird-house/emu).

from tests.utils import resource_file, compare_xml
from owslib.wps import WebProcessingService, WPSExecution, ComplexDataInput
from owslib.etree import etree


def test_wps_request9():
    # Process input/output arguments
    processid = "helloworld"
    inputs = [("user", 'Pingu')]

    # Build XML request for WPS process execution
    execution = WPSExecution()
    requestElement = execution.buildRequest(processid, inputs)
    request = etree.tostring(requestElement)

    # Compare to cached XML request
    _request = open(resource_file('wps_EmuExecuteRequest9.xml'), 'rb').read()
    assert compare_xml(request, _request) is True
