from tests.utils import service_ok

import pytest

from owslib.ogcapi.records import Records

SERVICE_URL = 'https://demo.pycsw.org/cite'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_ogcapi_records_pycsw():
    w = Records(SERVICE_URL)

    assert w.url == 'https://demo.pycsw.org/cite/'
    assert w.url_query_string is None

    api = w.api()
    assert api['components']['parameters'] is not None
    paths = api['paths']
    assert paths is not None
    assert paths['/collections/{collectionId}'] is not None

    conformance = w.conformance()
    assert len(conformance['conformsTo']) == 14

    collections = w.collections()
    assert len(collections) > 0

    record_collections = w.records()
    assert record_collections == ['metadata:main']

    pycsw_cite_demo = w.collection('metadata:main')
    assert pycsw_cite_demo['id'] == 'metadata:main'
    assert pycsw_cite_demo['title'] == 'pycsw OGC CITE demo and Reference Implementation'  # noqa
    assert pycsw_cite_demo['itemType'] == 'record'
    assert w.request == 'https://demo.pycsw.org/cite/collections/metadata:main'  # noqa
    assert w.response is not None
    assert isinstance(w.response, dict)

    pycsw_cite_demo_queryables = w.collection_queryables('metadata:main')
    assert len(pycsw_cite_demo_queryables['properties'].keys()) == 14

    # Minimum of limit param is 1
    with pytest.raises(RuntimeError):
        pycsw_cite_demo_query = w.collection_items('metadata:main', limit=0)

    pycsw_cite_demo_query = w.collection_items('metadata:main', limit=1)
    assert pycsw_cite_demo_query['numberMatched'] == 12
    assert pycsw_cite_demo_query['numberReturned'] == 1
    assert len(pycsw_cite_demo_query['features']) == 1

    pycsw_cite_demo_query = w.collection_items('metadata:main', q='lorem')
    assert pycsw_cite_demo_query['numberMatched'] == 5
    assert pycsw_cite_demo_query['numberReturned'] == 5
    assert len(pycsw_cite_demo_query['features']) == 5

    cql_text = "title LIKE 'Lorem%'"
    pycsw_cite_demo_query = w.collection_items('metadata:main', filter=cql_text)
    assert pycsw_cite_demo_query['numberMatched'] == 2
    assert pycsw_cite_demo_query['numberReturned'] == 2
    assert len(pycsw_cite_demo_query['features']) == 2

    cql_json = {'op': '=', 'args': [{'property': 'title'}, 'Lorem ipsum']}
    pycsw_cite_demo_query = w.collection_items('metadata:main', cql=cql_json)
    assert pycsw_cite_demo_query['numberMatched'] == 1
    assert pycsw_cite_demo_query['numberReturned'] == 1
    assert len(pycsw_cite_demo_query['features']) == 1


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
@pytest.mark.parametrize("path, expected", [
    ('collections/foo/1', 'https://demo.pycsw.org/cite/collections/foo/1'),
    ('collections/foo/https://example.org/11', 'https://demo.pycsw.org/cite/collections/foo/https://example.org/11')  # noqa
])
def test_ogcapi_build_url(path, expected):
    w = Records(SERVICE_URL)
    assert w._build_url(path) == expected
