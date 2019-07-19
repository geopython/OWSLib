# -*- coding: UTF-8 -*-
import codecs
from owslib.util import clean_ows_url, build_get_url, strip_bom


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
    assert clean_ows_url('http://example.org/wms?map=/path/to/foo.map&SERVICE=WMS&version=1.3.0&request=GetCapabilities') == 'http://example.org/wms?map=%2Fpath%2Fto%2Ffoo.map'  # noqa
    clean_url = clean_ows_url('http://example.org/wms?map=/path/to/foo.map&foo=bar&&SERVICE=WMS&version=1.3.0&request=GetCapabilities')  # noqa
    assert 'http://example.org/wms?' in clean_url
    assert 'map=%2Fpath%2Fto%2Ffoo.map' in clean_url
    assert 'foo=bar' in clean_url


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
