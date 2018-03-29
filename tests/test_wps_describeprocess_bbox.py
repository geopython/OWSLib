from tests.utils import resource_file

from owslib.wps import WebProcessingService


def test_wps_describeprocess_bbox():
    # Initialize WPS client
    wps = WebProcessingService('http://localhost:8094/wps', skip_caps=True)
    # Execute fake invocation of DescribeProcess operation by parsing cached response from Emu service
    xml = open(resource_file('wps_bbox_DescribeProcess.xml'), 'rb').read()
    process = wps.describeprocess('bbox', xml=xml)
    # Check process description
    assert process.identifier == 'bbox'
    assert process.title == 'Bounding Box'
    # Check process inputs
    # Example Input:
    #     identifier=bbox, title=Bounding Box, abstract=None, data type=BoundingBoxData
    #     Supported Value: EPSG:4326
    #     Supported Value: EPSG:3035
    #     Default Value: EPSG:4326
    #     minOccurs=1, maxOccurs=1
    for input in process.dataInputs:
        assert input.identifier == 'bbox'
        assert input.dataType == 'BoundingBoxData'
    # Example Output:
    #    identifier=bbox, title=Bounding Box, abstract=None, data type=BoundingBoxData
    #    Supported Value: EPSG:4326
    #    Default Value: EPSG:4326
    #    reference=None, mimeType=None
    # Check process outputs
    for output in process.processOutputs:
        assert output.identifier == 'bbox'
        assert output.dataType == 'BoundingBoxData'
