from tests.utils import scratch_file
from tests.utils import service_ok
from owslib.wcs import WebCoverageService


import pytest
import datetime

SERVICE_URL = 'http://ows.rasdaman.org/rasdaman/ows'


@pytest.mark.online
@pytest.mark.skip(reason="WCS service is broken (#494)")
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WCS service is unreachable")
def test_wcs_200():
    """
    Web Coverage Service
    WCS Version 2.0.x

    rewritten doctest/wcs_200.txt
    """
    wcs = WebCoverageService(SERVICE_URL, version="2.0.1")
    assert wcs.version == '2.0.1'
    assert wcs.url == SERVICE_URL
    assert wcs.identification.title == 'rasdaman'
    assert wcs.identification.service == 'OGC WCS'
    assert wcs.provider.name == 'Jacobs University Bremen'
    assert 'AvgLandTemp' in wcs.contents.keys()
    assert len(wcs.contents.keys()) >= 20
    cvg = wcs.contents['AvgLandTemp']
    assert cvg.boundingboxes[0]['bbox'] == (-90, -180,
                                            90, 180)
    assert cvg.timelimits == [datetime.datetime(2000, 2, 1, 0, 0), datetime.datetime(2015, 6, 1, 0, 0)]
    assert cvg.timepositions[0:5] == [datetime.datetime(2000, 2, 1, 0, 0), datetime.datetime(2000, 3, 1, 0, 0),
                                      datetime.datetime(2000, 4, 1, 0, 0), datetime.datetime(2000, 5, 1, 0, 0),
                                      datetime.datetime(2000, 6, 1, 0, 0)]
    assert cvg.supportedFormats == ['application/gml+xml', 'image/jpeg', 'image/png', 'image/tiff', 'image/bmp',
                                    'image/jp2', 'application/netcdf', 'text/csv', 'application/json',
                                    'application/dem', 'application/x-ogc-dted', 'application/x-ogc-ehdr',
                                    'application/x-ogc-elas', 'application/x-ogc-envi', 'application/x-ogc-ers',
                                    'application/x-ogc-fit', 'application/x-ogc-fits', 'image/gif',
                                    'application/x-netcdf-gmt', 'application/x-ogc-gs7bg', 'application/x-ogc-gsag',
                                    'application/x-ogc-gsbg', 'application/x-ogc-gta', 'application/x-ogc-hf2',
                                    'application/x-erdas-hfa', 'application/x-ogc-ida', 'application/x-ogc-ingr',
                                    'application/x-ogc-isis2', 'application/x-erdas-lan', 'application/x-ogc-mff2',
                                    'application/x-ogc-nitf', 'application/x-ogc-paux', 'application/x-ogc-pcidsk',
                                    'application/x-ogc-pcraster', 'application/x-ogc-pdf', 'application/x-ogc-pnm',
                                    'text/x-r', 'application/x-ogc-rmf', 'image/x-sgi', 'application/x-ogc-vrt',
                                    'image/xpm', 'application/x-ogc-zmap']
    assert cvg.grid.axislabels == ['Lat', 'Long', 'ansi']
    assert cvg.grid.dimension == 3
    assert cvg.grid.lowlimits == ['0', '0', '0']
    assert cvg.grid.highlimits == ['1799', '3599', '184']
    covID = 'AvgLandTemp'
    time_subset = ("ansi", "2000-02-01T00:00:00Z")
    lat_subset = ('Lat', 40, 50)
    long_subset = ('Long', -10, 0)
    formatType = 'application/netcdf'
    output = wcs.getCoverage(identifier=[covID], format=formatType, subsets=[long_subset, lat_subset, time_subset])
    f = open(scratch_file('test_wcs_200.nc'), 'wb')
    bytes_written = f.write(output.read())
    f.close()
