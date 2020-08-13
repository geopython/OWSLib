from owslib.feature import postrequest
from owslib.etree import etree
from owslib.namespaces import Namespaces
from owslib import util

n = Namespaces()
FES_NAMESPACE = n.get_namespace("fes")
GML_NAMESPACE = n.get_namespace("gml")
GML32_NAMESPACE = n.get_namespace("gml32")
OGC_NAMESPACE = n.get_namespace("ogc")
WFS_NAMESPACE = n.get_namespace("wfs")
WFS20_NAMESPACE = n.get_namespace("wfs20")

xml_filter_1_1_0 = """<?xml version="1.0" ?>
    <wfs:GetFeature service="WFS" version="1.1.0"
        xmlns:wfs="http://www.opengis.net/wfs"
        xmlns:ogc="http://www.opengis.net/ogc"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.opengis.net/wfs
                            http://schemas.opengis.net/wfs/1.1.0/wfs.xsd">
        <ogc:Filter>
            <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>status</ogc:PropertyName>
                <ogc:Literal>rejected</ogc:Literal>
            </ogc:PropertyIsEqualTo>
        </ogc:Filter>
    </wfs:GetFeature>
    """

xml_filter_2_0_0 = """<?xml version="1.0" ?>
    <wfs:GetFeature service="WFS" version="2.0.0"
        xmlns:wfs="http://www.opengis.net/wfs/2.0"
            xmlns:fes="http://www.opengis.net/fes/2.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.opengis.net/wfs/2.0
                                http://schemas.opengis.net/wfs/2.0.02.0/wfs.xsd">
        <fes:Filter>
            <fes:PropertyIsEqualTo>
                <fes:ValueReference>status</fes:ValueReference>
                <fes:Literal>rejected</fes:Literal>
            </fes:PropertyIsEqualTo>
        </fes:Filter>
    </wfs:GetFeature>
    """


