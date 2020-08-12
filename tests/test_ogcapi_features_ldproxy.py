from tests.utils import service_ok

import pytest

from owslib.ogcapi.features import Features

SERVICE_URL = 'https://www.ldproxy.nrw.de/rest/services/kataster/?f=json'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_ogcapi_features_ldproxy():
    w = Features(SERVICE_URL)

    assert w.url == 'https://www.ldproxy.nrw.de/rest/services/kataster/'
    assert w.url_query_string == 'f=json'

    conformance = w.conformance()
    assert len(conformance['conformsTo']) == 5

    feature_collections = w.feature_collections()
    assert len(feature_collections) >= 0

    # TODO: remove pytest.raises once ldproxy is fixed/updated
    with pytest.raises(RuntimeError):
        api = w.api()
        assert api['components']['parameters'] is not None
        assert api['paths'] is not None
