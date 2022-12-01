from io import BytesIO

from tests.utils import service_ok

import pytest

from owslib.ogcapi.maps import Maps

SERVICE_URL = 'https://test.cubewerx.com/cubewerx/cubeserv/demo/ogcapi/EuroRegionalMap/'  # noqa


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_ogcapi_maps_pygeoapi():
    w = Maps(SERVICE_URL)

    assert w.url == SERVICE_URL
    assert w.url_query_string is None

    collections = w.collections()
    assert len(collections) > 0

    maps = w.maps()
    assert len(maps) > 0

    erm = w.collection('erm')
    assert erm['id'] == 'erm'
    assert erm['title'] == 'EuroRegionalMap'

    data = w.map('erm', width=1200, height=800, transparent=False)
    assert isinstance(data, BytesIO)
