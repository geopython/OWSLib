from tests.utils import service_ok

import pytest

from owslib.opensearch import OpenSearch

SERVICE_URL = 'https://datahub.creodias.eu/resto/api/collections/Sentinel1/describe.xml'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_opensearch_creodias():

    o = OpenSearch(SERVICE_URL)

    assert o.description.shortname == 'Sentinel-1'
    assert o.description.description == 'Sentinel-1 Collection'
    assert o.description.language == 'en'

    assert len(o.description.urls) == 1

    assert len(o.description.urls['application/json']['parameters']) > 0

    with pytest.raises(RuntimeError):
        _ = o.search('application/json', productType='invalid')

    with pytest.raises(RuntimeError):
        _ = o.search('application/json', foo='bar')

    results = o.search('application/json', productType='SLC')

    assert isinstance(results, dict)
