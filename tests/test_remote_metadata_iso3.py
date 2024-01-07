import pytest

import owslib
import owslib.util
from owslib.etree import etree
from owslib.wfs import WebFeatureService
from owslib.wms import WebMapService


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
def mp_md3(monkeypatch):
    """ Patch in ISO 19115 Part 3 XML
    """
    def openURL(*args, **kwargs):
        data = open('tests/resources/iso3_examples/auscope-3d-model.xml', 'rb')
        return data

    monkeypatch.setattr(owslib.util, "openURL", openURL)

class TestOffline(object):

    def test_wfs_110_remotemd3_parse_all(self, mp_md3, mp_wfs_110):
        """Test the remote metadata parsing for WFS 1.1.0.

        Tests parsing the remote metadata for all layers.

        Test whether the method is available and returns remote metadata
        if MetadataURLs are available in the GetCapabilities.

        Parameters
        ----------
        mp_wfs_110 : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.
        mp_md3 : pytest.fixture
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
            assert type(m) is owslib.iso_3.MD_Metadata