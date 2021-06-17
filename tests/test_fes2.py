from owslib import fes2
from owslib.gml import Point
from owslib.etree import etree


def test_filter():
    point = Point(id="qc", srsName="http://www.opengis.net/gml/srs/epsg.xml#4326", pos=[-71, 46])
    f = fes2.Filter(
        fes2.And([fes2.Intersects(propertyname="the_geom", geometry=point),
                  fes2.PropertyIsLike("name", "value")]
                 )
    )

    xml = f.toXML()
    assert etree.tostring(xml) ==  b'<fes:Filter ' \
                                b'xmlns:fes="http://www.opengis.net/fes/2.0"><fes:And><fes:Intersects><fes:ValueReference>the_geom</fes:ValueReference><gml32:Point xmlns:gml32="http://www.opengis.net/gml/3.2" gml32:id="qc" gml32:srsName="http://www.opengis.net/gml/srs/epsg.xml#4326"><gml32:pos>-71 46</gml32:pos></gml32:Point></fes:Intersects><fes:PropertyIsLike wildCard="%" singleChar="_" escapeChar="\\"><fes:ValueReference>name</fes:ValueReference><fes:Literal>value</fes:Literal></fes:PropertyIsLike></fes:And></fes:Filter>'
