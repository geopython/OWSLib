from tests.utils import service_ok

import pytest

from owslib.ogcapi.features import Features

SERVICE_URL = 'https://www.ldproxy.nrw.de/rest/services/kataster/?f=json'


@pytest.mark.online
@pytest.mark.skip(reason='api() call fails. See issue #625')
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_ogcapi_features_ldproxy():
    w = Features(SERVICE_URL)

    assert w.url == 'https://www.ldproxy.nrw.de/rest/services/kataster/'
    assert w.url_query_string == 'f=json'

    conformance = w.conformance()
    assert len(conformance['conformsTo']) == 5

    api = w.api()
    assert api['components']['parameters'] is not None
    assert api['paths'] is not None
