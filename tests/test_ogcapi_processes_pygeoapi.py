from tests.utils import service_ok

import pytest

from owslib.ogcapi.processes import Processes

SERVICE_URL = 'https://demo.pygeoapi.io/master'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_ogcapi_processes_pygeoapi():
    w = Processes(SERVICE_URL)

    assert w.url == 'https://demo.pygeoapi.io/master/'
    assert w.url_query_string is None

    api = w.api()
    assert api['components']['parameters'] is not None
    paths = api['paths']
    assert paths is not None
    assert paths['/processes/hello-world'] is not None

    conformance = w.conformance()
    assert len(conformance['conformsTo']) == 16

    # list processes
    processes = w.processes()
    assert len(processes) > 0
    assert processes[0].id == 'hello-world'

    # process description
    hello = w.process_description('hello-world')
    assert hello.id == 'hello-world'
    assert hello.title == 'Hello World'
    assert "An example process that takes a name as input" in hello.description

    # running jobs
    jobs = w.job_list('hello-world')
    assert len(jobs) >= 0

    # execute process in sync mode
    request_json = {"inputs": [{"id": "name", "value": "hello"}], "mode": "sync"}
    result = w.execute('hello-world', json=request_json)
    assert len(result.outputs) == 1
    assert result.outputs[0].id == 'echo'
    assert result.outputs[0].value == 'Hello hello!'

    # execute process in async mode
    request_json = {"inputs": [{"id": "name", "value": "hello"}], "mode": "async"}
    result = w.execute('hello-world', json=request_json)
    assert result.outputs is None
    assert 'processes/hello-world/jobs' in result.location
    assert result.jobID is not None

    # get job status
    # status = w.status('hello-world', result.job_id)
