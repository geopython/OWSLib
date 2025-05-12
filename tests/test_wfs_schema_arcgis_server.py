import pytest

import owslib
from owslib.etree import etree
from owslib.wfs import WebFeatureService
from tests.utils import service_ok

WFS_SERVICE_URL = 'https://geoportal.stadt-koeln.de/arcgis/services/basiskarten/adressen_stadtteil/MapServer/WFSServer?SERVICE=WFS&request=GetCapabilities'


@pytest.fixture
def mp_wfs_110(monkeypatch):
    """Monkeypatch the call to the remote GetCapabilities request of WFS
    version 1.1.0.

    Parameters
    ----------
    monkeypatch : pytest.fixture
        PyTest monkeypatch fixture.
    """
    def read(*args, **kwargs):
        with open('tests/resources/wfs_koeln_arcgis_getcapabilities_110.xml', 'r') as f:
            data = f.read()
            if type(data) is not bytes:
                data = data.encode('utf-8')
            data = etree.fromstring(data)
        return data

    monkeypatch.setattr(
        owslib.feature.common.WFSCapabilitiesReader, 'read', read)


@pytest.fixture
def mp_wfs_200(monkeypatch):
    """Monkeypatch the call to the remote GetCapabilities request of WFS
    version 2.0.0.

    Parameters
    ----------
    monkeypatch : pytest.fixture
        PyTest monkeypatch fixture.
    """
    def read(*args, **kwargs):
        with open('tests/resources/wfs_koeln_arcgis_getcapabilities_200.xml', 'r') as f:
            data = f.read()
            if type(data) is not bytes:
                data = data.encode('utf-8')
            data = etree.fromstring(data)
        return data

    monkeypatch.setattr(
        owslib.feature.common.WFSCapabilitiesReader, 'read', read)


@pytest.fixture()
def mp_remote_describefeaturetype(monkeypatch):
    """Monkeypatch the call to the remote DescribeFeatureType request.

    Returns a standard DescribeFeatureType response.

    Parameters
    ----------
    monkeypatch : pytest.fixture
        PyTest monkeypatch fixture.
    """
    def __remote_describefeaturetype(*args, **kwargs):
        with open('tests/resources/wfs_koeln_arcgis_describefeaturetype_110.xml', 'r') as f:
            data = f.read()
            if type(data) is not bytes:
                data = data.encode('utf-8')
            data = etree.fromstring(data)
        return data

    monkeypatch.setattr(owslib.feature.schema,
                        '_get_remote_describefeaturetype',
                        __remote_describefeaturetype)


class TestOnline(object):
    """Class grouping online tests for the WFS get_schema method."""

    @pytest.mark.xfail
    @pytest.mark.online
    @pytest.mark.skipif(not service_ok(WFS_SERVICE_URL),
                       reason="WFS service is unreachable")
    @pytest.mark.parametrize("wfs_version", ["1.1.0", "2.0.0"])
    def test_get_schema(self, wfs_version):
        """Test the get_schema method for a standard schema."""
        wfs = WebFeatureService(WFS_SERVICE_URL, version=wfs_version)
        schema = wfs.get_schema('adressen_stadtteil:Blumenberg')

    @pytest.mark.xfail
    @pytest.mark.online
    @pytest.mark.skipif(not service_ok(WFS_SERVICE_URL),
                       reason="WFS service is unreachable")
    @pytest.mark.parametrize("wfs_version", ["1.1.0", "2.0.0"])
    def test_schema_result(self, wfs_version):
        """Test whether the output from get_schema is a wellformed dictionary."""
        wfs = WebFeatureService(WFS_SERVICE_URL, version=wfs_version)
        schema = wfs.get_schema('adressen_stadtteil:Blumenberg')
        assert isinstance(schema, dict)

        assert 'properties' in schema or 'geometry' in schema

        if 'geometry' in schema:
            assert 'geometry_column' in schema

        if 'properties' in schema:
            assert isinstance(schema['properties'], dict)

        assert 'required' in schema
        assert isinstance(schema['required'], list)


class TestOffline(object):
    """Class grouping offline tests for the WFS get_schema method."""

    def test_get_schema(self, mp_wfs_110, mp_remote_describefeaturetype):
        """Test the get_schema method for a standard schema.

        Parameters
        ----------
        mp_wfs_110 : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.
        mp_remote_describefeaturetype : pytest.fixture
            Monkeypatch the call to the remote DescribeFeatureType request.
        """
        wfs = WebFeatureService(WFS_SERVICE_URL, version='1.1.0')
        schema = wfs.get_schema('adressen_stadtteil:Blumenberg')

    def test_schema_result(self, mp_wfs_110, mp_remote_describefeaturetype):
        """Test whether the output from get_schema is a wellformed dictionary.

        Parameters
        ----------
        mp_wfs_110 : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.
        mp_remote_describefeaturetype : pytest.fixture
            Monkeypatch the call to the remote DescribeFeatureType request.
        """
        wfs = WebFeatureService(WFS_SERVICE_URL, version='1.1.0')
        schema = wfs.get_schema('adressen_stadtteil:Blumenberg')
        assert isinstance(schema, dict)

        assert 'properties' in schema or 'geometry' in schema

        if 'geometry' in schema:
            assert 'geometry_column' in schema

        if 'properties' in schema:
            assert isinstance(schema['properties'], dict)

        assert 'required' in schema
        assert isinstance(schema['required'], list)
