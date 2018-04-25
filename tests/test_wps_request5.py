# Test generation of a WPS request from input arguments.
# The specific request involves a "reprojectCoords" process submitted to the PML WPS service.

from tests.utils import resource_file, compare_xml
from owslib.wps import WebProcessingService, WPSExecution
from owslib.etree import etree


def test_wps_request5():
    # Process input/output arguments
    processid = "reprojectCoords"
    inputs = [("coords", "http://rsg.pml.ac.uk/wps/testdata/coords.txt"),
              ("outputSRS", "EPSG:32630"),
              ("inputSRS", "EPSG:4326")]

    # build XML request for WPS process execution
    execution = WPSExecution()
    requestElement = execution.buildRequest(processid, inputs)
    request = etree.tostring(requestElement)

    # Compare to cached XML request
    _request = open(resource_file('wps_PMLExecuteRequest5.xml'), 'rb').read()
    assert compare_xml(request, _request) is True
