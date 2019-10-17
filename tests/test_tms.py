from tests.utils import scratch_file
from tests.utils import service_ok

import pytest

SERVICE_URL = 'http://geodata.nationaalgeoregister.nl/tiles/service/tms/1.0.0'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="TMS service is unreachable")
def test_tms():
    # Find out what a TMS has to offer. Service metadata:
    from owslib.tms import TileMapService
    tms = TileMapService(SERVICE_URL)

    # Fetch a tile (using some defaults):
    tile = tms.gettile(7, 7, 4, title='brtachtergrondkaart', srs='EPSG:28992', mimetype='image/png')
    out = open(scratch_file('brtachtergrondkaart.png'), 'wb')
    out.write(tile.read())
    out.close()
