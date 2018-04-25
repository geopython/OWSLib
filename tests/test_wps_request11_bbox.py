# Test generation of a WPS request from input arguments.
# The specific request involves a "bbox" process submitted to the Emu WPS service
# (https://github.com/bird-house/emu).

from tests.utils import resource_file, compare_xml
from owslib.wps import WebProcessingService, WPSExecution, BoundingBoxDataInput
from owslib.etree import etree


def test_wps_request11_bbox():
    processid = "bbox"
    bbox = BoundingBoxDataInput([51.9, 7.0, 53.0, 8.0])
    inputs = [("bbox", bbox)]

    # Build XML request for WPS process execution
    execution = WPSExecution()
    requestElement = execution.buildRequest(processid, inputs)
    request = etree.tostring(requestElement)

    # Compare to cached XML request
    _request = open(resource_file('wps_EmuExecuteRequest11.xml'), 'rb').read()
    assert compare_xml(request, _request) is True
