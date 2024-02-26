from tests.utils import service_ok

import pytest

from owslib.ogcapi.coverages import Coverages

SERVICE_URL = 'https://demo.pygeoapi.io/master/'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_ogcapi_coverages_pygeoapi():
    w = Coverages(SERVICE_URL)

    assert w.url == SERVICE_URL
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
    assert gdps['extent']['spatial']['grid'][0]['cellsCount'] == 2400
    assert gdps['extent']['spatial']['grid'][0]['resolution'] == 0.15000000000000002  # noqa
    assert gdps['extent']['spatial']['grid'][1]['cellsCount'] == 1201
    assert gdps['extent']['spatial']['grid'][1]['resolution'] == 0.15

    schema = w.collection_schema('gdps-temperature')
    assert len(schema['properties']) == 1
    assert schema['properties']['1']['title'] == 'Temperature [C]'
    assert schema['properties']['1']['type'] == 'number'
    assert schema['properties']['1']['x-ogc-unit'] == '[C]'

    with pytest.raises(RuntimeError):
        w.coverage('gdps-temperature', properties=[8])
