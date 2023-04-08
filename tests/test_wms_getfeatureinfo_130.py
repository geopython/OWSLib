import pytest
from tests.utils import service_ok

from owslib.wms import WebMapService

SERVICE_URL = 'http://geoserv.weichand.de:8080/geoserver/wms'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WMS service is unreachable")
def test_wms_getfeatureinfo_130():
    wms = WebMapService(SERVICE_URL, version='1.3.0')

    res1 = wms.getfeatureinfo(
        layers=['bvv:dgm50_epsg31468'], srs='EPSG:31468',
        bbox=(4500000, 5500000, 4500500, 5500500), size=(500, 500), format='image/jpeg',
        info_format="text/html", xy=(250, 250))
    html_string1 = res1.read().decode("utf-8")
    assert 'dgm5' in html_string1
