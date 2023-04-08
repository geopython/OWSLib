from tests.utils import service_ok

import pytest

from owslib.ogcapi.records import Records

SERVICE_URL = 'https://demo.pygeoapi.io/master/'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_ogcapi_records_pygeoapi():
    w = Records(SERVICE_URL)

    assert w.url == SERVICE_URL
    assert w.url_query_string is None

    api = w.api()
    assert api['components']['parameters'] is not None
    paths = api['paths']
    assert paths is not None
    assert paths['/collections/dutch-metadata'] is not None

    conformance = w.conformance()
    assert len(conformance['conformsTo']) > 8

    collections = w.collections()
    assert len(collections) > 0

    records = w.records()
    assert len(records) == 1

    dutch_metacat = w.collection('dutch-metadata')
    assert dutch_metacat['id'] == 'dutch-metadata'
    assert dutch_metacat['title'] == 'Sample metadata records from Dutch Nationaal georegister'  # noqa
    assert dutch_metacat['description'] == 'Sample metadata records from Dutch Nationaal georegister'  # noqa
    assert w.request == f'{SERVICE_URL}collections/dutch-metadata'
    assert w.response is not None
    assert isinstance(w.response, dict)

    dutch_metacat_queryables = w.collection_queryables('dutch-metadata')
    assert len(dutch_metacat_queryables['properties']) == 11

    # Minimum of limit param is 1
    with pytest.raises(RuntimeError):
        dutch_metacat_query = w.collection_items('dutch-metadata', limit=0)

    dutch_metacat_query = w.collection_items('dutch-metadata', limit=1)
    assert dutch_metacat_query['numberMatched'] == 308
    assert dutch_metacat_query['numberReturned'] == 1
    assert len(dutch_metacat_query['features']) == 1

    dutch_metacat_query = w.collection_items('dutch-metadata', q='Wegpanorama')
    assert dutch_metacat_query['numberMatched'] == 3
    assert dutch_metacat_query['numberReturned'] == 3
    assert len(dutch_metacat_query['features']) == 3
