import pytest
import requests

from owslib.csw import CatalogueServiceWeb

SERVICE_URL = 'http://gis.armf.bg:8080/geoserver/csw'

@pytest.mark.online
@pytest.mark.skipif(not requests.get(SERVICE_URL).ok,
                    reason='service is unreachable')
def test_csw_geoserver():
    c = CatalogueServiceWeb(SERVICE_URL)
    c.getrecords2(typenames='csw:Record')
    assert c.results.get('returned') > 0
    assert c.results.get('nextrecord') > 0
    assert c.results.get('matches') > 0
