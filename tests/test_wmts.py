from tests.utils import scratch_file
from tests.utils import service_ok

import pytest

SERVICE_URL = 'http://map1c.vis.earthdata.nasa.gov/wmts-geo/wmts.cgi'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WMTS service is unreachable")
def test_wmts():
    # Find out what a WMTS has to offer. Service metadata:
    from owslib.wmts import WebMapTileService
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


SERVICE_URL_ARCGIS = 'http://data.geus.dk/arcgis/rest/services/OneGeologyGlobal/S071_G2500_OneGeology/MapServer/WMTS/1.0.0/WMTSCapabilities.xml'  # noqa


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL_ARCGIS),
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