class TestPostRequest_v_1_1_0():

    def test_minimal_query(self):
        request = postrequest.PostRequest_1_1_0()
        request.create_query("ns:typename")

        elem = request._root.find(util.nspath("Query", WFS_NAMESPACE))

        assert elem.get("typeName") == "ns:typename"

    def test_basic_query(self):
        request = postrequest.PostRequest_1_1_0()
        request.create_query("ns:typename")
        request.set_maxfeatures(2)
        request.set_outputformat('JSON')
        request.set_startindex(0)
        request.set_propertyname(["genericName"])

        root = request._root
        elem = request._query.findtext("PropertyName")

        assert root.get("maxFeatures") == '2'
        assert root.get("outputFormat") == 'JSON'
        assert root.get("startIndex") == '0'
        assert elem == "genericName"

    def test_featureid_query_single(self):
        request = postrequest.PostRequest_1_1_0()
        request.create_query("ns:typename")
        request.set_featureid(["1"])

        filter_elem = request._query.find(util.nspath("Filter", OGC_NAMESPACE))
        equal_elem = filter_elem.find(util.nspath("PropertyIsEqualTo", OGC_NAMESPACE))
        propertyname = equal_elem.findtext(util.nspath("PropertyName", OGC_NAMESPACE))
        literal = equal_elem.findtext(util.nspath("Literal", OGC_NAMESPACE))

        assert filter_elem
        assert equal_elem
        assert propertyname == "id"
        assert literal == "1"

    def test_featureid_query_multiple(self):
        request = postrequest.PostRequest_1_1_0()
        request.create_query("ns:typename")
        request.set_featureid(["1", "2", "3"])

        filter_elem = request._query.find(util.nspath("Filter", OGC_NAMESPACE))
        or_elem = filter_elem.find(util.nspath("Or", OGC_NAMESPACE))
        equal_elem = or_elem.findall(util.nspath("PropertyIsEqualTo", OGC_NAMESPACE))
        propertyname = []
        literal = []
        for elem in equal_elem:
            propertyname.append(elem.findtext(util.nspath("PropertyName", OGC_NAMESPACE)))
            literal.append(elem.findtext(util.nspath("Literal", OGC_NAMESPACE)))

        assert filter_elem
        assert or_elem
        assert len(equal_elem) == 3
        assert propertyname[0] == "id"
        assert propertyname[1] == "id"
        assert propertyname[2] == "id"
        assert literal[0] == "1"
        assert literal[1] == "2"
        assert literal[2] == "3"

    def test_sortby_query_single(self):
        request = postrequest.PostRequest_1_1_0()
        request.create_query("ns:typename")
        request.set_sortby(["id"])

        sort_elem = request._query.find(util.nspath("SortBy", OGC_NAMESPACE))
        sortprop_elem = sort_elem.find(util.nspath("SortProperty", OGC_NAMESPACE))
        propertyname = sortprop_elem.findtext(util.nspath("PropertyName", OGC_NAMESPACE))

        assert sort_elem
        assert sortprop_elem
        assert propertyname == "id"

    def test_sortby_query_multiple(self):
        request = postrequest.PostRequest_1_1_0()
        request.create_query("ns:typename")
        request.set_sortby(["id", "type"])

        sort_elem = request._query.find(util.nspath("SortBy", OGC_NAMESPACE))
        sortprop_elem = sort_elem.findall(util.nspath("SortProperty", OGC_NAMESPACE))
        propertyname = []
        for elem in sortprop_elem:
            propertyname.append(elem.findtext(util.nspath("PropertyName", OGC_NAMESPACE)))

        assert sort_elem
        assert len(sortprop_elem) == 2
        assert propertyname[0] == "id"
        assert propertyname[1] == "type"

    def test_bbox_query(self):
        request = postrequest.PostRequest_1_1_0()
        request.create_query("ns:typename")
        request.set_bbox([10, 10, 20, 20])

        filter_elem = request._query.find(util.nspath("Filter", OGC_NAMESPACE))
        bbox_elem = filter_elem.find(util.nspath("BBOX", OGC_NAMESPACE))
        envel_elem = bbox_elem.find(util.nspath("Envelope", GML_NAMESPACE))
        lower_elem = envel_elem.findtext(util.nspath("lowerCorner", GML_NAMESPACE))
        higher_elem = envel_elem.findtext(util.nspath("upperCorner", GML_NAMESPACE))

        assert filter_elem
        assert bbox_elem
        assert envel_elem
        assert lower_elem == "10 10"
        assert higher_elem == "20 20"

    def test_filter_query(self):
        request = postrequest.PostRequest_1_1_0()
        request.create_query("ns:typename")
        request.set_filter(xml_filter_1_1_0)

        filter_elem = request._query.find(util.nspath("Filter", OGC_NAMESPACE))
        equal_elem = filter_elem.find(util.nspath("PropertyIsEqualTo", OGC_NAMESPACE))
        propertyname = equal_elem.findtext(util.nspath("PropertyName", OGC_NAMESPACE))
        literal = equal_elem.findtext(util.nspath("Literal", OGC_NAMESPACE))

        assert filter_elem
        assert equal_elem
        assert propertyname == "status"
        assert literal == "rejected"


