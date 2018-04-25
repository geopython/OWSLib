# Simulate a WPS GetCapabilities invocation.
# This test does not execute any live HTTP request, rather it parses XML files containing pre-made HTTP responses.

from tests.utils import resource_file
from owslib.wps import WebProcessingService


def test_wps_getcapabilities_52n():
    # Initialize WPS client
    wps = WebProcessingService(
        'http://geoprocessing.demo.52north.org:8080/52n-wps-webapp-3.3.1/WebProcessingService',
        skip_caps=True)

    # Execute fake invocation of GetCapabilities operation by parsing cached response from 52North service
    xml = open(resource_file('wps_52nCapabilities.xml'), 'rb').read()
    wps.getcapabilities(xml=xml)

    # Check WPS description
    assert wps.identification.type == 'WPS'

    # Check available operations
    operations = [op.name for op in wps.operations]
    assert operations == [
        'GetCapabilities',
        'DescribeProcess',
        'Execute']

    # Check high level process descriptions
    processes = [(p.identifier, p.title) for p in wps.processes]
    assert processes == [
        ('org.n52.wps.server.algorithm.test.MultiReferenceInputAlgorithm', 'for testing multiple inputs by reference'),
        ('org.n52.wps.server.algorithm.test.EchoProcess', 'Echo process'),
        ('org.n52.wps.server.algorithm.test.MultiReferenceBinaryInputAlgorithm', 'for testing multiple binary inputs by reference'),  # noqa
        ('org.n52.wps.server.algorithm.test.LongRunningDummyTestClass', 'org.n52.wps.server.algorithm.test.LongRunningDummyTestClass'),  # noqa
        ('org.n52.wps.server.algorithm.JTSConvexHullAlgorithm', 'org.n52.wps.server.algorithm.JTSConvexHullAlgorithm'),
        ('org.n52.wps.server.algorithm.test.MultipleComplexInAndOutputsDummyTestClass', 'org.n52.wps.server.algorithm.test.MultipleComplexInAndOutputsDummyTestClass'),  # noqa
        ('org.n52.wps.server.algorithm.test.DummyTestClass', 'org.n52.wps.server.algorithm.test.DummyTestClass')]
