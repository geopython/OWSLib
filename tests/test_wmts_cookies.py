from tests.utils import scratch_file
from tests.utils import service_ok

from owslib.wmts import WebMapTileService

import pytest

SERVICE_URL_EXAMPLE = 'https://mapsneu.wien.gv.at/basemapneu/1.0.0/WMTSCapabilities.xml'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL_EXAMPLE, timeout=20),
                    reason="WMTS service is unreachable")
def test_wmts_cookies():
    from owslib.wmts import WebMapTileService
    cookies = {
        'cookie1': 'example1',
        'cookie2': 'example2'
    }
    wmts = WebMapTileService(SERVICE_URL_EXAMPLE, cookies=cookies)
    tile = wmts.gettile(layer="bmaporthofoto30cm", tilematrix="10", row=357, column=547)
    tile_raw_cookies = tile._response.request.headers['Cookie']
    tile_cookies = (dict(i.split('=',1) for i in tile_raw_cookies.split('; ')))
    assert tile_cookies.get('cookie1') == 'example1'
    assert tile_cookies.get('cookie2') == 'example2'