from tests.utils import resource_file
from owslib.wps import WebProcessingService, Process


def test_wps_describeprocess_emu_all():
    # Initialize WPS client
    wps = WebProcessingService('http://localhost:8094/wps', skip_caps=True)
    # Execute fake invocation of DescribeProcess operation by parsing cached response from
    xml = open(resource_file('wps_EmuDescribeProcess_all.xml'), 'rb').read()
    process = wps.describeprocess('nap', xml=xml)
    processes = wps.describeprocess('all', xml=xml)
    assert isinstance(process, Process)
    assert isinstance(processes, list)
