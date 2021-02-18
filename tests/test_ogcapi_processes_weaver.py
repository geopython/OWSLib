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

    # TODO: RuntimeError: Did not find service-desc link (https://github.com/crim-ca/weaver/issues/200)
    # api = w.api()
    # assert api['components']['parameters'] is not None
    # paths = api['paths']
    # assert paths is not None
    # assert paths['/processes/hello-world'] is not None

    conformance = w.conformance()
    assert len(conformance['conformsTo']) > 0 and all(isinstance(c, str) for c in conformance['conformsTo'])

    # list processes
    processes = w.processes()
    assert len(processes) > 0

    # process description
    # following are builtin processes and should always be available
    for pid in ['file2string_array', 'jsonarray2netcdf', 'metalink2netcdf']:
        process = w.process_description(pid)
        proc_desc = process['process']
        assert proc_desc['id'] == pid
        assert 'inputs' in proc_desc and isinstance(proc_desc['inputs'], list) and len(proc_desc['inputs'])
        assert all('id' in p_in and isinstance(p_in['id'], str) for p_in in proc_desc['inputs'])
        assert 'outputs' in proc_desc and isinstance(proc_desc['outputs'], list) and len(proc_desc['outputs'])
        assert all('id' in p_out and isinstance(p_out['id'], str) for p_out in proc_desc['outputs'])
