from owslib.feature import postrequest
from owslib.etree import etree
from owslib.namespaces import Namespaces
from owslib import util
import pytest

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

raw_2_0_filter = """
    <fes:Filter  xmlns:fes="http://www.opengis.net/fes/2.0"
    xmlns:erl="http://xmlns.earthresourceml.org/earthresourceml-lite/1.0">
          <fes:PropertyIsEqualTo>
            <fes:ValueReference>reference</fes:ValueReference>
            <fes:Literal>gold</fes:Literal>
          </fes:PropertyIsEqualTo>
    </fes:Filter>
    """

typename = "ns:typename"


@pytest.fixture
def requestv110():
    request = postrequest.PostRequest_1_1_0()
    request.create_query(typename)
    return request


@pytest.fixture
def requestv200():
    request = postrequest.PostRequest_2_0_0()
    request.create_query(typename)
    return request


class TestPostRequest_v_1_1_0():

    def test_minimal_query(self, requestv110):

        elem = requestv110._root.find(util.nspath("Query", WFS_NAMESPACE))

        assert elem.get("typeName") == typename

    def test_basic_query(self, requestv110):
        requestv110.set_maxfeatures(2)
        requestv110.set_outputformat('JSON')
        requestv110.set_startindex(0)
        requestv110.set_propertyname(["genericName"])

        root = requestv110._root
        elem = requestv110._query.findtext("PropertyName")

        assert root.get("maxFeatures") == '2'
        assert root.get("outputFormat") == 'JSON'
        assert root.get("startIndex") == '0'
        assert elem == "genericName"

    def test_featureid_query_single(self, requestv110):
        requestv110.set_featureid(["1"])

        filter_elem = requestv110._query.find(util.nspath("Filter", OGC_NAMESPACE))
        resource_elem = filter_elem.find(util.nspath("GmlObjectId", OGC_NAMESPACE))

        assert filter_elem is not None
        assert resource_elem.get(util.nspath('id', GML_NAMESPACE)) == '1'

    def test_featureid_query_multiple(self, requestv110):
        requestv110.set_featureid(["1", "2", "3"])

        filter_elem = requestv110._query.find(util.nspath("Filter", OGC_NAMESPACE))
        resource_elem = filter_elem.findall(util.nspath("GmlObjectId", OGC_NAMESPACE))
        ids = []
        for elem in resource_elem:
            ids.append(elem.get(util.nspath('id', GML_NAMESPACE)))

        assert filter_elem is not None
        assert len(ids) == 3
        assert ids[0] == "1"
        assert ids[1] == "2"
        assert ids[2] == "3"

    def test_sortby_query_single(self, requestv110):
        requestv110.set_sortby(["id"])

        sort_elem = requestv110._query.find(util.nspath("SortBy", OGC_NAMESPACE))
        sortprop_elem = sort_elem.find(util.nspath("SortProperty", OGC_NAMESPACE))
        propertyname = sortprop_elem.findtext(util.nspath("PropertyName", OGC_NAMESPACE))

        assert sort_elem is not None
        assert sortprop_elem is not None
        assert propertyname == "id"

    def test_sortby_query_multiple(self, requestv110):
        requestv110.set_sortby(["id", "type"])

        sort_elem = requestv110._query.find(util.nspath("SortBy", OGC_NAMESPACE))
        sortprop_elem = sort_elem.findall(util.nspath("SortProperty", OGC_NAMESPACE))
        propertyname = []
        for elem in sortprop_elem:
            propertyname.append(elem.findtext(util.nspath("PropertyName", OGC_NAMESPACE)))

        assert sort_elem is not None
        assert len(sortprop_elem) == 2
        assert propertyname[0] == "id"
        assert propertyname[1] == "type"

    def test_bbox_query(self, requestv110):
        requestv110.set_bbox([10, 10, 20, 20])

        filter_elem = requestv110._query.find(util.nspath("Filter", OGC_NAMESPACE))
        bbox_elem = filter_elem.find(util.nspath("BBOX", OGC_NAMESPACE))
        envel_elem = bbox_elem.find(util.nspath("Envelope", GML_NAMESPACE))
        lower_elem = envel_elem.findtext(util.nspath("lowerCorner", GML_NAMESPACE))
        higher_elem = envel_elem.findtext(util.nspath("upperCorner", GML_NAMESPACE))

        assert filter_elem is not None
        assert bbox_elem is not None
        assert envel_elem is not None
        assert lower_elem == "10 10"
        assert higher_elem == "20 20"

    def test_filter_query(self, requestv110):
        requestv110.set_filter(xml_filter_1_1_0)

        filter_elem = requestv110._query.find(util.nspath("Filter", OGC_NAMESPACE))
        equal_elem = filter_elem.find(util.nspath("PropertyIsEqualTo", OGC_NAMESPACE))
        propertyname = equal_elem.findtext(util.nspath("PropertyName", OGC_NAMESPACE))
        literal = equal_elem.findtext(util.nspath("Literal", OGC_NAMESPACE))

        assert filter_elem is not None
        assert equal_elem is not None
        assert propertyname == "status"
        assert literal == "rejected"


