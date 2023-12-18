from tests.utils import service_ok

import pytest

from owslib.ogcapi.features import Features

SERVICE_URL = 'https://demo.pygeoapi.io/master'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_ogcapi_features_pygeoapi():
    w = Features(SERVICE_URL)

    assert w.url == 'https://demo.pygeoapi.io/master/'
    assert w.url_query_string is None

    api = w.api()
    assert api['components']['parameters'] is not None
    paths = api['paths']
    assert paths is not None
    assert paths['/collections/lakes'] is not None

    conformance = w.conformance()
    assert len(conformance['conformsTo']) > 0

    collections = w.collections()
    assert len(collections) > 0

    feature_collections = w.feature_collections()
    assert len(feature_collections) > 0

    lakes = w.collection('lakes')
    assert lakes['id'] == 'lakes'
    assert lakes['title'] == 'Large Lakes'
    assert lakes['description'] == 'lakes of the world, public domain'

    # lakes_queryables = w.collection_queryables('lakes')
    # assert len(lakes_queryables['queryables']) == 6

    # Minimum of limit param is 1
    with pytest.raises(RuntimeError):
        lakes_query = w.collection_items('lakes', limit=0)

    lakes_query = w.collection_items('lakes', limit=1, admin='admin-0')
    assert lakes_query['numberMatched'] > 0
    assert lakes_query['numberReturned'] == 1
    assert len(lakes_query['features']) == 1
