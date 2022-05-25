from unittest import mock
from tests.utils import service_ok

import pytest

from owslib.csw import CatalogueServiceWeb


def test_csw_sends_headers():
    """
    Test that if headers are provided in the CSW class they are sent
    when performing HTTP requests (in this case for GetCapabilities)
    """

    with mock.patch('owslib.util.requests.request', side_effect=RuntimeError) as mock_request:
        try:
            CatalogueServiceWeb(
                'http://example.com/csw',
                version='2.0.2',
                headers={'User-agent': 'my-app/1.0'}
            )
        except RuntimeError:
            assert mock_request.called
            assert mock_request.call_args[1]['headers'] == {'User-agent': 'my-app/1.0'}

    with mock.patch('owslib.util.requests.request', side_effect=RuntimeError) as mock_request:
        try:
            CatalogueServiceWeb(
                'http://example.com/csw',
                version='3.0.0',
                headers={'User-agent': 'my-app/1.0'}
            )
        except RuntimeError:
            assert mock_request.called
            assert mock_request.call_args[1]['headers'] == {'Accept': 'application/xml', 'User-agent': 'my-app/1.0'}
