from tests.utils import service_ok

import pytest

from owslib.wfs import WebFeatureService

SERVICE_URL = 'http://geo.kralidis.ca/pygeoapi'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_wfs3_pygeoapi():
    w = WebFeatureService(SERVICE_URL, version='3.0')

    assert w.url == 'http://geo.kralidis.ca/pygeoapi/'
    assert w.version == '3.0'
    assert w.url_query_string is None

    conformance = w.conformance()
    assert len(conformance['conformsTo']) == 4

    collections = w.collections()
    assert len(collections) == 3

    lakes = w.collection('lakes')
    assert lakes['name'] == 'lakes'
    assert lakes['title'] == 'Large Lakes'
    assert lakes['description'] == 'lakes of the world, public domain'

    lakes_query = w.collection_items('lakes', limit=0)
    assert lakes_query['numberMatched'] == 25
    assert lakes_query['numberReturned'] == 0
    assert len(lakes_query['features']) == 0
