from owslib.wfs import WebFeatureService
from owslib.util import ServiceException
from owslib.fes import PropertyIsLike, etree
from urllib.parse import urlparse
from tests.utils import resource_file, sorted_url_query, service_ok
import json
import pytest

SERVICE_URL = 'https://services.ga.gov.au/gis/stratunits/ows'

def test_caps_info():
    getcapsin = open(resource_file("wfs_HSRS_GetCapabilities_1_1_0.xml"), "rb").read()
    wfs = WebFeatureService('http://gis.bnhelp.cz/ows/crwfs', xml=getcapsin, version='1.1.0')
    assert wfs.identification.service == 'OGC WFS'
    assert wfs.identification.version == '1.1.0'
    assert wfs.identification.title == 'Help Service Gazeteer'
    assert wfs.identification.abstract == 'Vyhledavani sidel WFS'
    assert wfs.identification.keywords == ['Czech republic', 'gazeeteer']
    assert wfs.identification.fees == 'none'
    assert wfs.identification.accessconstraints == 'for non profit use'
    assert wfs.provider.name == 'Help Service Remote Sensing, ltd.'
    assert wfs.provider.url == 'http://www.hsrs.cz'
    assert wfs.provider.contact.email is None
    assert wfs.provider.contact.phone is None
    assert wfs.provider.contact.name == 'Stanislav Hol\xfd'
    assert wfs.provider.contact.organization is None
    assert wfs.provider.contact.city is None
    assert wfs.provider.contact.region is None
    assert wfs.provider.contact.postcode is None
    assert wfs.provider.contact.country is None


def test_getfeature():
    getcapsin = open(resource_file("wfs_HSRS_GetCapabilities_1_1_0.xml"), "rb").read()
    wfs = WebFeatureService('http://gis.bnhelp.cz/ows/crwfs', xml=getcapsin, version='1.1.0')

    assert sorted(wfs.contents.keys()) == ['kraje', 'nuts1', 'nuts2', 'nuts3', 'okresy', 'orp', 'sidla', 'states']
    assert wfs.contents['okresy'].crsOptions[0].getcodeurn() == 'urn:ogc:def:crs:EPSG::4326'
    assert sorted_url_query(wfs.getGETGetFeatureRequest(typename=['okresy'], maxfeatures=2)) == [
        'maxfeatures=2', 'request=GetFeature', 'service=WFS', 'typename=okresy', 'version=1.1.0']

    assert sorted_url_query(wfs.getGETGetFeatureRequest(
        typename=['okresy'], maxfeatures=2, bbox=[15, 49, 16, 51, 'urn:ogc:def:crs:EPSG:4326'])) == [
        'bbox=49%2C15%2C51%2C16%2Curn%3Aogc%3Adef%3Acrs%3AEPSG%3A%3A4326',
        'maxfeatures=2', 'request=GetFeature', 'service=WFS', 'typename=okresy', 'version=1.1.0']

    assert sorted_url_query(wfs.getGETGetFeatureRequest(
        typename=['okresy'], maxfeatures=2, bbox=[-685336, -993518, -684996, -993285])) == [
        'bbox=-993518%2C-685336%2C-993285%2C-684996%2Curn%3Aogc%3Adef%3Acrs%3AEPSG%3A%3A4326',
        'maxfeatures=2', 'request=GetFeature', 'service=WFS', 'typename=okresy', 'version=1.1.0']


def test_verbOptions_wfs_100():
    with open(resource_file("wfs_dov_getcapabilities_100_verbOptions.xml"), "rb") as f:
        getcapsin = f.read()
    wfs = WebFeatureService('http://gis.bnhelp.cz/ows/crwfs', xml=getcapsin, version='1.0.0')
    verbOptions = [cm.verbOptions for cm in wfs.contents.values()]
    assert len(verbOptions[0]) == 2


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WFS service is unreachable")
def test_outputformat_wfs_100():
    wfs = WebFeatureService(SERVICE_URL, version='1.0.0')
    feature = wfs.getfeature(
        typename=['stratunit:StratigraphicUnit'], maxfeatures=1, propertyname=None, outputFormat='application/json')
    assert len(json.loads(feature.read())['features']) == 1


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WFS service is unreachable")
def test_outputformat_wfs_110():
    wfs = WebFeatureService(SERVICE_URL, version='1.1.0')
    feature = wfs.getfeature(
        typename=['stratunit:StratigraphicUnit'], maxfeatures=1, propertyname=None, outputFormat='application/json')
    assert len(json.loads(feature.read())['features']) == 1


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WFS service is unreachable")
def test_outputformat_wfs_200():
    wfs = WebFeatureService(SERVICE_URL, version='2.0.0')
    feature = wfs.getfeature(
        typename=['stratunit:StratigraphicUnit'], maxfeatures=1, propertyname=None, outputFormat='application/json')
    assert len(json.loads(feature.read())['features']) == 1


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WFS service is unreachable")
def test_srsname_wfs_100():
    wfs = WebFeatureService(SERVICE_URL, version='1.0.0')
    # ServiceException: Unable to support srsName: EPSG:99999999
    with pytest.raises(ServiceException):
        feature = wfs.getfeature(
            typename=['stratunit:StratigraphicUnit'], maxfeatures=1, propertyname=None, outputFormat='application/json',
            srsname="EPSG:99999999")

    wfs = WebFeatureService(SERVICE_URL, version='1.0.0')
    feature = wfs.getfeature(
        typename=['stratunit:StratigraphicUnit'], maxfeatures=1, propertyname=None, outputFormat='application/json',
        srsname="urn:x-ogc:def:crs:EPSG:4326")
    assert len(json.loads(feature.read())['features']) == 1


