# Test generation of a WPS request from input arguments.
# The specific request involves a "v.net.path" process submitted to the PML WPS service.


from tests.utils import resource_file, compare_xml
from owslib.wps import WebProcessingService, WPSExecution
from owslib.etree import etree


def test_wps_request6():
    # Process input/output arguments

    processid = "v.net.path"
    inputs = [("input", "http://rsg.pml.ac.uk/wps/example/graph.gml"),
              ("file", "1 -960123.1421801624 4665723.56559387 -101288.65106088226 5108200.011823481")]

    # Build XML request for WPS process execution
    execution = WPSExecution()
    requestElement = execution.buildRequest(processid, inputs)
    request = etree.tostring(requestElement)

    # Compare to cached XML request
    _request = open(resource_file('wps_PMLExecuteRequest6.xml'), 'rb').read()
    assert compare_xml(request, _request) is True
