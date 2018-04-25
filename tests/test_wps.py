import pytest

from tests.utils import resource_file
from owslib.wps import WebProcessingService, WPSExecution


@pytest.fixture
def wps():
    '''Returns a WPS instance'''
    # Initialize WPS client
    wps = WebProcessingService('http://example.org/wps', skip_caps=True)
    xml = open(resource_file('wps_CEDACapabilities.xml'), 'rb').read()
    wps.getcapabilities(xml=xml)
    return wps


def test_wps_getOperationByName(wps):
    wps.getOperationByName("GetCapabilities")
    wps.getOperationByName("DescribeProcess")
    wps.getOperationByName("Execute")
    # Unavailable operations
    with pytest.raises(KeyError):
        wps.getOperationByName("GetStatus")


def test_wps_checkStatus():
    execution = WPSExecution()
    xml = open(resource_file('wps_PMLExecuteResponse5.xml'), 'rb').read()
    execution.checkStatus(response=xml)
    assert execution.isSucceded()
    assert execution.creationTime == '2011-11-08T21:36:55Z'
