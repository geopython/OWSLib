from tests.utils import service_ok
from tests.utils import resource_file

from owslib.wms import WebMapService
import os
from collections import OrderedDict

import pytest


def test_wms_capabilities():
    # Fake a request to a WMS Server using saved doc from
    # http://wms.jpl.nasa.gov/wms.cgi.
    xml = open(resource_file('wms_JPLCapabilities.xml'), 'rb').read()
    wms = WebMapService('url', version='1.1.1', xml=xml)

    # Test capabilities
    # -----------------

    assert wms.identification.type == 'OGC:WMS'
    assert wms.identification.version == '1.1.1'
    assert wms.identification.title == 'JPL Global Imagery Service'
    assert wms.identification.abstract == 'WMS Server maintained by JPL, worldwide satellite imagery.'
    assert wms.identification.keywords == ['ImageryBaseMapsEarthCover', 'Imagery',
                                           'BaseMaps', 'EarthCover', 'JPL', 'Jet Propulsion Laboratory',
                                           'Landsat', 'WMS', 'SLD', 'Global']
    assert wms.identification.accessconstraints == 'Server is load limited'
    assert wms.identification.fees == 'none'
    assert wms.provider.name == 'JPL'
    assert wms.provider.url == 'http://OnEarth.jpl.nasa.gov/index.html'

    # Check contact info (some of it is missing)
    assert wms.provider.contact.name == 'Lucian Plesea'
    assert wms.provider.contact.email == 'lucian.plesea@jpl.nasa.gov'
    wms.provider.contact.address
    wms.provider.contact.city
    wms.provider.contact.country
    wms.provider.contact.region
    wms.provider.contact.postcode
    assert wms.provider.contact.organization == 'JPL'
    wms.provider.contact.position

    # Test available content layers
    assert isinstance(wms.items(), list) is True
    assert isinstance(wms.contents, OrderedDict) is True

    # NOTE: Not sure this dictionary interface is right...??
    assert sorted(wms.contents.keys()) == ['BMNG', 'daily_afternoon', 'daily_planet',
                                           'gdem', 'global_mosaic', 'global_mosaic_base',
                                           'huemapped_srtm', 'modis', 'srtm_mag', 'srtmplus',
                                           'us_colordem', 'us_elevation', 'us_landsat_wgs84',
                                           'us_ned', 'worldwind_dem']

    assert sorted([wms[layer].id for layer in wms.contents]) == ['BMNG', 'daily_afternoon', 'daily_planet',
                                                                 'gdem', 'global_mosaic', 'global_mosaic_base',
                                                                 'huemapped_srtm', 'modis', 'srtm_mag', 'srtmplus',
                                                                 'us_colordem', 'us_elevation', 'us_landsat_wgs84',
                                                                 'us_ned', 'worldwind_dem']
    # Test single item accessor
    assert wms['global_mosaic'].title == 'WMS Global Mosaic, pan sharpened'
    assert wms['global_mosaic'].keywords == []

    ['GlobalMosaic', 'Imagery', 'BaseMaps', 'EarthCover', 'JPL', 'Jet Propulsion Laboratory',
     'Landsat', 'WMS', 'SLD', 'Global']

    wms['global_mosaic'].boundingBox
    assert wms['global_mosaic'].boundingBoxWGS84 == (-180.0, -60.0, 180.0, 84.0)
    assert sorted(wms['global_mosaic'].crsOptions) == ['AUTO:42003', 'EPSG:4326']

    x = wms['global_mosaic'].styles
    assert x == {'pseudo_bright': {'title': 'Pseudo-color image (Uses IR and Visual bands, 542 mapping), gamma 1.5'},
                 'pseudo': {'title': '(default) Pseudo-color image, pan sharpened (Uses IR and Visual bands, 542 mapping), gamma 1.5'},  # noqa
                 'visual': {'title': 'Real-color image, pan sharpened (Uses the visual bands, 321 mapping), gamma 1.5'},
                 'pseudo_low': {'title': 'Pseudo-color image, pan sharpened (Uses IR and Visual bands, 542 mapping)'},
                 'visual_low': {'title': 'Real-color image, pan sharpened (Uses the visual bands, 321 mapping)'},
                 'visual_bright': {'title': 'Real-color image (Uses the visual bands, 321 mapping), gamma 1.5'}}

    # Expecting a KeyError for invalid names
    with pytest.raises(KeyError, message="Expecting a KeyError for invalid names"):
        wms['utterly bogus'].title

    # Test operations
    assert sorted([op.name for op in wms.operations]) == ['GetCapabilities', 'GetMap', 'GetTileService']

    x = wms.getOperationByName('GetMap').methods
    assert x == [{'type': 'Get', 'url': 'http://wms.jpl.nasa.gov/wms.cgi?'}]

    assert wms.getOperationByName('GetMap').formatOptions == ['image/jpeg', 'image/png', 'image/geotiff',
                                                              'image/tiff', 'application/vnd.google-earth.kml+xml']

    # Test exceptions
    assert wms.exceptions == ['application/vnd.ogc.se_xml']


SERVICE_URL = 'http://giswebservices.massgis.state.ma.us/geoserver/wms'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WMS service is unreachable")
def test_wms_getmap():
    # Lastly, test the getcapabilities and getmap methods
    wms = WebMapService(SERVICE_URL, version='1.1.1')
