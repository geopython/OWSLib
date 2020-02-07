from owslib.wps import WebProcessingService
import owslib.wps
from owslib.etree import etree


def test_wps_getcapabilities_language(monkeypatch):

    def mock_open_url(*args, **kwargs):
        assert 'language=fr-CA' in args[1]

        class FakeResponse:
            def read(self):
                return b'<xml></xml>'

        return FakeResponse()

    monkeypatch.setattr(owslib.wps, "openURL", mock_open_url)
    WebProcessingService('http://www.example.com', language='fr-CA')


def test_wps_getcapabilities_parse_languages():
    xml = """
    <wps:Languages xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows">
        <wps:Default>
            <ows:Language>en-US</ows:Language>
        </wps:Default>
        <wps:Supported>
            <ows:Language>en-US</ows:Language>
            <ows:Language>fr-CA</ows:Language>
        </wps:Supported>
    </wps:Languages>
    """
    element = etree.fromstring(xml)
    languages = owslib.wps.Languages(element)
    assert languages.default == 'en-US'
    assert languages.supported == ['en-US', 'fr-CA']
