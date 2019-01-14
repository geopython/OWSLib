from owslib.namespaces import Namespaces

from owslib.ows import BoundingBox, DEFAULT_OWS_NAMESPACE
from owslib import crs
from owslib.etree import etree

DEFAULT_WPS_NAMESPACE = Namespaces().get_namespace('wps')


def test_ows_bbox():
    bbox_elem = etree.fromstring("""
    <ows:BoundingBox xmlns:ows="{}" crs="EPSG:4326" dimensions="2">
        <ows:LowerCorner>0.0 -90.0</ows:LowerCorner>
        <ows:UpperCorner>180.0 90.0</ows:UpperCorner>
    </ows:BoundingBox>""".format(DEFAULT_OWS_NAMESPACE))
    bbox = BoundingBox(bbox_elem)
    assert bbox.crs == crs.Crs('EPSG:4326')
    assert bbox.crs.axisorder == 'yx'
    assert bbox.dimensions == 2
    assert bbox.minx == '-90.0'
    assert bbox.miny == '0.0'
    assert bbox.maxx == '90.0'
    assert bbox.maxy == '180.0'


def test_ows_bbox_with_namespaces():
    """ XML bounding box description as received from a wps request """
    
    bbox_elem = etree.fromstring("""
    <wps:BoundingBoxData xmlns:wps="{}" xmlns:ows="{}" ows:crs="EPSG:4326" ows:dimensions="2">
        <ows:LowerCorner>0.0 -90.0</ows:LowerCorner>
        <ows:UpperCorner>180.0 90.0</ows:UpperCorner>
    </wps:BoundingBoxData>""".format(DEFAULT_WPS_NAMESPACE, DEFAULT_OWS_NAMESPACE))
    bbox = BoundingBox(bbox_elem)
    assert bbox.crs == crs.Crs('EPSG:4326')
    assert bbox.crs.axisorder == 'yx'
    assert bbox.dimensions == 2
    assert bbox.minx == '-90.0'
    assert bbox.miny == '0.0'
    assert bbox.maxx == '90.0'
    assert bbox.maxy == '180.0'
