from tests.utils import scratch_file
from tests.utils import service_ok

from owslib.wmts import WebMapTileService

import pytest

SERVICE_URL = 'http://map1c.vis.earthdata.nasa.gov/wmts-geo/wmts.cgi'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WMTS service is unreachable")
@pytest.mark.skip(reason="WMTS service not responding correctly")
def test_wmts():
    # Find out what a WMTS has to offer. Service metadata:
    wmts = WebMapTileService(SERVICE_URL)
    assert wmts.identification.type == 'OGC WMTS'
    assert wmts.identification.version == '1.0.0'
    assert wmts.identification.title == 'NASA Global Imagery Browse Services for EOSDIS'
    bytearray(wmts.identification.abstract, 'utf-8')
    bytearray(b'Near real time imagery from multiple NASA instruments')
    assert wmts.identification.keywords == ['World', 'Global']
    # Service Provider:
    assert wmts.provider.name == 'National Aeronautics and Space Administration'
    assert wmts.provider.url == 'https://earthdata.nasa.gov/'
    # Available Layers:
    assert len(wmts.contents.keys()) > 0
    assert sorted(list(wmts.contents))[0] == 'AIRS_CO_Total_Column_Day'
    # Fetch a tile (using some defaults):
    tile = wmts.gettile(layer='MODIS_Terra_CorrectedReflectance_TrueColor',
                        tilematrixset='EPSG4326_250m', tilematrix='0',
                        row=0, column=0, format="image/jpeg")
    out = open(scratch_file('nasa_modis_terra_truecolour.jpg'), 'wb')
    bytes_written = out.write(tile.read())
    out.close()
    # Test styles for several layers
    # TODO: fix dict order
    # assert wmts.contents['MLS_SO2_147hPa_Night'].styles == {'default': {'isDefault': True, 'title': 'default'}}
    assert wmts.contents['MLS_SO2_147hPa_Night'].styles['default']['isDefault'] is True
    # assert wmts.contents['MLS_SO2_147hPa_Night'].styles == {'default': {'isDefault': True, 'title': 'default'}}
    assert wmts.contents['MLS_SO2_147hPa_Night'].styles['default']['isDefault'] is True


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WMTS service is unreachable")
@pytest.mark.skip(reason="WMTS service not responding correctly")
def test_wmts_example_build_tile_request():
    """
    Example for wmts.buildTileRequest
    """
    wmts = WebMapTileService(SERVICE_URL)
    wmts.buildTileRequest(
        layer='VIIRS_CityLights_2012',
        tilematrixset='EPSG4326_500m',
        tilematrix='6',
        row=4, column=4)
    request = 'SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&\
LAYER=VIIRS_CityLights_2012&STYLE=default&TILEMATRIXSET=EPSG4326_500m&\
TILEMATRIX=6&TILEROW=4&TILECOL=4&FORMAT=image%2Fjpeg'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WMTS service is unreachable")
@pytest.mark.skip(reason="WMTS service not responding correctly")
def test_wmts_example_get_title():
    """
    Example for wmts.getTitle
    """
    wmts = WebMapTileService(SERVICE_URL)
    img = wmts.gettile(
        layer='VIIRS_CityLights_2012',
        tilematrixset='EPSG4326_500m',
        tilematrix='6',
        row=4, column=4)
    out = open('tile.jpg', 'wb')
    bytes_written = out.write(img.read())
    out.close()


EXAMPLE_SERVICE_URL = "http://tile.informatievlaanderen.be/ws/raadpleegdiensten/wmts"


def test_wmts_example_informatievlaanderen():
    wmts = WebMapTileService(EXAMPLE_SERVICE_URL)
    assert wmts.identification.type == 'OGC WMTS'
    assert wmts.identification.version == '1.0.0'
    assert wmts.identification.title == 'agentschap Informatie Vlaanderen WMTS service'
    # assert sorted(list(wmts.contents))[:5] == ['abw', 'ferraris', 'frickx', 'grb_bsk', 'grb_bsk_grijs']


@pytest.mark.online
@pytest.mark.skipif(not service_ok(EXAMPLE_SERVICE_URL),
                    reason="WMTS service is unreachable")
def test_wmts_without_serviceprovider_tag():
    # Test a WMTS without a ServiceProvider tag in Capababilities XML
    from owslib.wmts import WebMapTileService
    wmts = WebMapTileService(SERVICE_URL_ARCGIS)


SERVICE_URL_REST = 'https://www.basemap.at/wmts/1.0.0/WMTSCapabilities.xml'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL_REST),
                    reason="WMTS service is unreachable")
def test_wmts_rest_only():
    # Test a WMTS with REST only
    from owslib.wmts import WebMapTileService
    wmts = WebMapTileService(SERVICE_URL_REST)
    tile = wmts.gettile(layer="bmaporthofoto30cm", tilematrix="10", row=357, column=547)
    assert(tile.info()['Content-Type'] == 'image/jpeg')
