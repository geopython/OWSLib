# flake8: noqa: W503

import re
from pathlib import Path
import pytest
from pytest_httpserver import HTTPServer

from owslib.csw import CatalogueServiceWeb
from owslib.fes import PropertyIsEqualTo

MOCK_SERVER_PORT = 59950
MOCK_SERVICE_URL = f"http://localhost:{MOCK_SERVER_PORT}/csw"


@pytest.fixture
def records():
    """Mock a GetRecords response from INSPIRE Geoportal

    Source: https://inspire-geoportal.ec.europa.eu/srv/eng/csw
    """
    inspire_sample = str(
        Path(__file__).parent.parent
        / "tests"
        / "resources"
        / "inspire-getrecords-response.xml"
    )

    with open(inspire_sample, "r", encoding="utf-8") as f:
        xml_str = f.read()
        return xml_str


@pytest.mark.online
def test_language(records):
    """Test records"""

    with HTTPServer(port=MOCK_SERVER_PORT) as httpserver:
        httpserver.expect_request(re.compile("^/csw")).respond_with_data(records)
        csw = CatalogueServiceWeb(url=MOCK_SERVICE_URL, skip_caps=True)
        cq = PropertyIsEqualTo(
            "th_httpinspireeceuropaeutheme-theme.link",
            "http://inspire.ec.europa.eu/theme/ac",
        )
        csw.getrecords2(
            constraints=[cq],
            outputschema="http://www.isotc211.org/2005/gmd",
            maxrecords=2,
            startposition=83,
            esn="full",
        )

    assert len(csw.records) == 2
    rec1 = csw.records.get("8dad9c98-0512-4845-a2bf-3ace1c93df6f")
    assert rec1.languagecode == "eng"
    assert rec1.charset == "utf8"

    rec2 = csw.records.get("eeae2de7-0a09-4b69-b7a0-0b6b20903fd5")
    assert rec2.languagecode == "ger"
    assert rec2.charset is None
