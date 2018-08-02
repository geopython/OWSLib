import pytest

import owslib
from owslib.etree import etree
from owslib.wfs import WebFeatureService
from owslib.wms import WebMapService
from tests.utils import service_ok


WMS_SERVICE_URL = 'https://www.dov.vlaanderen.be/geoserver/gw_meetnetten/wms'
WFS_SERVICE_URL = 'https://www.dov.vlaanderen.be/geoserver/gw_meetnetten/wfs'


@pytest.fixture
def mp_wfs_100_nometadata(monkeypatch):
    """Monkeypatch the call to the remote GetCapabilities request of WFS
    version 1.0.0, not containing MetadataURLs.

    Parameters
    ----------
    monkeypatch : pytest.fixture
        PyTest monkeypatch fixture.

    """
    def read(*args, **kwargs):
        with open('tests/resources/wfs_dov_getcapabilities_100_nometadata.xml',
                  'r') as f:
            data = f.read()
            if type(data) is not bytes:
                data = data.encode('utf-8')
            data = etree.fromstring(data)
        return data

    monkeypatch.setattr(
        owslib.feature.common.WFSCapabilitiesReader, 'read', read)


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
        with open('tests/resources/wfs_dov_getcapabilities_110.xml', 'r') as f:
            data = f.read()
            if type(data) is not bytes:
                data = data.encode('utf-8')
            data = etree.fromstring(data)
        return data

    monkeypatch.setattr(
        owslib.feature.common.WFSCapabilitiesReader, 'read', read)

@pytest.fixture
def mp_wfs_110_nometadata(monkeypatch):
    """Monkeypatch the call to the remote GetCapabilities request of WFS
    version 1.1.0, not containing MetadataURLs.

    Parameters
    ----------
    monkeypatch : pytest.fixture
        PyTest monkeypatch fixture.

    """
    def read(*args, **kwargs):
        with open('tests/resources/wfs_dov_getcapabilities_110_nometadata.xml',
                  'r') as f:
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
        with open('tests/resources/wfs_dov_getcapabilities_200.xml',
                  'r') as f:
            data = f.read()
            if type(data) is not bytes:
                data = data.encode('utf-8')
            data = etree.fromstring(data)
        return data

    monkeypatch.setattr(
        owslib.feature.common.WFSCapabilitiesReader, 'read', read)


@pytest.fixture
def mp_wfs_200_nometadata(monkeypatch):
    """Monkeypatch the call to the remote GetCapabilities request of WFS
    version 2.0.0, not containing MetadataURLs.

    Parameters
    ----------
    monkeypatch : pytest.fixture
        PyTest monkeypatch fixture.

    """
    def read(*args, **kwargs):
        with open('tests/resources/wfs_dov_getcapabilities_200_nometadata.xml',
                  'r') as f:
            data = f.read()
            if type(data) is not bytes:
                data = data.encode('utf-8')
            data = etree.fromstring(data)
        return data

    monkeypatch.setattr(
        owslib.feature.common.WFSCapabilitiesReader, 'read', read)


@pytest.fixture
def mp_wms_111_nometadata(monkeypatch):
    """Monkeypatch the call to the remote GetCapabilities request of WMS
    version 1.1.1, not containing MetadataURLs.

    Parameters
    ----------
    monkeypatch : pytest.fixture
        PyTest monkeypatch fixture.

    """
    def read(*args, **kwargs):
        with open('tests/resources/wms_dov_getcapabilities_111_nometadata.xml',
                  'r') as f:
            data = f.read()
            if type(data) is not bytes:
                data = data.encode('utf-8')
            data = etree.fromstring(data)
        return data

    monkeypatch.setattr(
        owslib.map.common.WMSCapabilitiesReader, 'read', read)


