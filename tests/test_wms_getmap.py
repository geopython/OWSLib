from unittest import mock

import pytest
from tests.utils import service_ok

from owslib.wms import WebMapService
from owslib.map.wms130 import WebMapService_1_3_0
from owslib.util import ServiceException
from owslib.util import ResponseWrapper


SERVICE_URL = 'http://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r-t.cgi'
NCWMS2_URL = "http://wms.stccmop.org:8080/ncWMS2/wms"


@pytest.fixture
def wms():
    return WebMapService_1_3_0(SERVICE_URL, version='1.3.0')


@pytest.mark.parametrize("version", ["1.3.0", "1.1.1"])
def test_build_getmap_request_bbox_precision(version):
    bbox = (-126.123456789, 24.123456789, -66.123456789, 50.123456789)
    bbox_yx = (bbox[1], bbox[0], bbox[3], bbox[2])

    m = mock.Mock()
    type(m).version = mock.PropertyMock(return_value=version)

    request = WebMapService_1_3_0._WebMapService_1_3_0__build_getmap_request(m,
        layers=['layer1'],
        styles=['default'],
        srs='EPSG:4326',
        bbox=bbox,
        format='image/jpeg',
        size=(250, 250),
        transparent=True
    )
    assert request['bbox'] == ','.join(map(str, bbox_yx))


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WMS service is unreachable")
def test_wms_getmap_111():
    """MESONET GetMap 1.1.1"""
    wms = WebMapService(SERVICE_URL, version='1.1.1')
    assert wms.request == '{}?service=WMS&request=GetCapabilities&version=1.1.1'.format(SERVICE_URL)
    rsp = wms.getmap(
        layers=['nexrad_base_reflect'],
        styles=['default'],
        srs='EPSG:4326',
        bbox=(-126, 24, -66, 50),
        size=(250, 250),
        format='image/jpeg',
        transparent=True)
    import owslib.util
    assert type(rsp) is ResponseWrapper


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WMS service is unreachable")
def test_wms_getmap_111_service_exception():
    """GetMap 1.1.1 ServiceException for an invalid CRS"""
    wms = WebMapService(SERVICE_URL, version='1.1.1')
    try:
        wms.getmap(
            layers=['nexrad_base_reflect'],
            styles=['default'],
            srs='EPSG:4328',
            bbox=(-126, 24, -66, 50),
            size=(250, 250),
            format='image/jpeg',
            transparent=True)
    except ServiceException as e:
        assert "msWMSLoadGetMapParams(): WMS server error. Invalid SRS given : SRS must be valid for all requested layers." in str(e)  # noqa
    else:
        assert False


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WMS service is unreachable")
def test_wms_getmap_130():
    """GetMap 1.3.0"""
    wms = WebMapService(SERVICE_URL, version='1.3.0')
    rsp = wms.getmap(
        layers=['nexrad_base_reflect'],
        styles=['default'],
        srs='EPSG:4326',
        bbox=(-126, 24, -66, 50),
        size=(250, 250),
        format='image/jpeg',
        transparent=True)
    assert type(rsp) is ResponseWrapper


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WMS service is unreachable")
def test_wms_getmap_130_service_exception():
    """GetMap 1.3.0 ServiceException for an invalid CRS"""
    wms = WebMapService(SERVICE_URL, version='1.3.0')
    try:
        wms.getmap(
            layers=['nexrad_base_reflect'],
            styles=['default'],
            srs='EPSG:4328',
            bbox=(-126, 24, -66, 50),
            size=(250, 250),
            format='image/jpeg',
            transparent=True)
    except ServiceException as e:
        assert "msWMSLoadGetMapParams(): WMS server error. Invalid CRS given : CRS must be valid for all requested layers." in str(e)  # noqa
    else:
        assert False


SERVICE_URL_NATIONAL_MAP = 'http://services.nationalmap.gov/ArcGIS/services/geonames/MapServer/WMSServer'


