import pytest
from owslib.wfs import WebFeatureService
from owslib import fes2
from owslib.gml import Point
from owslib.namespaces import Namespaces
from owslib import util
import json

n = Namespaces()
FES_NAMESPACE = n.get_namespace("fes")
GML32_NAMESPACE = n.get_namespace("gml32")


SERVICE_URL = "http://soggy.zoology.ubc.ca:8080/geoserver/wfs"


def test_raw_filter():
    """Just inspect the filter object (not embedded in a getfeature request)."""
    point = Point(id="qc", srsName="http://www.opengis.net/gml/srs/epsg.xml#4326", pos=[-71, 46])
    f = fes2.Filter(
        fes2.And([fes2.Intersects(propertyname="the_geom", geometry=point),
                  fes2.PropertyIsLike("name", "value")]
                 )
    )

    xml = f.toXML()

    # Fairly basic test
    xml.find(util.nspath("Filter", FES_NAMESPACE))
    xml.find(util.nspath("And", FES_NAMESPACE))
    xml.find(util.nspath("Intersects", FES_NAMESPACE))
    xml.find(util.nspath("Point", GML32_NAMESPACE))

@pytest.mark.xfail
@pytest.mark.online
def test_filter():
    """A request without filtering will yield 600 entries. With filtering we expect only one.

    Note that this type of topological filtering only works (so far) with WFS 2.0.0 and POST requests.
    """
    wfs = WebFeatureService(SERVICE_URL, version="2.0.0")
    layer = "psf:level4"
    point = Point(id="random", srsName="http://www.opengis.net/gml/srs/epsg.xml#4326", pos=[-129.8, 55.44])
    f = fes2.Filter(fes2.Contains(propertyname="geom", geometry=point))
    r = wfs.getfeature(layer, outputFormat="application/json", method="POST", filter=f.toXML())
    assert json.load(r)["totalFeatures"] == 1
