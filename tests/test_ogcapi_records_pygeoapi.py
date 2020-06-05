from tests.utils import service_ok

import pytest

from owslib.ogcapi.records import Records

SERVICE_URL = 'https://dev.api.weather.gc.ca/msc-wis-dcpc'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_ogcapi_records_pygeoapi():
    w = Records(SERVICE_URL)

    assert w.url == 'https://dev.api.weather.gc.ca/msc-wis-dcpc'
    assert w.url_query_string is None

    api = w.api()
    assert api['components']['parameters'] is not None
    paths = api['paths']
    assert paths is not None
    assert paths['/collections/discovery-metadata'] is not None

    conformance = w.conformance()
    assert len(conformance['conformsTo']) == 8

    collections = w.collections()
    assert len(collections) > 0

    msc_wis_dcpc = w.collection('discovery-metadata')
    assert msc_wis_dcpc['id'] == 'discovery-metadata'
    assert msc_wis_dcpc['title'] == 'MSC WIS DCPC'
    assert msc_wis_dcpc['description'] == 'MSC WIS DCPC'

    msc_wis_dcpc_queryables = w.collection_queryables('discovery-metadata')
    assert len(msc_wis_dcpc_queryables['queryables']) == 7

    # Minimum of limit param is 1
    with pytest.raises(RuntimeError):
        msc_wis_dcpc_query = w.collection_items('discovery-metadata', limit=0)

    msc_wis_dcpc_query = w.collection_items('discovery-metadata', limit=1)
    assert msc_wis_dcpc_query['numberMatched'] == 178
    assert msc_wis_dcpc_query['numberReturned'] == 1
    assert len(msc_wis_dcpc_query['features']) == 1

    msc_wis_dcpc_query = w.collection_items('discovery-metadata', q='metar')
    assert msc_wis_dcpc_query['numberMatched'] == 2
    assert msc_wis_dcpc_query['numberReturned'] == 2
    assert len(msc_wis_dcpc_query['features']) == 2
