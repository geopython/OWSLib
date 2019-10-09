from tests.utils import service_ok

import pytest

from owslib.wfs import WebFeatureService

SERVICE_URL = 'https://demo.pygeoapi.io/master'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_wfs3_pygeoapi():
    w = WebFeatureService(SERVICE_URL, version='3.0')

    assert w.url == 'https://demo.pygeoapi.io/master/'
    assert w.version == '3.0'
    assert w.url_query_string is None

    api = w.api()
    assert api['components']['parameters'] is not None
    paths = api['paths']
    assert paths is not None
    assert paths['/collections/lakes'] is not None

    conformance = w.conformance()
    assert len(conformance['conformsTo']) == 4

    collections = w.collections()
    assert len(collections) > 0

    lakes = w.collection('lakes')
    assert lakes['id'] == 'lakes'
    assert lakes['title'] == 'Large Lakes'
    assert lakes['description'] == 'lakes of the world, public domain'

    # Minimum of limit param is 1
    lakes_query = w.collection_items('lakes', limit=0)
    assert lakes_query['code'] == 'InvalidParameterValue'

    lakes_query = w.collection_items('lakes', limit=1)
    assert lakes_query['numberMatched'] == 25
    assert lakes_query['numberReturned'] == 1
    assert len(lakes_query['features']) == 1
