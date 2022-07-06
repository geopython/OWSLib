from tests.utils import service_ok

import pytest

from owslib.ogcapi.processes import Processes

SERVICE_URL = 'https://demo.pygeoapi.io/master'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_ogcapi_processes_pygeoapi():
    p = Processes(SERVICE_URL)

    assert p.url == 'https://demo.pygeoapi.io/master/'
    assert p.url_query_string is None

    api = p.api()
    assert api['components']['parameters'] is not None
    paths = api['paths']
    assert paths is not None
    assert paths['/processes/hello-world'] is not None

    conformance = p.conformance()
    assert len(conformance['conformsTo']) > 0

    collections = p.collections()
    assert len(collections) > 0

    processes = p.processes()
    assert len(processes) == 1

    hello_world = p.process('hello-world')
    assert hello_world['id'] == 'hello-world'
    assert hello_world['title'] == 'Hello World'
