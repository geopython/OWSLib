from tests.utils import service_ok

import pytest

from owslib.csw import CatalogueServiceWeb

SERVICE_URL = 'http://geoportal.ypen.gr/geonetwork/srv/eng/csw'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_csw_geonetwork():
    c = CatalogueServiceWeb(SERVICE_URL)
    c.getrecords2(typenames='csw:Record')
    assert c.results.get('returned') > 0
    assert c.results.get('nextrecord') > 0
    assert c.results.get('matches') > 0

SERVICE_URL3 = 'https://metawal.wallonie.be/geonetwork/srv/eng/csw'

@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL3),
                    reason='service is unreachable')
@pytest.mark.parametrize("esn_in", ['full', 'summary'])
def test_csw_geonetwork_iso3(esn_in):
    """ Test retrieving records from Belgian geonetwork,
    specifically requesting ISO 19115 Part 3 XML records.
    """
    c = CatalogueServiceWeb(SERVICE_URL3)
    c.getrecords2(outputschema='http://standards.iso.org/iso/19115/-3/mdb/2.0',
                  typenames='mdb:MD_Metadata',
                  esn=esn_in)

    # Valid results were returned
    assert c.results.get('returned') > 0
    assert c.results.get('nextrecord') > 0
    assert c.results.get('matches') > 0
    for id in c.records.keys():
        assert c.records[id].identifier == id
