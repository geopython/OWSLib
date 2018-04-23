from tests.utils import scratch_file
from tests.utils import service_ok
from owslib.wcs import WebCoverageService


import pytest
import datetime

SERVICE_URL = 'http://earthserver.pml.ac.uk/rasdaman/ows'


@pytest.mark.online
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
    assert wcs.identification.title == 'Marine Science Data Service'
    assert wcs.identification.service == 'OGC WCS'
    assert wcs.provider.name == 'Plymouth Marine Laboratory'
    assert 'OCCCI_V3_1_chlor_a_monthly' in wcs.contents.keys()
    assert len(wcs.contents.keys()) >= 29
    cvg = wcs.contents['OCCCI_V3_1_chlor_a_monthly']
    assert cvg.boundingboxes[0]['bbox'] == (-89.9999973327159, -180.00000333371918,
                                            89.9999973327159, 180.00000333371918)
    assert cvg.timelimits == [datetime.datetime(1997, 9, 4, 0, 0), datetime.datetime(2016, 12, 1, 0, 0)]
    assert cvg.timepositions[0:5] == [datetime.datetime(1997, 9, 4, 0, 0), datetime.datetime(1997, 10, 1, 0, 0),
                                      datetime.datetime(1997, 11, 1, 0, 0), datetime.datetime(1997, 12, 1, 0, 0),
                                      datetime.datetime(1998, 1, 1, 0, 0)]
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
    assert cvg.grid.highlimits == ['4319', '8639', '231']
    covID = 'OCCCI_V3_1_chlor_a_monthly'
    time_subset = ("ansi", "2004-06-01T00:00:00Z")
    lat_subset = ('Lat', 40, 50)
    long_subset = ('Long', -10, 0)
    formatType = 'application/netcdf'
    output = wcs.getCoverage(identifier=[covID], format=formatType, subsets=[long_subset, lat_subset, time_subset])
    f = open(scratch_file('test_wcs_200.nc'), 'wb')
    bytes_written = f.write(output.read())
    f.close()
