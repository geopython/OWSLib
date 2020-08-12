# owslib imports:
from owslib import util
from owslib.etree import etree
from owslib.namespaces import Namespaces

n = Namespaces()
FES_NAMESPACE = n.get_namespace("fes")
GML_NAMESPACE = n.get_namespace("gml")
GML32_NAMESPACE = n.get_namespace("gml32")
OGC_NAMESPACE = n.get_namespace("ogc")
WFS_NAMESPACE = n.get_namespace("wfs")
WFS20_NAMESPACE = n.get_namespace("wfs20")


class PostRequest():
    """Superclass for POST request building"""

    def __init__(self, version=None, namespace=None):
        self._root = etree.Element(util.nspath('GetFeature', namespace))
        self._root.set("service", "WFS")
        self._root.set("version", version)
        self._query = etree.SubElement(self._root, util.nspath('Query', namespace))

    def set_startindex(self, startindex):
        self._root.set("startIndex", str(startindex))

    def set_propertyname(self, propertyname):
        for pn in propertyname:
            etree.SubElement(self._query, "PropertyName").text = pn

    def to_string(self):
        """Returns the xml request in string format"""
        return etree.tostring(self._root)


class PostRequest_1_1_0(PostRequest):
    """XML Post request payload builder for WFS version 1.1.0"""

    def __init__(self, version='1.1.0', namespace=WFS_NAMESPACE):
        super().__init__(version, namespace)

    def create_query(self, typename):
        """Creates the query tag with the corresponding typenames.
        Required element for each request."""
        self._query.set("typeName", typename)

    def set_bbox(self, bbox):
        filter_tree = etree.SubElement(self._query, util.nspath('Filter', OGC_NAMESPACE))
        bbox_tree = etree.SubElement(filter_tree, util.nspath('BBOX', OGC_NAMESPACE))
        coords = etree.SubElement(bbox_tree, util.nspath('Envelope', GML_NAMESPACE))
        etree.SubElement(coords, util.nspath('lowerCorner', GML_NAMESPACE)
                         ).text = '{} {}'.format(bbox[0], bbox[1])
        etree.SubElement(coords, util.nspath('upperCorner', GML_NAMESPACE)
                         ).text = '{} {}'.format(bbox[2], bbox[3])

    def set_featureid(self, featureid):
        feature_tree = etree.SubElement(self._query, util.nspath('Filter', OGC_NAMESPACE))
        if len(featureid) > 1:
            or_operator = etree.SubElement(feature_tree, util.nspath('Or', OGC_NAMESPACE))
        for ft in featureid:
            prop_equal = etree.Element(util.nspath('PropertyIsEqualTo', OGC_NAMESPACE))
            etree.SubElement(prop_equal, util.nspath('PropertyName', OGC_NAMESPACE)).text = "id"
            etree.SubElement(prop_equal, util.nspath('Literal', OGC_NAMESPACE)).text = ft
            if len(featureid) > 1:
                or_operator.append(prop_equal)
            else:
                feature_tree.append(prop_equal)

    def set_filter(self, filter):
        f = etree.fromstring(filter)
        sub_elem = f.find(util.nspath("Filter", OGC_NAMESPACE))
        self._query.append(sub_elem)

    def set_maxfeatures(self, maxfeatures):
        self._root.set("maxFeatures", str(maxfeatures))

    def set_outputformat(self, outputFormat):
        self._root.set("outputFormat", outputFormat)

    def set_sortby(self, sortby):
        sort_tree = etree.SubElement(self._query, util.nspath("SortBy", OGC_NAMESPACE))
        for s in sortby:
            prop = etree.SubElement(sort_tree, util.nspath("SortProperty", OGC_NAMESPACE))
            etree.SubElement(prop, util.nspath('PropertyName', OGC_NAMESPACE)).text = s


class PostRequest_2_0_0(PostRequest):
    """XML Post request payload builder for WFS version 2.0.0"""

    def __init__(self, version='2.0.0', namespace=WFS20_NAMESPACE):
        super().__init__(version, namespace)

    def create_query(self, typename):
        """Creates the query tag with the corresponding typenames.
        Required element for each request."""
        self._query.set("typenames", typename)

    def set_bbox(self, bbox):
        filter_tree = etree.SubElement(self._query, util.nspath('Filter', FES_NAMESPACE))
        bbox_tree = etree.SubElement(filter_tree, util.nspath('BBOX', FES_NAMESPACE))
        etree.SubElement(bbox_tree, util.nspath('ValueReference', FES_NAMESPACE))
        coords = etree.SubElement(bbox_tree, util.nspath('Envelope', GML32_NAMESPACE))
        etree.SubElement(coords, util.nspath('lowerCorner', FES_NAMESPACE)
                         ).text = '{} {}'.format(bbox[0], bbox[1])
        etree.SubElement(coords, util.nspath('upperCorner', GML32_NAMESPACE)
                         ).text = '{} {}'.format(bbox[2], bbox[3])

    def set_featureid(self, featureid):
        feature_tree = etree.SubElement(self._query, util.nspath('Filter', FES_NAMESPACE))
        if len(featureid) > 1:
            or_operator = etree.SubElement(feature_tree, util.nspath('Or', FES_NAMESPACE))
        for ft in featureid:
            prop_equal = etree.Element(util.nspath('PropertyIsEqualTo', FES_NAMESPACE))
            etree.SubElement(prop_equal, util.nspath('ValueReference', FES_NAMESPACE)).text = "id"
            etree.SubElement(prop_equal, util.nspath('Literal', FES_NAMESPACE)).text = ft
            if len(featureid) > 1:
                or_operator.append(prop_equal)
            else:
                feature_tree.append(prop_equal)

    def set_filter(self, filter):
        f = etree.fromstring(filter)
        sub_elem = f.find(util.nspath("Filter", FES_NAMESPACE))
        self._query.append(sub_elem)

    def set_maxfeatures(self, maxfeatures):
        self._root.set("count", str(maxfeatures))

    def set_outputformat(self, outputFormat):
        self._root.set("outputformat", outputFormat)

    def set_sortby(self, sortby):
        sort_tree = etree.SubElement(self._query, util.nspath("SortBy", FES_NAMESPACE))
        for s in sortby:
            prop = etree.SubElement(sort_tree, util.nspath("SortProperty", FES_NAMESPACE))
            etree.SubElement(prop, util.nspath('ValueReference', FES_NAMESPACE)).text = s
