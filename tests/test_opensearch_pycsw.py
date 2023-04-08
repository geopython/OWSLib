from tests.utils import service_ok

import pytest

from owslib.opensearch import OpenSearch

SERVICE_URL = 'https://demo.pycsw.org/cite/opensearch'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_opensearch_creodias():

    o = OpenSearch(SERVICE_URL)

    assert o.description.shortname == 'pycsw OGC CITE d'
    assert o.description.longname == 'pycsw OGC CITE demo and Reference Implementation'

    assert len(o.description.urls) == 2

    results = o.search('application/atom+xml')

    assert isinstance(results, dict)
