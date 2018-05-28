import pytest


from tests.utils import resource_file
from owslib.wps import WebProcessingService, WPSExecution, Process
from owslib.etree import etree


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


def test_wps_process_representation(wps):
    p = wps.processes[0]
    assert repr(p) == '<owslib.wps.Process CDMSSubsetVariable>'
    assert str(p) == 'WPS Process: CDMSSubsetVariable, title=Writes a text file and returns an output.'


def test_wps_process_with_invalid_identifer():
    p = Process(etree.Element('invalid'))
    assert repr(p) == '<owslib.wps.Process >'
    assert str(p) == 'WPS Process: , title='


def test_wps_response_with_lineage():
    execution = WPSExecution()
    xml = open(resource_file('wps_HummingbirdExecuteResponse1.xml'), 'rb').read()
    execution.checkStatus(response=xml)
    assert execution.isSucceded()
    assert execution.creationTime == '2018-05-08T14:00:54Z'
    # check lineage input with literal data
    inp = execution.dataInputs[0]
    assert inp.identifier == 'test'
    assert inp.title == 'Select the test you want to run.'
    assert inp.abstract == 'CF-1.6=Climate and Forecast Conventions (CF)'
    assert inp.data[0] == 'CF-1.6'
    # check lineage input with reference
    inp = execution.dataInputs[1]
    assert inp.identifier == 'dataset'
    assert inp.title == 'Upload your NetCDF file here'
    assert inp.abstract == 'or enter a URL pointing to a NetCDF file.'
    assert inp.reference.startswith('https://www.esrl.noaa.gov/')
    # check output with reference
    outp = execution.processOutputs[0]
    assert outp.identifier == 'output'
    assert outp.title == 'Test Report'
    assert outp.abstract == 'Compliance checker test report.'
    assert outp.reference.startswith('http://localhost:8090/wpsoutputs')
