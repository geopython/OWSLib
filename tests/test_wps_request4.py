# Test generation of a WPS request from input arguments.
# The specific request involves a "reprojectImage" process submitted to the PML WPS service.

from tests.utils import resource_file, compare_xml
from owslib.wps import WebProcessingService, WPSExecution
from owslib.etree import etree


def test_wps_request4():
    # Process input/ouutput arguments
    processid = "reprojectImage"
    inputs = [("inputImage", "http://rsg.pml.ac.uk/wps/testdata/elev_srtm_30m.img"),
              ("outputSRS", "EPSG:4326")]
    output = "outputImage"

    # build XML request for WPS process execution
    execution = WPSExecution()
    requestElement = execution.buildRequest(processid, inputs, output=output)
    request = etree.tostring(requestElement)

    # Compare to cached XML request
    _request = open(resource_file('wps_PMLExecuteRequest4.xml'), 'rb').read()
    assert compare_xml(request, _request) is True
