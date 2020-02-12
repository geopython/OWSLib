from tests.utils import scratch_file
from tests.utils import service_ok

from owslib.wmts import WebMapTileService

import pytest

SERVICE_URL = "http://geoserv.weichand.de/mapproxy/wmts/1.0.0/WMTSCapabilities.xml"


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WMTS service is unreachable")
def test_wmts_rest_only():
    # ServiceMetadata
    wmts = WebMapTileService(SERVICE_URL)
    assert wmts.identification.type == 'OGC WMTS'
    assert wmts.identification.version == '1.0.0'
    assert wmts.identification.title == 'WMTS-Testserver DOP80'
    # Content
    assert sorted(list(wmts.contents)) == ['dop80']
    # RESTful WMTS
    assert wmts.restonly
    resource = wmts.buildTileResource(
        layer='dop80', tilematrixset='webmercator', tilematrix='11', row='706', column='1089')
    assert resource == 'http://geoserv.weichand.de/mapproxy/wmts/dop80/webmercator/11/1089/706.png'

    tile = wmts.gettile(
        layer='dop80', tilematrixset='webmercator', tilematrix='11', row='706', column='1089')
    out = open(scratch_file('bvv_bayern_dop80.png'), 'wb')
    bytes_written = out.write(tile.read())
    out.close()