class TestPostRequest_v_2_0_0():

    def test_minimal_query(self, requestv200):
        elem = requestv200._root.find(util.nspath("Query", WFS20_NAMESPACE))

        assert elem.get("typeNames") == typename

    def test_basic_query(self, requestv200):
        requestv200.set_maxfeatures(2)
        requestv200.set_outputformat('JSON')
        requestv200.set_startindex(0)
        requestv200.set_propertyname(["genericName"])

        root = requestv200._root
        elem = requestv200._query.findtext("PropertyName")

        assert root.get("count") == '2'
        assert root.get("outputformat") == 'JSON'
        assert root.get("startIndex") == '0'
        assert elem == "genericName"

    def test_create_storedquery(self):
        stored_params = {"city": "Washington", "elevation_m": "125"}
        request = postrequest.PostRequest_2_0_0()
        request.create_storedquery("stored_id_1", stored_params)

        stored_query_elem = request._root.find(util.nspath("StoredQuery", WFS20_NAMESPACE))
        assert stored_query_elem.get("id") == "stored_id_1"

        params = stored_query_elem.findall(util.nspath("Parameter", WFS20_NAMESPACE))
        assert params[0].get("name") == "city"
        assert params[0].text == "Washington"
        assert params[1].get("name") == "elevation_m"
        assert params[1].text == "125"

    def test_featureid_query_single(self, requestv200):
        requestv200.set_featureid(["1"])

        filter_elem = requestv200._query.find(util.nspath("Filter", FES_NAMESPACE))
        resource_elem = filter_elem.find(util.nspath("ResourceId", FES_NAMESPACE))

        assert filter_elem is not None
        assert resource_elem.get("rid") == "1"

    def test_featureid_query_multiple(self, requestv200):
        requestv200.set_featureid(["1", "2", "3"])

        filter_elem = requestv200._query.find(util.nspath("Filter", FES_NAMESPACE))
        resource_elems = filter_elem.findall(util.nspath("ResourceId", FES_NAMESPACE))
        ids = []
        for elem in resource_elems:
            ids.append(elem.get("rid"))

        assert filter_elem is not None
        assert len(ids) == 3
        assert ids[0] == "1"
        assert ids[1] == "2"
        assert ids[2] == "3"

    def test_sortby_query_single(self, requestv200):
        requestv200.set_sortby(["id"])

        sort_elem = requestv200._query.find(util.nspath("SortBy", FES_NAMESPACE))
        sortprop_elem = sort_elem.find(util.nspath("SortProperty", FES_NAMESPACE))
        propertyname = sortprop_elem.findtext(util.nspath("ValueReference", FES_NAMESPACE))

        assert sort_elem is not None
        assert sortprop_elem is not None
        assert propertyname == "id"

    def test_sortby_query_multiple(self, requestv200):
        requestv200.set_sortby(["id", "type"])

        sort_elem = requestv200._query.find(util.nspath("SortBy", FES_NAMESPACE))
        sortprop_elem = sort_elem.findall(util.nspath("SortProperty", FES_NAMESPACE))
        propertyname = []
        for elem in sortprop_elem:
            propertyname.append(elem.findtext(util.nspath("ValueReference", FES_NAMESPACE)))

        assert sort_elem is not None
        assert len(sortprop_elem) == 2
        assert propertyname[0] == "id"
        assert propertyname[1] == "type"

    def test_bbox_query(self, requestv200):
        requestv200.set_bbox([10, 10, 20, 20])

        filter_elem = requestv200._query.find(util.nspath("Filter", FES_NAMESPACE))
        bbox_elem = filter_elem.find(util.nspath("BBOX", FES_NAMESPACE))
        envel_elem = bbox_elem.find(util.nspath("Envelope", GML32_NAMESPACE))
        lower_elem = envel_elem.findtext(util.nspath("lowerCorner", GML32_NAMESPACE))
        higher_elem = envel_elem.findtext(util.nspath("upperCorner", GML32_NAMESPACE))

        assert filter_elem is not None
        assert bbox_elem is not None
        assert envel_elem is not None
        assert lower_elem == "10 10"
        assert higher_elem == "20 20"

    def test_filter_query(self, requestv200):
        requestv200.set_filter(xml_filter_2_0_0)

        filter_elem = requestv200._query.find(util.nspath("Filter", FES_NAMESPACE))
        equal_elem = filter_elem.find(util.nspath("PropertyIsEqualTo", FES_NAMESPACE))
        propertyname = equal_elem.findtext(util.nspath("ValueReference", FES_NAMESPACE))
        literal = equal_elem.findtext(util.nspath("Literal", FES_NAMESPACE))

        assert filter_elem is not None
        assert equal_elem is not None
        assert propertyname == "status"
        assert literal == "rejected"

    def test_filter_root_query(self, requestv200):
        """Same as test_filter_query, but the filter is the root element."""
        requestv200.set_filter(raw_2_0_filter)

        filter_elem = requestv200._query.find(util.nspath("Filter", FES_NAMESPACE))
        equal_elem = filter_elem.find(util.nspath("PropertyIsEqualTo", FES_NAMESPACE))
        propertyname = equal_elem.findtext(util.nspath("ValueReference", FES_NAMESPACE))
        literal = equal_elem.findtext(util.nspath("Literal", FES_NAMESPACE))

        assert filter_elem is not None
        assert equal_elem is not None
        assert propertyname == "reference"
        assert literal == "gold"
