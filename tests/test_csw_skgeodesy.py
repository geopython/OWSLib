from tests.utils import service_ok

import pytest

from owslib.csw import CatalogueServiceWeb

SERVICE_URL = 'https://zbgisws.skgeodesy.sk/zbgiscsw/service.svc/get'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason='service is unreachable')
def test_csw_skgeodsy():
    c = CatalogueServiceWeb(SERVICE_URL)

    assert sorted([op.name for op in c.operations]) == [
        'DescribeRecord',
        'GetCapabilities',
        'GetRecordById',
        'GetRecords',
        'Transaction']

    grop = c.get_operation_by_name('GetRecords')
    assert grop.name == 'GetRecords'

    c.getrecords2(typenames='csw:Record gmd:MD_Metadata')
    assert c.results.get('returned') > 0
    assert c.results.get('nextrecord') > 0
    assert c.results.get('matches') > 0
