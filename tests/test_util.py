# -*- coding: UTF-8 -*-
import pytest

import codecs
from owslib.util import clean_ows_url, build_get_url, strip_bom, encode_string


def test_encode_string():
    assert encode_string('hello') == 'hello'
    assert encode_string('Particulate Matter < 10 µm') == 'Particulate Matter < 10 µm'
    assert encode_string(u'Particulate Matter < 10 µm') == 'Particulate Matter < 10 µm'


def test_strip_bom():
    assert strip_bom('<city>Hamburg</city>') == '<city>Hamburg</city>'
    assert strip_bom(codecs.BOM_UTF8 + '<city>Dublin</city>'.encode('utf-8')) == \
        '<city>Dublin</city>'.encode('utf-8')
    assert strip_bom(codecs.BOM_UTF16 + '<city>Vancover</city>'.encode('utf-16')) == \
        '<city>Vancover</city>'.encode('utf-16')


def test_clean_ows_url():
    assert clean_ows_url('http//example.org/wms') == 'http//example.org/wms'
    assert clean_ows_url('http//example.org/wms?service=WMS') == 'http//example.org/wms'
    assert clean_ows_url('http//example.org/wms?SERVICE=WMS') == 'http//example.org/wms'
    assert clean_ows_url('http//example.org/wms?SeRvIcE=WMS') == 'http//example.org/wms'
    assert clean_ows_url('http//example.org/wms?SeRvIcE=WMS&version=1.3.0&request=GetCapabilities') == 'http//example.org/wms'  # noqa
    assert clean_ows_url('http//example.org/wms?foo=bar&SeRvIcE=WMS&version=1.3.0&request=GetCapabilities') == 'http//example.org/wms?foo=bar'  # noqa


@pytest.mark.skip(reason="fails on python 3.4")
def test_util_py34():
    assert clean_ows_url('http://example.org/wms?map=/path/to/foo.map&SERVICE=WMS&version=1.3.0&request=GetCapabilities') == 'http://example.org/wms?map=%2Fpath%2Fto%2Ffoo.map'  # noqa
    assert clean_ows_url('http://example.org/wms?map=/path/to/foo.map&foo=bar&&SERVICE=WMS&version=1.3.0&request=GetCapabilities') == 'http://example.org/wms?map=%2Fpath%2Fto%2Ffoo.map&foo=bar'  # noqa


def test_build_get_url():
    assert build_get_url("http://example.org/wps", {'service': 'WPS'}) == 'http://example.org/wps?service=WPS'
    assert build_get_url("http://example.org/wms", {'SERVICE': 'wms'}) == 'http://example.org/wms?SERVICE=wms'
    assert build_get_url("http://example.org/wps?service=WPS", {'request': 'GetCapabilities'}) == \
        'http://example.org/wps?service=WPS&request=GetCapabilities'
    assert build_get_url("http://example.org/wps?service=WPS", {'request': 'GetCapabilities'}) == \
        'http://example.org/wps?service=WPS&request=GetCapabilities'
    # Can not overwrite parameter
    assert build_get_url("http://example.org/ows?SERVICE=WPS", {'SERVICE': 'WMS'}) == \
        'http://example.org/ows?SERVICE=WPS'
    # Parameter is case-senstive
    assert build_get_url("http://example.org/ows?SERVICE=WPS", {'service': 'WMS'}) == \
        'http://example.org/ows?SERVICE=WPS&service=WMS'


def test_build_get_url_overwrite():
    # Use overwrite flag
    assert build_get_url("http://example.org/ows?SERVICE=WPS", {'SERVICE': 'WMS'}, overwrite=True) == \
        'http://example.org/ows?SERVICE=WMS'