@pytest.mark.online
@pytest.mark.skip(reason="this is a flaky test")
# @pytest.mark.skipif(not service_ok(SERVICE_URL_NATIONAL_MAP),
#                    reason="WMS service is unreachable")
def test_getmap_130_national_map():
    """National Map"""
    # TODO: use flaky tests or fix it: https://pypi.python.org/pypi/pytest-ignore-flaky
    url = SERVICE_URL_NATIONAL_MAP
    wms = WebMapService(url, version='1.3.0')
    rsp = wms.getmap(
        layers=['3'],
        styles=['default'],
        srs='CRS:84',
        bbox=(-176.646, 17.7016, -64.8017, 71.2854),
        size=(500, 300),
        format='image/png',
        transparent=True)
    assert type(rsp) is ResponseWrapper
    assert "service=WMS" in wms.request
    assert "version=1.3.0" in wms.request
    assert "request=GetMap" in wms.request
    assert "layers=3" in wms.request
    assert "styles=default" in wms.request
    assert "crs=CRS%3A84" in wms.request
    assert "box=-176.646%2C17.7016%2C-64.8017%2C71.2854" in wms.request
    assert "width=500" in wms.request
    assert "height=300" in wms.request
    assert "format=image%2Fpng" in wms.request
    assert "transparent=TRUE" in wms.request
    assert "bgcolor=0x#FFFFFF" in wms.request


@pytest.mark.online
@pytest.mark.skip(reason="this is a flaky test")
# @pytest.mark.skipif(not service_ok(SERVICE_URL_NATIONAL_MAP),
#                    reason="WMS service is unreachable")
def test_getmap_130_national_map_no_bgcolor():
    """National Map"""
    url = SERVICE_URL_NATIONAL_MAP
    wms = WebMapService(url, version='1.3.0')
    rsp = wms.getmap(
        layers=['3'],
        styles=['default'],
        srs='CRS:84',
        bbox=(-176.646, 17.7016, -64.8017, 71.2854),
        size=(500, 300),
        format='image/png',
        transparent=True,
        bgcolor=None)
    assert type(rsp) is ResponseWrapper
    assert "bgcolor" not in wms.request


@pytest.mark.online
@pytest.mark.skipif(not service_ok(NCWMS2_URL), reason="WMS service is unreachable")
def test_ncwms2():
    """Test with an ncWMS2 server.
    """
    # Note that this does not exercise the bug in https://github.com/geopython/OWSLib/issues/556
    wms = WebMapService(NCWMS2_URL, version='1.3.0')
    rsp = wms.getmap(
        layers=['f33_thredds/min_temp'],
        styles=['default'],
        srs='CRS:84',
        bbox=(-124.17, 46.02, -123.29, 46.38),
        size=(256, 256),
        format='image/png',
        transparent=True,
        mode='32bit',

    )
    assert type(rsp) is ResponseWrapper
    assert "service=WMS" in wms.request
    assert "version=1.3.0" in wms.request
    assert "request=GetMap" in wms.request
    assert "layers=f33_thredds/min_temp" in wms.request
    assert "styles=default" in wms.request
    assert "crs=CRS%3A84" in wms.request
    assert "width=256" in wms.request
    assert "height=256" in wms.request
    assert "format=image%2Fpng" in wms.request
    assert "transparent=TRUE" in wms.request
    assert "bgcolor=0x#FFFFFF" in wms.request


@pytest.mark.parametrize('wms_version', ['1.1.1', '1.3.0'])
def test_wms_sends_headers(wms_version):
    """Test that if headers are provided in the WMS class they are sent
    when performing HTTP requests (in this case for GetCapabilities)
    """

    with mock.patch('owslib.util.requests.request', side_effect=RuntimeError) as mock_request:
        try:
            WebMapService(
                'http://example.com/wms',
                version=wms_version,
                headers={'User-agent': 'my-app/1.0'}
            )
        except RuntimeError:

            assert mock_request.called
            assert mock_request.call_args[1]['headers'] == {'User-agent': 'my-app/1.0'}
