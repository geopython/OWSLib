from tests.utils import service_ok

import pytest

from owslib.ogcapi.processes import Processes

SERVICE_URL = 'http://geoprocessing.demo.52north.org:8080/javaps/rest/'


@pytest.mark.xfail
@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_ogcapi_processes_52n():
    w = Processes(SERVICE_URL)

    assert w.url == 'http://geoprocessing.demo.52north.org:8080/javaps/rest/'
    assert w.url_query_string is None

    # TODO: RuntimeError: Did not find service-desc link
    # api = w.api()
    # assert api['components']['parameters'] is not None
    # paths = api['paths']
    # assert paths is not None
    # assert paths['/processes/hello-world'] is not None

    conformance = w.conformance()
    assert len(conformance['conformsTo']) == 5

    # list processes
    processes = w.processes()
    assert len(processes) > 0

    # process description
    echo = w.process_description('org.n52.javaps.test.EchoProcess')
    assert echo['id'] == 'org.n52.javaps.test.EchoProcess'
    assert echo['title'] == 'org.n52.javaps.test.EchoProcess'
    # assert "An example process that takes a name as input" in echo['description']

    # running jobs
    jobs = w.job_list('org.n52.javaps.test.EchoProcess')
    assert len(jobs) >= 0

    # TODO: post request not allowed at 52n?
