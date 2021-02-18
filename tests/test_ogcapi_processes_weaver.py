from tests.utils import service_ok

import pytest

from owslib.ogcapi.processes import Processes

SERVICE_URL = 'https://ogc-ades.crim.ca/ADES/'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_ogcapi_processes_weaver():
    w = Processes(SERVICE_URL)

    assert w.url == 'https://ogc-ades.crim.ca/ADES/'
    assert w.url_query_string is None

    # TODO: RuntimeError: Did not find service-desc link
    api = w.api()
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
    # TODO: response not as expected {'process': {'id': 'ColibriFlyingpigeon_SubsetBbox'}}
    # should be {'id': 'ColibriFlyingpigeon_SubsetBbox'}
    # process = w.process_description('ColibriFlyingpigeon_SubsetBbox')
    # print(process)
    # assert process['process']['id'] == 'ColibriFlyingpigeon_SubsetBbox'
    # assert process['process']['title'] == 'ColibriFlyingpigeon_SubsetBbox'
    # assert "An example process that takes a name as input" in process['process']['description']
