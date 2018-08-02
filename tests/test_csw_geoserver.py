from tests.utils import service_ok

import pytest

from owslib.csw import CatalogueServiceWeb

SERVICE_URL = 'http://gis.armf.bg:8080/geoserver/csw'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_csw_geoserver():
    c = CatalogueServiceWeb(SERVICE_URL)
    c.getrecords2(typenames='csw:Record')
    assert c.results.get('returned') > 0
    assert c.results.get('nextrecord') > 0
    assert c.results.get('matches') > 0
