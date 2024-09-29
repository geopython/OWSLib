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
    assert len(processes) == 6

    hello_world = p.process('hello-world')
    assert hello_world['id'] == 'hello-world'
    assert hello_world['title'] == 'Hello World'

    inputs = {
        'name': 'World',
        'message': 'Testing from OWSLib'
    }

    execution = p.execute('hello-world', inputs=inputs)

    assert execution['outputs'][0]['id'] == 'echo'
    assert execution['outputs'][0]['value'] == 'Hello World! Testing from OWSLib'  # noqa

    execution = p.execute('hello-world', inputs=inputs, response='raw')

    assert execution['id'] == 'echo'
    assert execution['value'] == 'Hello World! Testing from OWSLib'
