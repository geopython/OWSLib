# SOS version 2.0 tests on http://www.bom.gov.au/waterdata/services

from owslib.sos import SensorObservationService

from tests.utils import service_ok
import pytest

SERVICE_URL = 'http://www.bom.gov.au/waterdata/services'


@pytest.mark.online
@pytest.mark.skip('service responds with an exception (#496)')
@pytest.mark.skipif(not service_ok(SERVICE_URL + "?service=SOS&request=GetCapabilities"),
                    reason="SOS service is unreachable")
def test_sos_20_bom_gov_au():
    # Setup
    service = SensorObservationService(SERVICE_URL, version='2.0.0')
    id = service.identification
    # Check basic service metadata
    assert id.service == 'SOS'
    assert id.title == 'KISTERS KiWIS SOS2'
    assert id.keywords == []
    assert service.provider.name == 'Provider Name'
    assert service.provider.contact.name == 'Name'
    assert service.provider.contact.position is None
    assert len(service.operations) == 5
    assert service.get_operation_by_name('GetObservation').methods[0]['url'] == \
        'http://bom.gov.au/waterdata/services?datasource=0'
    response = service.get_observation(
        featureOfInterest='http://bom.gov.au/waterdata/services/stations/181.1',
        offerings=['http://bom.gov.au/waterdata/services/tstypes/Pat4_PC_1'],
        observedProperties=['http://bom.gov.au/waterdata/services/parameters/Water Course Discharge'],
        eventTime='om:phenomenonTime,2016-01-01T00:00:00+10/2016-03-05T00:00:00+10')
    # Process WaterML Response
    from owslib.etree import etree
    from owslib.swe.observation.sos200 import SOSGetObservationResponse
    from owslib.swe.observation.waterml2 import MeasurementTimeseriesObservation

    et = etree.fromstring(response)
    parsed_response = SOSGetObservationResponse(et)
    assert len(parsed_response.observations) > 0
    for o in parsed_response.observations:
        assert isinstance(o, MeasurementTimeseriesObservation)
