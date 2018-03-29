from tests.utils import service_ok

from owslib.wms import WebMapService
from owslib.util import ServiceException
from owslib.util import ResponseWrapper


import pytest

SERVICE_URL = 'http://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r-t.cgi'


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
        rsp = wms.getmap(
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
        rsp = wms.getmap(
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
