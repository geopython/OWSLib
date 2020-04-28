from tests.utils import service_ok

import pytest

from owslib.ogcapi.records import Records

SERVICE_URL = 'http://52.170.144.218:8000'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_ogcapi_records_pygeoapi():
    w = Records(SERVICE_URL)

    assert w.url == 'http://52.170.144.218:8000/'
    assert w.url_query_string is None

    api = w.api()
    assert api['components']['parameters'] is not None
    paths = api['paths']
    assert paths is not None
    assert paths['/collections/msc-wis-dcpc'] is not None

    conformance = w.conformance()
    assert len(conformance['conformsTo']) == 8

    collections = w.collections()
    assert len(collections) > 0

    msc_wis_dcpc = w.collection('msc-wis-dcpc')
    assert msc_wis_dcpc['id'] == 'msc-wis-dcpc'
    assert msc_wis_dcpc['title'] == 'MSC WIS DCPC'
    assert msc_wis_dcpc['description'] == 'MSC WIS DCPC'

    msc_wis_dcpc_queryables = w.collection_queryables('msc-wis-dcpc')
    assert len(msc_wis_dcpc_queryables['queryables']) == 7

    # Minimum of limit param is 1
    with pytest.raises(RuntimeError):
        msc_wis_dcpc_query = w.collection_items('msc-wis-dcpc', limit=0)

    msc_wis_dcpc_query = w.collection_items('msc-wis-dcpc', limit=1)
    assert msc_wis_dcpc_query['numberMatched'] == 178
    assert msc_wis_dcpc_query['numberReturned'] == 1
    assert len(msc_wis_dcpc_query['features']) == 1

    msc_wis_dcpc_query = w.collection_items('msc-wis-dcpc', q='metar')
    assert msc_wis_dcpc_query['numberMatched'] == 2
    assert msc_wis_dcpc_query['numberReturned'] == 2
    assert len(msc_wis_dcpc_query['features']) == 2
