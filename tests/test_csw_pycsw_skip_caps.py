from tests.utils import service_ok

import pytest

from owslib.csw import CatalogueServiceWeb as cs

SERVICE_URL = 'http://demo.pycsw.org/cite/csw'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_csw_pycsw_skip_caps():
    c = cs(SERVICE_URL, skip_caps=True)
    c.getrecords2()
    assert c.results.get('returned') > 0
    assert c.results.get('nextrecord') > 0
    assert c.results.get('matches') > 0
