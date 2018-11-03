from tests.utils import service_ok

import pytest

from owslib.wfs import WebFeatureService

SERVICE_URL = 'https://www.ldproxy.nrw.de/rest/services/kataster/?f=json'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_wfs3_ldproxy():
    w = WebFeatureService(SERVICE_URL, version='3.0')

    assert w.url == 'https://www.ldproxy.nrw.de/rest/services/kataster/'
    assert w.version == '3.0'
    assert w.url_query_string == 'f=json'

    conformance = w.conformance()
    assert len(conformance['conformsTo']) == 5
