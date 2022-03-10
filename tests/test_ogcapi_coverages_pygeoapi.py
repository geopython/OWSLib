from tests.utils import service_ok

import pytest

from owslib.ogcapi.coverages import Coverages

SERVICE_URL = 'https://dev.api.weather.gc.ca/coverages-demo'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_ogcapi_coverages_pygeoapi():
    w = Coverages(SERVICE_URL)

    assert w.url == 'https://dev.api.weather.gc.ca/coverages-demo/'
    assert w.url_query_string is None

    api = w.api()
    assert api['components']['parameters'] is not None
    paths = api['paths']
    assert paths is not None
    assert paths['/collections/gdps-temperature'] is not None

    conformance = w.conformance()
    assert len(conformance['conformsTo']) > 1

    collections = w.collections()
    assert len(collections) > 0

    coverages = w.coverages()
    assert len(coverages) > 0

    gdps = w.collection('gdps-temperature')
    assert gdps['id'] == 'gdps-temperature'
    assert gdps['title'] == 'Global Deterministic Prediction System sample'
    assert gdps['description'] == 'Global Deterministic Prediction System sample'  # noqa

    domainset = w.coverage_domainset('gdps-temperature')

    assert domainset['generalGrid']['axisLabels'] == ['x', 'y']
    assert domainset['generalGrid']['gridLimits']['axisLabels'] == ['i', 'j']

    rangetype = w.coverage_rangetype('gdps-temperature')
    assert len(rangetype['field']) == 1
    assert rangetype['field'][0]['definition'] == 'float64'

    with pytest.raises(RuntimeError):
        w.coverage('gdps-temperature', properties=[8])
