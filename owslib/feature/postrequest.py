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
        self._wfsnamespace = namespace
        self._query = None

    def _create_query(self, typename):
        self._query = etree.SubElement(self._root, util.nspath('Query', self._wfsnamespace))

    def set_featureversion(self, version):
        self._query.set("featureVersion", version)

    def set_propertyname(self, propertyname):
        """Set which feature properties will be returned.

        If not set, will return all properties."""
        for pn in propertyname:
            etree.SubElement(self._query, "PropertyName").text = pn

    def set_startindex(self, startindex):
        """Set the starting index value for the request"""
        self._root.set("startIndex", str(startindex))

    def to_string(self):
        """Returns the xml request in string format.

        Required in order to use the request with getfeature()"""
        return etree.tostring(self._root)


class PostRequest_1_1_0(PostRequest):
    """XML Post request payload builder for WFS version 1.1.0"""

    def __init__(self):
        super().__init__(version='1.1.0', namespace=WFS_NAMESPACE)

    def create_query(self, typename):
        """Creates the query tag with the corresponding typenames.
        Required element for each request."""
        super()._create_query(typename)
        self._query.set("typeName", typename)

    def set_bbox(self, bbox):
        """Set a bbox filter.

        Cannot be used with set_featureid() or set_filter().
        """
        filter_tree = etree.SubElement(self._query, util.nspath('Filter', OGC_NAMESPACE))
        bbox_tree = etree.SubElement(filter_tree, util.nspath('BBOX', OGC_NAMESPACE))
        coords = etree.SubElement(bbox_tree, util.nspath('Envelope', GML_NAMESPACE))
        if len(bbox) > 4:
            coords.set('srsName', bbox[4])
        lower = etree.SubElement(coords, util.nspath('lowerCorner', GML_NAMESPACE))
        lower.text = '{} {}'.format(bbox[0], bbox[1])

        upper = etree.SubElement(coords, util.nspath('upperCorner', GML_NAMESPACE))
        upper.text = '{} {}'.format(bbox[2], bbox[3])

    def set_featureid(self, featureid):
        """Set filter by feature id.

        Cannot be used with set_bbox() or set_filter().
        """
        feature_tree = etree.SubElement(self._query, util.nspath('Filter', OGC_NAMESPACE))

        for ft in featureid:
            prop_id = etree.Element(util.nspath('GmlObjectId', OGC_NAMESPACE))
            prop_id.set(util.nspath('id', GML_NAMESPACE), ft)
            feature_tree.append(prop_id)

    def set_filter(self, filter):
        """Set filter from existing filter.

        Will integrate the filter tag of a provided xml filter to the query being built.

        Cannot be used with set_bbox() or set_featureid().
        """
        f = etree.fromstring(filter)
        sub_elem = f.find(util.nspath("Filter", OGC_NAMESPACE))
        self._query.append(sub_elem)

    def set_maxfeatures(self, maxfeatures):
        """Set the maximum number of features to be returned."""
        self._root.set("maxFeatures", str(maxfeatures))

    def set_outputformat(self, outputFormat):
        """Set the output format.

        Verify the available formats with a GetCapabilites request."""
        self._root.set("outputFormat", outputFormat)

    def set_sortby(self, sortby):
        """Set the properties by which the response will be sorted."""
        sort_tree = etree.SubElement(self._query, util.nspath("SortBy", OGC_NAMESPACE))
        for s in sortby:
            prop_elem = etree.SubElement(sort_tree, util.nspath("SortProperty", OGC_NAMESPACE))
            prop_name = etree.SubElement(prop_elem, util.nspath('PropertyName', OGC_NAMESPACE))
            prop_name.text = s


class PostRequest_2_0_0(PostRequest):
    """XML Post request payload builder for WFS version 2.0.0."""

    def __init__(self):
        super().__init__(version='2.0.0', namespace=WFS20_NAMESPACE)

    def create_query(self, typename):
        """Creates the query tag with the corresponding typenames.
        Required element for each request ecept for stored queries."""
        super()._create_query(typename)
        self._query.set("typenames", typename)

    def create_storedquery(self, stored_id, parameters):
        """Create the storedQuery tag and configure it's sub elements and attributes."""
        storedquery = etree.SubElement(self._root, util.nspath('StoredQuery', self._wfsnamespace))
        storedquery.set("id", str(stored_id))
        for param in parameters:
            p = etree.SubElement(storedquery, util.nspath('Parameter', self._wfsnamespace))
            p.set("name", param)
            p.text = parameters[param]

    def set_bbox(self, bbox):
        """Set a bbox filter.

        Cannot be used with set_featureid() or set_filter().
        """
        filter_tree = etree.SubElement(self._query, util.nspath('Filter', FES_NAMESPACE))
        bbox_tree = etree.SubElement(filter_tree, util.nspath('BBOX', FES_NAMESPACE))
        coords = etree.SubElement(bbox_tree, util.nspath('Envelope', GML32_NAMESPACE))
        if len(bbox) > 4:
            coords.set('srsName', bbox[4])

        lower = etree.SubElement(coords, util.nspath('lowerCorner', GML32_NAMESPACE))
        lower.text = '{} {}'.format(bbox[0], bbox[1])

        upper = etree.SubElement(coords, util.nspath('upperCorner', GML32_NAMESPACE))
        upper.text = '{} {}'.format(bbox[2], bbox[3])

    def set_featureid(self, featureid):
        """Set filter by feature id.

        Cannot be used with set_bbox() or set_filter().
        """
        feature_tree = etree.SubElement(self._query, util.nspath('Filter', FES_NAMESPACE))
        for ft in featureid:
            prop_id = etree.Element(util.nspath('ResourceId', FES_NAMESPACE))
            prop_id.set('rid', ft)
            feature_tree.append(prop_id)

    def set_filter(self, filter):
        """Set filter from existing filter.

        Will integrate the filter tag of a provided xml filter to the current one
        being built.

        Cannot be used with set_bbox() or set_featureid().
        """
        f = etree.fromstring(filter)
        sub_elem = f.find(util.nspath("Filter", FES_NAMESPACE))
        self._query.append(sub_elem)

    def set_maxfeatures(self, maxfeatures):
        """Set the maximum number of features to be returned."""
        self._root.set("count", str(maxfeatures))

    def set_outputformat(self, outputFormat):
        """Set the output format.

        Verify the available formats with a GetCapabilites request.
        """
        self._root.set("outputformat", outputFormat)

    def set_sortby(self, sortby):
        """Set the properties by which the response will be sorted."""
        sort_tree = etree.SubElement(self._query, util.nspath("SortBy", FES_NAMESPACE))
        for s in sortby:
            prop_elem = etree.SubElement(sort_tree, util.nspath("SortProperty", FES_NAMESPACE))
            value = etree.SubElement(prop_elem, util.nspath('ValueReference', FES_NAMESPACE))
            value.text = s
