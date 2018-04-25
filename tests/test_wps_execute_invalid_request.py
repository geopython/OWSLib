# Simulate a WPS Execute invocation with INVALID arguments.
# This test does not execute any live HTTP request, rather it parses XML files containing pre-made HTTP responses.

from tests.utils import resource_file, setup_logging
from owslib.wps import WebProcessingService


def test_wps_execute_invalid_request():
    # Initialize WPS client
    wps = WebProcessingService('http://cida.usgs.gov/gdp/process/WebProcessingService')

    # Submit fake invocation of Execute operation using cached HTTP request and response
    request = open(resource_file('wps_USGSExecuteInvalidRequest.xml'), 'rb').read()
    response = open(resource_file('wps_USGSExecuteInvalidRequestResponse.xml'), 'rb').read()
    execution = wps.execute(None, [], request=request, response=response)

    assert execution.isComplete() is True

    # Display errors
    ex = execution.errors[0]
    assert ex.code is None
    assert ex.locator is None
    assert ex.text == 'Attribute null not found in feature collection'
