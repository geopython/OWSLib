from tests.utils import scratch_file


def test_wmts():
    # Find out what a WMTS has to offer. Service metadata:
    from owslib.wmts import WebMapTileService
    wmts = WebMapTileService("http://map1c.vis.earthdata.nasa.gov/wmts-geo/wmts.cgi")
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
    assert sorted(list(wmts.contents))[0] == 'AIRS_All_Sky_Outgoing_Longwave_Radiation_Daily_Day'
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
    # Test a WMTS without a ServiceProvider tag in Capababilities XML
    wmts = WebMapTileService(
        'http://data.geus.dk/arcgis/rest/services/OneGeologyGlobal/S071_G2500_OneGeology/MapServer/WMTS/1.0.0/WMTSCapabilities.xml')  # noqa
