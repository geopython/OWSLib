# Simulate a WPS GetCapabilities invocation.
# This test does not execute any live HTTP request, rather it parses XML files containing pre-made HTTP responses.

from tests.utils import resource_file
from owslib.wps import WebProcessingService


def test_wps_getcapabilities_ceda():
    # Initialize WPS client
    wps = WebProcessingService('http://ceda-wps2.badc.rl.ac.uk/wps', skip_caps=True)

    # Execute fake invocation of GetCapabilities operation by parsing cached response from USGS service
    xml = open(resource_file('wps_CEDACapabilities.xml'), 'rb').read()
    wps.getcapabilities(xml=xml)

    # Check WPS description
    assert wps.identification.type == 'WPS'
    assert wps.identification.title == 'WPS Pylons Test Server'
    assert wps.identification.abstract is None

    # Check available operations
    operations = [op.name for op in wps.operations]
    assert operations == [
        'GetCapabilities',
        'DescribeProcess',
        'Execute']

    # Check high level process descriptions
    processes = [(p.identifier, p.title) for p in wps.processes]
    assert processes == [
        ('CDMSSubsetVariable', 'Writes a text file and returns an output.'),
        ('NCDumpIt', 'Calls ncdump on the input file path and writes it to an output file.'),
        ('TestDap', 'Writes a text file and returns an output.'),
        ('CDMSDescribeVariableDomain', 'Writes a text file and returns an output.'),
        ('CFCheck', 'Writes a text file and returns an output.'),
        ('DoubleIt', 'Doubles the input number and returns value'),
        ('SimplePlot', 'Creates a simple map plot.'),
        ('CDMSListDatasets', 'Writes a text file and returns an output.'),
        ('CDMSListVariables', 'Writes a text file and returns an output.'),
        ('WCSWrapper', 'Web Coverage Service Wrapper Process'),
        ('GetWeatherStations', 'Writes a text file with one weather station per line'),
        ('ListPPFileHeader', 'Writes a text file that contains a listing of pp-records in a file.'),
        ('TakeAges', 'A test process to last a long time.'),
        ('CMIP5FileFinder', 'Writes a test file of matched CMIP5 files.'),
        ('SubsetPPFile', 'Filters a PP-file to generate a new subset PP-file.'),
        ('ExtractUKStationData', 'ExtractUKStationData'),
        ('CDOWrapper1', 'Writes a text file and returns an output.'),
        ('MMDNCDiff', 'MMDNCDiff'),
        ('PlotRotatedGrid', 'Creates a plot - to show we can plot a rotated grid.'),
        ('MMDAsync', 'Writes a text file and returns an output.'),
        ('MashMyDataMultiplier', 'Writes a text file and returns an output.'),
        ('Delegator', 'Writes a text file and returns an output.'),
        ('ExArchProc1', 'Writes a text file and returns an output.'),
        ('CDOShowInfo', 'Writes a text file and returns an output.'),
        ('PostTest', 'Writes a text file and returns an output.'),
        ('StatusTestProcess', 'An process to test status responses'),
        ('WaitForFileDeletionCached', 'An asynchronous job that waits for a file to be deleted'),
        ('WaitForAllFilesToBeDeleted', 'An asynchronous job that waits for a number of files to be deleted'),
        ('AsyncTest', 'Does an asynchronous test job run'),
        ('SyncTest1', 'Just creates a file.'),
        ('WaitForFileDeletion', 'An asynchronous job that waits for a file to be deleted'),
        ('ProcessTemplate', 'Writes a text file and returns an output.')]
