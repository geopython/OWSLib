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
        layers=['bvv:lkr_ex'], srs='EPSG:31468',
        bbox=(4500000, 5500000, 4500500, 5500500), size=(500, 500), format='image/jpeg',
        info_format="text/html", xy=(250, 250))
    html_string1 = res1.read().decode("utf-8")
    assert 'lkr_ex' in html_string1

    res2 = wms.getfeatureinfo(
        layers=['bvv:lkr_ex', 'bvv:gmd_ex'], srs='EPSG:31468',
        bbox=(4500000, 5500000, 4500500, 5500500), size=(500, 500), format='image/jpeg',
        info_format="text/html", xy=(250, 250))
    html_string2 = res2.read().decode("utf-8")
    assert 'lkr_ex' in html_string2
    assert 'gmd_ex' in html_string2

    res3 = wms.getfeatureinfo(
        layers=['bvv:lkr_ex', 'bvv:gmd_ex'], srs='EPSG:31468',
        bbox=(4500000, 5500000, 4500500, 5500500), size=(500, 500), format='image/jpeg',
        query_layers=['bvv:lkr_ex'], info_format="text/html", xy=(250, 250))
    html_string3 = res3.read().decode("utf-8")
    assert 'lkr_ex' in html_string3
    assert 'gmd_ex' not in html_string3
