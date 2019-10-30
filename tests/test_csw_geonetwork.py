from tests.utils import service_ok

import pytest

from owslib.csw import CatalogueServiceWeb

SERVICE_URL = 'https://metadata.bgs.ac.uk/geonetwork/srv/en/csw'


@pytest.mark.online
@pytest.mark.skip(reason='server ssl issue. See issue #624')
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_csw_geonetwork():
    c = CatalogueServiceWeb(SERVICE_URL)
    c.getrecords2(typenames='csw:Record')
    assert c.results.get('returned') > 0
    assert c.results.get('nextrecord') > 0
    assert c.results.get('matches') > 0
