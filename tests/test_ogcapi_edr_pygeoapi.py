from tests.utils import service_ok

import pytest

from owslib.ogcapi.edr import EnvironmentalDataRetrieval

SERVICE_URL = 'https://demo.pygeoapi.io/master/'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_ogcapi_coverages_pygeoapi():
    w = EnvironmentalDataRetrieval(SERVICE_URL)

    assert w.url == SERVICE_URL
    assert w.url_query_string is None

    api = w.api()
    assert api['components']['parameters'] is not None
    paths = api['paths']
    assert paths is not None
    assert paths['/collections/icoads-sst'] is not None

    conformance = w.conformance()
    assert len(conformance['conformsTo']) > 1

    collections = w.collections()
    assert len(collections) > 0

    datas = w.data()
    assert len(datas) > 0

    icoads = w.collection('icoads-sst')
    assert icoads['id'] == 'icoads-sst'
    assert icoads['title'] == 'International Comprehensive Ocean-Atmosphere Data Set (ICOADS)'  # noqa
    assert icoads['description'] == 'International Comprehensive Ocean-Atmosphere Data Set (ICOADS)'  # noqa

    parameter_names = icoads['parameter_names'].keys()
    assert sorted(parameter_names) == ['AIRT', 'SST', 'UWND', 'VWND']

    response = w.query_data('icoads-sst', 'position', coords='POINT(-75 45)')
    assert isinstance(response, dict)
