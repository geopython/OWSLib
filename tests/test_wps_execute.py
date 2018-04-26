# Simulate a WPS Execute invocation.
# This test does not execute any live HTTP request, rather it parses XML files containing pre-made HTTP responses.

from tests.utils import resource_file, setup_logging
from owslib.wps import WebProcessingService


def test_wps_execute():
    wps = WebProcessingService('http://cida.usgs.gov/gdp/process/WebProcessingService')

    # Execute fake invocation of Execute operation using cached HTTP request and response
    request = open(resource_file('wps_USGSExecuteRequest1.xml'), 'rb').read()
    response = open(resource_file('wps_USGSExecuteResponse1a.xml'), 'rb').read()
    execution = wps.execute(None, [], request=request, response=response)
    assert execution.status == 'ProcessStarted'
    assert execution.isComplete() is False

    # Simulate end of process
    response = open(resource_file('wps_USGSExecuteResponse1b.xml'), 'rb').read()
    execution.checkStatus(sleepSecs=0, response=response)
    assert execution.status == 'ProcessSucceeded'
    assert execution.isComplete() is True

    # Display location of process output
    output = execution.processOutputs[0]
    assert output.reference == \
        'http://cida.usgs.gov/climate/gdp/process/RetrieveResultServlet?id=1318528582026OUTPUT.601bb3d0-547f-4eab-8642-7c7d2834459e'  # noqa
