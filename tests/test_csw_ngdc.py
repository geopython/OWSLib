from tests.utils import service_ok

from owslib import fes, csw
from owslib.dif import namespaces

import pytest

SERVICE_URL = 'http://www.ngdc.noaa.gov/geoportal/csw'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="CSW service is unreachable")
def test_csw_ngdc():
    "rewritten doctest/cws_ngdc.txt"
    c = csw.CatalogueServiceWeb(SERVICE_URL, timeout=120)
    assert c.identification.title == 'ArcGIS Server Geoportal Extension 10 - OGC CSW 2.0.2 ISO AP'
    assert c.identification.version == '2.0.2'
    assert sorted(c.identification.keywords) == [
        'Geophysical Metadata', 'NGDC', 'Ocean Metadata', 'Space Weather Metadata']
    assert c.provider.name == 'NOAA NGDC'

    # Get some records

    sos_urn = 'urn:x-esri:specification:ServiceType:sos:url'
    aoos_uuid = '1706F520-2647-4A33-B7BF-592FAFDE4B45'
    uuid_filter = fes.PropertyIsEqualTo(propertyname='sys.siteuuid', literal="{%s}" % aoos_uuid)

    c.getrecords2([uuid_filter], esn='full', maxrecords=999999)
    assert len(c.records) > 40
    assert 'AOOS SOS' in c.records

    aoos_sos = c.records['AOOS SOS']
    assert aoos_sos.abstract == 'Alaska Ocean Observing System SOS'
    assert sorted([x['url'] for x in aoos_sos.references if x['scheme'] == sos_urn]) == [
        'http://sos.aoos.org/sos/sos/kvp?service=SOS&request=GetCapabilities&acceptVersions=1.0.0',
        'http://sos.aoos.org/sos/sos/kvp?service=SOS&request=GetCapabilities&acceptVersions=1.0.0',
        'http://sos.aoos.org/sos/sos/kvp?service=SOS&request=GetCapabilities&acceptVersions=1.0.0']
    assert c.getService_urls(sos_urn) == [
        'http://sos.aoos.org/sos/sos/kvp?service=SOS&request=GetCapabilities&acceptVersions=1.0.0']