@pytest.fixture
def mp_wms_130(monkeypatch):
    """Monkeypatch the call to the remote GetCapabilities request of WMS
    version 1.3.0.

    Parameters
    ----------
    monkeypatch : pytest.fixture
        PyTest monkeypatch fixture.

    """
    def read(*args, **kwargs):
        with open('tests/resources/wms_dov_getcapabilities_130.xml', 'r') as f:
            data = f.read()
            if type(data) is not bytes:
                data = data.encode('utf-8')
            data = etree.fromstring(data)
        return data

    monkeypatch.setattr(
        owslib.map.common.WMSCapabilitiesReader, 'read', read)


@pytest.fixture
def mp_wms_130_nometadata(monkeypatch):
    """Monkeypatch the call to the remote GetCapabilities request of WMS
    version 1.3.0, not containing MetadataURLs.

    Parameters
    ----------
    monkeypatch : pytest.fixture
        PyTest monkeypatch fixture.

    """
    def read(*args, **kwargs):
        with open('tests/resources/wms_dov_getcapabilities_130_nometadata'
                  '.xml', 'r') as f:
            data = f.read()
            if type(data) is not bytes:
                data = data.encode('utf-8')
            data = etree.fromstring(data)
        return data

    monkeypatch.setattr(
        owslib.map.common.WMSCapabilitiesReader, 'read', read)


@pytest.fixture
def mp_remote_md(monkeypatch):
    def openURL(*args, **kwargs):
        with open('tests/resources/csw_dov_getrecordbyid.xml', 'r') as f:
            data = f.read()
            if type(data) is not bytes:
                data = data.encode('utf-8')
            data = etree.fromstring(data)
        return data

    monkeypatch.setattr(owslib.util, 'openURL', openURL)


