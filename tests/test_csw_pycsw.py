from tests.utils import service_ok

import pytest

from owslib.csw import CatalogueServiceWeb as cs

SERVICE_URL = 'http://demo.pycsw.org/cite/csw'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_csw_pycsw():
    c = cs(SERVICE_URL)
    assert c.updateSequence is not None
    assert c.version == '2.0.2'
    assert c.identification.title == 'pycsw OGC CITE demo and Reference Implementation'
    assert c.constraints['MaxRecordDefault'].values[0] == '10'
    c.getrecords2()
    assert c.results.get('returned') > 0
    assert c.results.get('nextrecord') > 0
    assert c.results.get('matches') > 0
