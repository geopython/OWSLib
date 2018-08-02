# Simulate a WPS GetCapabilities invocation.
# This test does not execute any live HTTP request, rather it parses XML files containing pre-made HTTP responses.

from tests.utils import resource_file
from owslib.wps import WebProcessingService


def test_wps_getcapabilities_usgs():
    # Initialize WPS client
    wps = WebProcessingService('http://cida.usgs.gov/gdp/process/WebProcessingService', skip_caps=True)

    # Execute fake invocation of GetCapabilities operation by parsing cached response from USGS service
    xml = open(resource_file('wps_USGSCapabilities.xml'), 'rb').read()
    wps.getcapabilities(xml=xml)

    # Check WPS description
    assert wps.updateSequence is not None
    assert wps.identification.type == 'WPS'
    assert wps.identification.title == 'Geo Data Portal WPS Implementation'
    assert wps.identification.abstract == 'A Geo Data Portal Service based on the 52north implementation of WPS 1.0.0'

    # Check available operations
    operations = [op.name for op in wps.operations]
    assert operations == [
        'GetCapabilities',
        'DescribeProcess',
        'Execute']

    # Check high level process descriptions
    processes = [(p.identifier, p.title) for p in wps.processes]
    assert processes == [
        ('gov.usgs.cida.gdp.wps.algorithm.filemanagement.ReceiveFiles', 'gov.usgs.cida.gdp.wps.algorithm.filemanagement.ReceiveFiles'),  # noqa
        ('gov.usgs.cida.gdp.wps.algorithm.discovery.CalculateWCSCoverageInfo', 'gov.usgs.cida.gdp.wps.algorithm.discovery.CalculateWCSCoverageInfo'),  # noqa
        ('gov.usgs.cida.gdp.wps.algorithm.communication.EmailWhenFinishedAlgorithm', 'gov.usgs.cida.gdp.wps.algorithm.communication.EmailWhenFinishedAlgorithm'),  # noqa
        ('gov.usgs.cida.gdp.wps.algorithm.communication.GeoserverManagementAlgorithm', 'gov.usgs.cida.gdp.wps.algorithm.communication.GeoserverManagementAlgorithm'),  # noqa
        ('gov.usgs.cida.gdp.wps.algorithm.discovery.GetWcsCoverages', 'gov.usgs.cida.gdp.wps.algorithm.discovery.GetWcsCoverages'),  # noqa
        ('gov.usgs.cida.gdp.wps.algorithm.filemanagement.GetWatersGeom', 'gov.usgs.cida.gdp.wps.algorithm.filemanagement.GetWatersGeom'),  # noqa
        ('gov.usgs.cida.gdp.wps.algorithm.discovery.ListOpendapGrids', 'gov.usgs.cida.gdp.wps.algorithm.discovery.ListOpendapGrids'),  # noqa
        ('gov.usgs.cida.gdp.wps.algorithm.filemanagement.CreateNewShapefileDataStore', 'gov.usgs.cida.gdp.wps.algorithm.filemanagement.CreateNewShapefileDataStore'),  # noqa
        ('gov.usgs.cida.gdp.wps.algorithm.discovery.GetGridTimeRange', 'gov.usgs.cida.gdp.wps.algorithm.discovery.GetGridTimeRange'),  # noqa
        ]