class TestOffline(object):
    def test_wfs_100_noremotemd_parse_all(self, mp_wfs_100_nometadata):
        """Test the remote metadata parsing for WFS 1.0.0.

        Tests parsing the remote metadata for all layers.

        Test whether the method is available and returns no remote metadata
        if no MetadataURLs are available in the GetCapabilities.

        Parameters
        ----------
        mp_wfs_100_nometadata : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.

        """
        wfs = WebFeatureService(url='http://localhost/not_applicable',
                                version='1.0.0',
                                parse_remote_metadata=True)
        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    def test_wfs_100_noremotemd_parse_single(self, mp_wfs_100_nometadata):
        """Test the remote metadata parsing for WFS 1.0.0.

        Tests parsing the remote metadata for a single layer.

        Test whether the method is available and returns no remote metadata
        if no MetadataURLs are available in the GetCapabilities.

        Parameters
        ----------
        mp_wfs_100_nometadata : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.

        """
        wfs = WebFeatureService(url='http://localhost/not_applicable',
                                version='1.0.0',
                                parse_remote_metadata=False)
        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']
        layer.parse_remote_metadata()

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    def test_wfs_100_noremotemd_parse_none(self, mp_wfs_100_nometadata):
        """Test the remote metadata parsing for WFS 1.0.0.

        Tests the case when no remote metadata is parsed.

        Test whether no remote metadata is returned.

        Parameters
        ----------
        mp_wfs_100_nometadata : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.

        """
        wfs = WebFeatureService(url='http://localhost/not_applicable',
                                version='1.0.0',
                                parse_remote_metadata=False)
        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    def test_wfs_110_noremotemd_parse_all(self, mp_wfs_110_nometadata):
        """Test the remote metadata parsing for WFS 1.1.0.

        Tests parsing the remote metadata for all layers.

        Test whether the method is available and returns no remote metadata
        if no MetadataURLs are available in the GetCapabilities.

        Parameters
        ----------
        mp_wfs_110_nometadata : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.

        """
        wfs = WebFeatureService(url='http://localhost/not_applicable',
                                version='1.1.0',
                                parse_remote_metadata=True)
        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    def test_wfs_110_noremotemd_parse_single(self, mp_wfs_110_nometadata):
        """Test the remote metadata parsing for WFS 1.1.0.

        Tests parsing the remote metadata for a single layer.

        Test whether the method is available and returns no remote metadata
        if no MetadataURLs are available in the GetCapabilities.

        Parameters
        ----------
        mp_wfs_110_nometadata : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.

        """
        wfs = WebFeatureService(url='http://localhost/not_applicable',
                                version='1.1.0',
                                parse_remote_metadata=False)
        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']
        layer.parse_remote_metadata()

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    def test_wfs_110_noremotemd_parse_none(self, mp_wfs_110_nometadata):
        """Test the remote metadata parsing for WFS 1.1.0.

        Tests the case when no remote metadata is parsed.

        Test whether no remote metadata is returned.

        Parameters
        ----------
        mp_wfs_110_nometadata : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.

        """
        wfs = WebFeatureService(url='http://localhost/not_applicable',
                                version='1.1.0',
                                parse_remote_metadata=False)
        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    def test_wfs_110_remotemd_parse_all(self, mp_wfs_110, mp_remote_md):
        """Test the remote metadata parsing for WFS 1.1.0.

        Tests parsing the remote metadata for all layers.

        Test whether the method is available and returns remote metadata
        if MetadataURLs are available in the GetCapabilities.

        Parameters
        ----------
        mp_wfs_110 : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.
        mp_remote_md : pytest.fixture
            Monkeypatch the call to the remote metadata.

        """
        wfs = WebFeatureService(url='http://localhost/not_applicable',
                                version='1.1.0',
                                parse_remote_metadata=True)
        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 1

        for m in mdrecords:
            assert type(m) is owslib.iso.MD_Metadata

    def test_wfs_110_remotemd_parse_single(self, mp_wfs_110, mp_remote_md):
        """Test the remote metadata parsing for WFS 1.1.0.

        Tests parsing the remote metadata for a single layer.

        Test whether the method is available and returns remote metadata
        if MetadataURLs are available in the GetCapabilities.

        Parameters
        ----------
        mp_wfs_110 : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.
        mp_remote_md : pytest.fixture
            Monkeypatch the call to the remote metadata.

        """
        wfs = WebFeatureService(url='http://localhost/not_applicable',
                                version='1.1.0',
                                parse_remote_metadata=False)
        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']
        layer.parse_remote_metadata()

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 1

        for m in mdrecords:
            assert type(m) is owslib.iso.MD_Metadata

    def test_wfs_110_remotemd_parse_none(self, mp_wfs_110):
        """Test the remote metadata parsing for WFS 1.1.0.

        Tests the case when no remote metadata is parsed.

        Test whether no remote metadata is returned.

        Parameters
        ----------
        mp_wfs_110 : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.

        """
        wfs = WebFeatureService(url='http://localhost/not_applicable',
                                version='1.1.0',
                                parse_remote_metadata=False)
        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    def test_wfs_200_noremotemd_parse_all(self, mp_wfs_200_nometadata):
        """Test the remote metadata parsing for WFS 2.0.0.

        Tests parsing the remote metadata for all layers.

        Test whether the method is available and returns no remote metadata
        if no MetadataURLs are available in the GetCapabilities.

        Parameters
        ----------
        mp_wfs_200_nometadata : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.

        """
        wfs = WebFeatureService(url='http://localhost/not_applicable',
                                version='2.0.0',
                                parse_remote_metadata=True)
        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    def test_wfs_200_noremotemd_parse_single(self, mp_wfs_200_nometadata):
        """Test the remote metadata parsing for WFS 2.0.0.

        Tests parsing the remote metadata for a single layer.

        Test whether the method is available and returns no remote metadata
        if no MetadataURLs are available in the GetCapabilities.

        Parameters
        ----------
        mp_wfs_200_nometadata : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.

        """
        wfs = WebFeatureService(url='http://localhost/not_applicable',
                                version='2.0.0',
                                parse_remote_metadata=False)
        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']
        layer.parse_remote_metadata()

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    def test_wfs_200_noremotemd_parse_none(self, mp_wfs_200_nometadata):
        """Test the remote metadata parsing for WFS 2.0.0.

        Tests the case when no remote metadata is parsed.

        Test whether no remote metadata is returned.

        Parameters
        ----------
        mp_wfs_200_nometadata : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.

        """
        wfs = WebFeatureService(url='http://localhost/not_applicable',
                                version='2.0.0',
                                parse_remote_metadata=False)
        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    def test_wfs_200_remotemd_parse_all(self, mp_wfs_200, mp_remote_md):
        """Test the remote metadata parsing for WFS 2.0.0.

        Tests parsing the remote metadata for all layers.

        Test whether the method is available and returns remote metadata
        if MetadataURLs are available in the GetCapabilities.

        Parameters
        ----------
        mp_wfs_200 : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.
        mp_remote_md : pytest.fixture
            Monkeypatch the call to the remote metadata.

        """
        wfs = WebFeatureService(url='http://localhost/not_applicable',
                                version='2.0.0',
                                parse_remote_metadata=True)
        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 1

        for m in mdrecords:
            assert type(m) is owslib.iso.MD_Metadata

    def test_wfs_200_remotemd_parse_single(self, mp_wfs_200, mp_remote_md):
        """Test the remote metadata parsing for WFS 2.0.0.

        Tests parsing the remote metadata for a single layer.

        Test whether the method is available and returns remote metadata
        if MetadataURLs are available in the GetCapabilities.

        Parameters
        ----------
        mp_wfs_200 : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.
        mp_remote_md : pytest.fixture
            Monkeypatch the call to the remote metadata.

        """
        wfs = WebFeatureService(url='http://localhost/not_applicable',
                                version='2.0.0',
                                parse_remote_metadata=False)
        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']
        layer.parse_remote_metadata()

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 1

        for m in mdrecords:
            assert type(m) is owslib.iso.MD_Metadata

    def test_wfs_200_remotemd_parse_none(self, mp_wfs_200):
        """Test the remote metadata parsing for WFS 2.0.0.

        Tests the case when no remote metadata is parsed.

        Test whether no remote metadata is returned.

        Parameters
        ----------
        mp_wfs_200 : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.

        """
        wfs = WebFeatureService(url='http://localhost/not_applicable',
                                version='2.0.0',
                                parse_remote_metadata=False)
        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    def test_wms_111_noremotemd_parse_all(self, mp_wms_111_nometadata):
        """Test the remote metadata parsing for WMS 1.1.1.

        Tests parsing the remote metadata for all layers.

        Test whether the method is available and returns no remote metadata
        if no MetadataURLs are available in the GetCapabilities.

        Parameters
        ----------
        mp_wms_111_nometadata : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.

        """
        wms = WebMapService(url='http://localhost/not_applicable',
                            version='1.1.1',
                            parse_remote_metadata=True)
        assert 'meetnetten' in wms.contents
        layer = wms.contents['meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    def test_wms_111_noremotemd_parse_single(self, mp_wms_111_nometadata):
        """Test the remote metadata parsing for WMS 1.1.1.

        Tests parsing the remote metadata for a single layer.

        Test whether the method is available and returns no remote metadata
        if no MetadataURLs are available in the GetCapabilities.

        Parameters
        ----------
        mp_wms_111_nometadata : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.

        """
        wms = WebMapService(url='http://localhost/not_applicable',
                            version='1.1.1',
                            parse_remote_metadata=False)
        assert 'meetnetten' in wms.contents
        layer = wms.contents['meetnetten']
        layer.parse_remote_metadata()

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    def test_wms_111_noremotemd_parse_none(self, mp_wms_111_nometadata):
        """Test the remote metadata parsing for WMS 1.1.1.

        Tests the case when no remote metadata is parsed.

        Test whether no remote metadata is returned.

        Parameters
        ----------
        mp_wms_111_nometadata : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.

        """
        wms = WebMapService(url='http://localhost/not_applicable',
                            version='1.1.1',
                            parse_remote_metadata=False)
        assert 'meetnetten' in wms.contents
        layer = wms.contents['meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    def test_wms_130_remotemd_parse_all(self, mp_wms_130):
        """Test the remote metadata parsing for WMS 1.3.0.

        Tests parsing the remote metadata for all layers.

        Test whether the method is available and returns remote metadata
        if MetadataURLs are available in the GetCapabilities.

        Parameters
        ----------
        mp_wms_130 : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.

        """
        wms = WebMapService(url='http://localhost/not_applicable',
                            version='1.3.0',
                            parse_remote_metadata=True)
        assert 'meetnetten' in wms.contents
        layer = wms.contents['meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 1

        for m in mdrecords:
            assert type(m) is owslib.iso.MD_Metadata

    def test_wms_130_remotemd_parse_single(self, mp_wms_130):
        """Test the remote metadata parsing for WMS 1.3.0.

        Tests parsing the remote metadata for a single layer.

        Test whether the method is available and returns remote metadata
        if MetadataURLs are available in the GetCapabilities.

        Parameters
        ----------
        mp_wms_130 : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.

        """
        wms = WebMapService(url='http://localhost/not_applicable',
                            version='1.3.0',
                            parse_remote_metadata=False)
        assert 'meetnetten' in wms.contents
        layer = wms.contents['meetnetten']
        layer.parse_remote_metadata()

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 1

        for m in mdrecords:
            assert type(m) is owslib.iso.MD_Metadata

    def test_wms_130_remotemd_parse_none(self, mp_wms_130):
        """Test the remote metadata parsing for WMS 1.3.0.

        Tests the case when no remote metadata is parsed.

        Test whether no remote metadata is returned.

        Parameters
        ----------
        mp_wms_130 : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.

        """
        wms = WebMapService(url='http://localhost/not_applicable',
                            version='1.3.0',
                            parse_remote_metadata=False)
        assert 'meetnetten' in wms.contents
        layer = wms.contents['meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    def test_wms_130_noremotemd_parse_all(self, mp_wms_130_nometadata):
        """Test the remote metadata parsing for WMS 1.3.0.

        Tests parsing the remote metadata for all layers.

        Test whether the method is available and returns no remote metadata
        if no MetadataURLs are available in the GetCapabilities.

        Parameters
        ----------
        mp_wms_130_nometadata : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.

        """
        wms = WebMapService(url='http://localhost/not_applicable',
                            version='1.3.0',
                            parse_remote_metadata=True)
        assert 'meetnetten' in wms.contents
        layer = wms.contents['meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    def test_wms_130_noremotemd_parse_single(self, mp_wms_130_nometadata):
        """Test the remote metadata parsing for WMS 1.3.0.

        Tests parsing the remote metadata for a single layer.

        Test whether the method is available and returns no remote metadata
        if no MetadataURLs are available in the GetCapabilities.

        Parameters
        ----------
        mp_wms_130_nometadata : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.

        """
        wms = WebMapService(url='http://localhost/not_applicable',
                            version='1.3.0',
                            parse_remote_metadata=False)
        assert 'meetnetten' in wms.contents
        layer = wms.contents['meetnetten']
        layer.parse_remote_metadata()

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    def test_wms_130_noremotemd_parse_none(self, mp_wms_130_nometadata):
        """Test the remote metadata parsing for WMS 1.3.0.

        Tests the case when no remote metadata is parsed.

        Test whether no remote metadata is returned.

        Parameters
        ----------
        mp_wms_130_nometadata : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.

        """
        wms = WebMapService(url='http://localhost/not_applicable',
                            version='1.3.0',
                            parse_remote_metadata=False)
        assert 'meetnetten' in wms.contents
        layer = wms.contents['meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0


class TestOnline(object):
    @pytest.mark.online
    @pytest.mark.skipif(not service_ok(WFS_SERVICE_URL),
                        reason="WFS service is unreachable")
    @pytest.mark.parametrize("wfs_version", ["1.1.0", "2.0.0"])
    def test_wfs_remotemd_parse_single(self, wfs_version):
        """Test the remote metadata parsing for WFS.

        Tests parsing the remote metadata for a single layer.

        Test whether the method is available and returns remote metadata.

        """
        wfs = WebFeatureService(url=WFS_SERVICE_URL,
                                version=wfs_version,
                                parse_remote_metadata=False)

        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']
        layer.parse_remote_metadata()

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) > 0

        for m in mdrecords:
            assert type(m) is owslib.iso.MD_Metadata

    @pytest.mark.online
    @pytest.mark.skipif(not service_ok(WFS_SERVICE_URL),
                        reason="WFS service is unreachable")
    @pytest.mark.parametrize("wfs_version", ["1.1.0", "2.0.0"])
    def test_wfs_remotemd_parse_all(self, wfs_version):
        """Test the remote metadata parsing for WFS.

        Tests parsing the remote metadata for all layers.

        Test whether the method is available and returns remote metadata.

        """
        wfs = WebFeatureService(url=WFS_SERVICE_URL,
                                version=wfs_version,
                                parse_remote_metadata=True)

        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) > 0

        for m in mdrecords:
            assert type(m) is owslib.iso.MD_Metadata

    @pytest.mark.online
    @pytest.mark.skipif(not service_ok(WFS_SERVICE_URL),
                        reason="WFS service is unreachable")
    @pytest.mark.parametrize("wfs_version", ["1.1.0", "2.0.0"])
    def test_wfs_remotemd_parse_none(self, wfs_version):
        """Test the remote metadata parsing for WFS.

        Tests the case when no remote metadata is parsed.

        Test whether no remote metadata is returned.

        """
        wfs = WebFeatureService(url=WFS_SERVICE_URL,
                                version=wfs_version,
                                parse_remote_metadata=False)

        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    @pytest.mark.online
    @pytest.mark.skipif(not service_ok(WFS_SERVICE_URL),
                        reason="WFS service is unreachable")
    @pytest.mark.parametrize("wfs_version", ["1.0.0"])
    def test_wfs_noremotemd_parse_single(self, wfs_version):
        """Test the remote metadata parsing for WFS.

        Tests parsing the remote metadata for a single layer.

        Test whether the method is available and returns no remote metadata
        if no MetadataURLs are available in the GetCapabilities.

        """
        wfs = WebFeatureService(url=WFS_SERVICE_URL,
                                version=wfs_version,
                                parse_remote_metadata=False)

        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']
        layer.parse_remote_metadata()

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    @pytest.mark.online
    @pytest.mark.skipif(not service_ok(WFS_SERVICE_URL),
                        reason="WFS service is unreachable")
    @pytest.mark.parametrize("wfs_version", ["1.0.0"])
    def test_wfs_noremotemd_parse_all(self, wfs_version):
        """Test the remote metadata parsing for WFS.

        Tests parsing the remote metadata for all layers.

        Test whether the method is available and returns no remote
        metadata if no MetadataURLs are available in the GetCapabilities.

        """
        wfs = WebFeatureService(url=WFS_SERVICE_URL,
                                version=wfs_version,
                                parse_remote_metadata=True)

        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    @pytest.mark.online
    @pytest.mark.skipif(not service_ok(WFS_SERVICE_URL),
                        reason="WFS service is unreachable")
    @pytest.mark.parametrize("wfs_version", ["1.0.0"])
    def test_wfs_noremotemd_parse_none(self, wfs_version):
        """Test the remote metadata parsing for WFS.

        Tests the case when no remote metadata is parsed.

        Test whether no remote metadata is returned.

        """
        wfs = WebFeatureService(url=WFS_SERVICE_URL,
                                version=wfs_version,
                                parse_remote_metadata=False)

        assert 'gw_meetnetten:meetnetten' in wfs.contents
        layer = wfs.contents['gw_meetnetten:meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    @pytest.mark.online
    @pytest.mark.skipif(not service_ok(WMS_SERVICE_URL),
                        reason="WMS service is unreachable")
    @pytest.mark.parametrize("wms_version", ["1.3.0"])
    def test_wms_remotemd_parse_single(self, wms_version):
        """Test the remote metadata parsing for WMS.

        Tests parsing the remote metadata for a single layer.

        Test whether the method is available and returns remote metadata.

        """
        wms = WebMapService(url=WMS_SERVICE_URL,
                            version=wms_version,
                            parse_remote_metadata=False)

        assert 'meetnetten' in wms.contents
        layer = wms.contents['meetnetten']
        layer.parse_remote_metadata()

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) > 0

        for m in mdrecords:
            assert type(m) is owslib.iso.MD_Metadata

    @pytest.mark.online
    @pytest.mark.skipif(not service_ok(WMS_SERVICE_URL),
                        reason="WMS service is unreachable")
    @pytest.mark.parametrize("wms_version", ["1.3.0"])
    def test_wms_remotemd_parse_all(self, wms_version):
        """Test the remote metadata parsing for WMS.

        Tests parsing the remote metadata for all layers.

        Test whether the method is available and returns remote metadata.

        """
        wms = WebMapService(url=WMS_SERVICE_URL,
                            version=wms_version,
                            parse_remote_metadata=True)

        assert 'meetnetten' in wms.contents
        layer = wms.contents['meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) > 0

        for m in mdrecords:
            assert type(m) is owslib.iso.MD_Metadata

    @pytest.mark.online
    @pytest.mark.skipif(not service_ok(WMS_SERVICE_URL),
                        reason="WMS service is unreachable")
    @pytest.mark.parametrize("wms_version", ["1.3.0"])
    def test_wms_remotemd_parse_none(self, wms_version):
        """Test the remote metadata parsing for WMS.

        Tests the case when no remote metadata is parsed.

        Test whether no remote metadata is returned.

        """
        wms = WebMapService(url=WMS_SERVICE_URL,
                            version=wms_version,
                            parse_remote_metadata=False)

        assert 'meetnetten' in wms.contents
        layer = wms.contents['meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    @pytest.mark.online
    @pytest.mark.skipif(not service_ok(WMS_SERVICE_URL),
                        reason="WMS service is unreachable")
    @pytest.mark.parametrize("wms_version", ["1.1.1"])
    def test_wms_noremotemd_parse_single(self, wms_version):
        """Test the remote metadata parsing for WMS.

         Tests parsing the remote metadata for a single layer.

         Test whether the method is available and returns no remote metadata
         if no MetadataURLs are available in the GetCapabilities.

         """
        wms = WebMapService(url=WMS_SERVICE_URL,
                            version=wms_version,
                            parse_remote_metadata=False)

        assert 'meetnetten' in wms.contents
        layer = wms.contents['meetnetten']
        layer.parse_remote_metadata()

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    @pytest.mark.online
    @pytest.mark.skipif(not service_ok(WMS_SERVICE_URL),
                        reason="WMS service is unreachable")
    @pytest.mark.parametrize("wms_version", ["1.1.1"])
    def test_wms_noremotemd_parse_all(self, wms_version):
        """Test the remote metadata parsing for WMS.

        Tests parsing the remote metadata for all layers.

        Test whether the method is available and returns no remote
        metadata if no MetadataURLs are available in the GetCapabilities.

        """
        wms = WebMapService(url=WMS_SERVICE_URL,
                            version=wms_version,
                            parse_remote_metadata=True)

        assert 'meetnetten' in wms.contents
        layer = wms.contents['meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0

    @pytest.mark.online
    @pytest.mark.skipif(not service_ok(WMS_SERVICE_URL),
                        reason="WMS service is unreachable")
    @pytest.mark.parametrize("wms_version", ["1.1.1"])
    def test_wms_noremotemd_parse_none(self, wms_version):
        """Test the remote metadata parsing for WMS.

        Tests the case when no remote metadata is parsed.

        Test whether no remote metadata is returned.

        """
        wms = WebMapService(url=WMS_SERVICE_URL,
                            version=wms_version,
                            parse_remote_metadata=False)

        assert 'meetnetten' in wms.contents
        layer = wms.contents['meetnetten']

        mdrecords = layer.get_metadata()
        assert type(mdrecords) is list
        assert len(mdrecords) == 0