class TestPostRequest_v_2_0_0():

    def test_minimal_query(self):
        request = postrequest.PostRequest_2_0_0()
        request.create_query("ns:typename")

        elem = request._root.find(util.nspath("Query", WFS20_NAMESPACE))

        assert elem.get("typenames") == "ns:typename"

    def test_basic_query(self):
        request = postrequest.PostRequest_2_0_0()
        request.create_query("ns:typename")
        request.set_maxfeatures(2)
        request.set_outputformat('JSON')
        request.set_startindex(0)
        request.set_propertyname(["genericName"])

        root = request._root
        elem = request._query.findtext("PropertyName")

        assert root.get("count") == '2'
        assert root.get("outputformat") == 'JSON'
        assert root.get("startIndex") == '0'
        assert elem == "genericName"

    def test_featureid_query_single(self):
        request = postrequest.PostRequest_2_0_0()
        request.create_query("ns:typename")
        request.set_featureid(["1"])

        filter_elem = request._query.find(util.nspath("Filter", FES_NAMESPACE))
        equal_elem = filter_elem.find(util.nspath("PropertyIsEqualTo", FES_NAMESPACE))
        propertyname = equal_elem.findtext(util.nspath("ValueReference", FES_NAMESPACE))
        literal = equal_elem.findtext(util.nspath("Literal", FES_NAMESPACE))

        assert filter_elem
        assert equal_elem
        assert propertyname == "id"
        assert literal == "1"

    def test_featureid_query_multiple(self):
        request = postrequest.PostRequest_2_0_0()
        request.create_query("ns:typename")
        request.set_featureid(["1", "2", "3"])

        filter_elem = request._query.find(util.nspath("Filter", FES_NAMESPACE))
        or_elem = filter_elem.find(util.nspath("Or", FES_NAMESPACE))
        equal_elem = or_elem.findall(util.nspath("PropertyIsEqualTo", FES_NAMESPACE))
        propertyname = []
        literal = []
        for elem in equal_elem:
            propertyname.append(elem.findtext(util.nspath("ValueReference", FES_NAMESPACE)))
            literal.append(elem.findtext(util.nspath("Literal", FES_NAMESPACE)))

        assert filter_elem
        assert or_elem
        assert len(equal_elem) == 3
        assert propertyname[0] == "id"
        assert propertyname[1] == "id"
        assert propertyname[2] == "id"
        assert literal[0] == "1"
        assert literal[1] == "2"
        assert literal[2] == "3"

    def test_sortby_query_single(self):
        request = postrequest.PostRequest_2_0_0()
        request.create_query("ns:typename")
        request.set_sortby(["id"])

        sort_elem = request._query.find(util.nspath("SortBy", FES_NAMESPACE))
        sortprop_elem = sort_elem.find(util.nspath("SortProperty", FES_NAMESPACE))
        propertyname = sortprop_elem.findtext(util.nspath("ValueReference", FES_NAMESPACE))

        assert sort_elem
        assert sortprop_elem
        assert propertyname == "id"

    def test_sortby_query_multiple(self):
        request = postrequest.PostRequest_2_0_0()
        request.create_query("ns:typename")
        request.set_sortby(["id", "type"])

        sort_elem = request._query.find(util.nspath("SortBy", FES_NAMESPACE))
        sortprop_elem = sort_elem.findall(util.nspath("SortProperty", FES_NAMESPACE))
        propertyname = []
        for elem in sortprop_elem:
            propertyname.append(elem.findtext(util.nspath("ValueReference", FES_NAMESPACE)))

        assert sort_elem
        assert len(sortprop_elem) == 2
        assert propertyname[0] == "id"
        assert propertyname[1] == "type"

    def test_bbox_query(self):
        request = postrequest.PostRequest_2_0_0()
        request.create_query("ns:typename")
        request.set_bbox([10, 10, 20, 20])

        filter_elem = request._query.find(util.nspath("Filter", FES_NAMESPACE))
        bbox_elem = filter_elem.find(util.nspath("BBOX", FES_NAMESPACE))
        envel_elem = bbox_elem.find(util.nspath("Envelope", GML32_NAMESPACE))
        lower_elem = envel_elem.findtext(util.nspath("lowerCorner", GML32_NAMESPACE))
        higher_elem = envel_elem.findtext(util.nspath("upperCorner", GML32_NAMESPACE))

        assert filter_elem
        assert bbox_elem
        assert envel_elem
        assert lower_elem == "10 10"
        assert higher_elem == "20 20"

    def test_filter_query(self):
        request = postrequest.PostRequest_2_0_0()
        request.create_query("ns:typename")
        request.set_filter(xml_filter_2_0_0)

        filter_elem = request._query.find(util.nspath("Filter", FES_NAMESPACE))
        equal_elem = filter_elem.find(util.nspath("PropertyIsEqualTo", FES_NAMESPACE))
        propertyname = equal_elem.findtext(util.nspath("ValueReference", FES_NAMESPACE))
        literal = equal_elem.findtext(util.nspath("Literal", FES_NAMESPACE))

        assert filter_elem
        assert equal_elem
        assert propertyname == "status"
        assert literal == "rejected"