@pytest.mark.xfail
@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WFS service is unreachable")
def test_srsname_wfs_110():
    wfs = WebFeatureService(SERVICE_URL, version='1.1.0')
    # ServiceException: Unable to support srsName: EPSG:99999999
    with pytest.raises(ServiceException):
        feature = wfs.getfeature(
            typename=['stratunit:StratigraphicUnit'], maxfeatures=1, propertyname=None, outputFormat='application/json',
            srsname="EPSG:99999999")

    wfs = WebFeatureService(SERVICE_URL, version='1.1.0')
    feature = wfs.getfeature(
        typename=['stratunit:StratigraphicUnit'], maxfeatures=1, propertyname=None, outputFormat='application/json',
        srsname="urn:x-ogc:def:crs:EPSG:4326")
    assert len(json.loads(feature.read())['features']) == 1


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WFS service is unreachable")
def test_srsname_wfs_200():
    wfs = WebFeatureService(SERVICE_URL, version='2.0.0')
    # ServiceException: Unable to support srsName: EPSG:99999999
    with pytest.raises(ServiceException):
        feature = wfs.getfeature(
            typename=['stratunit:StratigraphicUnit'], maxfeatures=1, propertyname=None, outputFormat='application/json',
            srsname="EPSG:99999999")

    wfs = WebFeatureService(SERVICE_URL, version='2.0.0')
    feature = wfs.getfeature(
        typename=['stratunit:StratigraphicUnit'], maxfeatures=1, propertyname=None, outputFormat='application/json',
        srsname="urn:x-ogc:def:crs:EPSG:4326")
    assert len(json.loads(feature.read())['features']) == 1


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WFS service is unreachable")
def test_schema_wfs_100():
    wfs = WebFeatureService(SERVICE_URL, version='1.0.0')
    schema = wfs.get_schema('stratunit:StratigraphicUnit')
    assert len(schema['properties']) == 33
    assert schema['properties']['DESCRIPTION'] == 'string'
    assert schema['geometry'] is None


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WFS service is unreachable")
def test_schema_wfs_110():
    wfs = WebFeatureService(SERVICE_URL, version='1.1.0')
    schema = wfs.get_schema('stratunit:StratigraphicUnit')
    assert len(schema['properties']) == 33
    assert schema['properties']['DESCRIPTION'] == 'string'
    assert schema['geometry'] is None


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WFS service is unreachable")
def test_schema_wfs_200():
    wfs = WebFeatureService(SERVICE_URL, version='2.0.0')
    schema = wfs.get_schema('stratunit:StratigraphicUnit')
    assert len(schema['properties']) == 33
    assert schema['properties']['DESCRIPTION'] == 'string'
    assert schema['geometry'] is None


@pytest.mark.online
@pytest.mark.skip(reason='HTTP 403 issue. See issue #956')
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WFS service is unreachable")
def test_xmlfilter_wfs_110():
    wfs = WebFeatureService(SERVICE_URL, version='1.1.0')
    filter_prop = PropertyIsLike(propertyname='stratunit:GEOLOGICHISTORY', literal='Cisuralian - Guadalupian',
        matchCase=True)

    filterxml = etree.tostring(filter_prop.toXML()).decode("utf-8")

    getfeat_params = {'typename': 'stratunit:StratigraphicUnit', 'filter': filterxml}

    response = wfs.getfeature(**getfeat_params).read()
    assert b'<stratunit:NAME>Ellen Harkins carbonaceous shale</stratunit:NAME>' in response


@pytest.mark.online
@pytest.mark.skip(reason='HTTP 403 issue. See issue #956')
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="WFS service is unreachable")
def test_xmlfilter_wfs_200():
    wfs = WebFeatureService(SERVICE_URL,  version='2.0.0')
    filter_prop = PropertyIsLike(propertyname='stratunit:geologichistory', literal='Cisuralian - Guadalupian',
        matchCase=True)

    filterxml = etree.tostring(filter_prop.toXML()).decode("utf-8")

    getfeat_params = {'typename': 'stratunit:StratigraphicUnit', 'filter': filterxml}

    response = wfs.getfeature(**getfeat_params).read()
    assert b'<stratunit:NAME>Boolgeeda Iron Formation</stratunit:NAME>' in response

