
import pytest

from owslib.namespaces import Namespaces

def test_namespaces():
    ns = Namespaces()

    assert ns.get_namespace('csw') == 'http://www.opengis.net/cat/csw/2.0.2'

    x = ns.get_namespaces(['csw','gmd','fes'])
    assert x == {'csw': 'http://www.opengis.net/cat/csw/2.0.2', 'fes': 'http://www.opengis.net/fes/2.0', 'gmd': 'http://www.isotc211.org/2005/gmd'}

    ns.get_namespaces()

    assert ns.get_versioned_namespace('ows') == 'http://www.opengis.net/ows'

    assert ns.get_versioned_namespace('ows','1.0.0') == 'http://www.opengis.net/ows'

    assert ns.get_versioned_namespace('ows','1.1.0') ==  'http://www.opengis.net/ows/1.1'

    assert ns.get_versioned_namespace('ows','2.0.0') == 'http://www.opengis.net/ows/2.0'

    assert ns.get_namespaces('csw') == {'csw': 'http://www.opengis.net/cat/csw/2.0.2'}

    assert ns.get_namespace('csw') == 'http://www.opengis.net/cat/csw/2.0.2'

    assert ns.get_namespace('sa') == 'http://www.opengis.net/sampling/1.0'

    # 'om300' does not exist as a namespace, so the below will return nothing
    assert ns.get_namespace('om300') is None

    # CSW 3.1.1 doesn't exist, so the below will return nothing
    assert ns.get_versioned_namespace('csw','3.1.1') is None


    # Invalid Usage Tests

    with pytest.raises(TypeError):
        ns.get_namespace()

    with pytest.raises(TypeError):
        ns.get_versioned_namespace()
