from tests.utils import cast_tuple_int_list, scratch_file
from tests.utils import service_ok
from owslib.wcs import WebCoverageService

import pytest

SERVICE_URL = 'http://www.idee.es/wcs/IDEE-WCS-UTM30N/wcsServlet'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WCS service is unreachable")
def test_wcs_idee():
    """
    COWS Web Coverage Service
    WCS Version 1.0.0

    rewritten doctest/wcs_idee.txt
    """
    wcs = WebCoverageService(SERVICE_URL)
    assert wcs.version == '1.0.0'
    assert wcs.url == SERVICE_URL
    assert wcs.identification.title == 'WCS UTM30N - MDT Peninsula y Baleares'
    assert wcs.identification.service == 'IDEE-WCS-UTM30N'
    assert wcs.provider.name == u'Instituto Geogr\xe1fico Nacional'
    assert sorted(wcs.contents.keys()) == [
        'MDT1000_peninsula_baleares',
        'MDT1000_peninsula_baleares_aspecto',
        'MDT1000_peninsula_baleares_pendientes',
        'MDT25_peninsula_ZIP',
        'MDT25_peninsula_aspecto',
        'MDT25_peninsula_pendientes',
        'MDT500_peninsula_baleares',
        'MDT500_peninsula_baleares_aspecto',
        'MDT500_peninsula_baleares_pendientes',
        'MDT_peninsula_baleares',
        'MDT_peninsula_baleares_aspecto',
        'MDT_peninsula_baleares_pendientes']
    cvg = wcs['MDT25_peninsula_pendientes']
    assert cvg.title == 'MDT25 Pendientes Peninsula'
    assert cast_tuple_int_list(cvg.boundingBoxWGS84) == [-8, 35, 3, 43]
    assert cvg.timelimits == []
    assert sorted(cvg.supportedFormats) == ['AsciiGrid', 'FloatGrid_Zip', 'GeoTIFF']
    assert sorted(map(lambda x: x.getcode(), cvg.supportedCRS)) == [
        'EPSG:23028',
        'EPSG:23029',
        'EPSG:23030',
        'EPSG:23030',
        'EPSG:23031',
        'EPSG:4230',
        'EPSG:4326']
    output = wcs.getCoverage(
        identifier='MDT25_peninsula_pendientes',
        bbox=(600000, 4200000, 601000, 4201000),
        crs='EPSG:23030', format='AsciiGrid', resX=25, resY=25)
    f = open(scratch_file('test_idee.grd'), 'wb')
    bytes_written = f.write(output.read())
    f.close()
