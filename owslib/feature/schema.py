# =============================================================================
# OWSLib. Copyright (C) 2015 Jachym Cepicky
#
# Contact email: jachym.cepicky@gmail.com
#
# =============================================================================
"""
Set of functions, which are suitable for DescribeFeatureType parsing and
generating layer schema description compatible with `fiona`
"""

import sys
from urllib.parse import urlencode, parse_qsl
from owslib.etree import etree
from owslib.namespaces import Namespaces
from owslib.util import findall, Authentication, openURL

MYNS = Namespaces()
XS_NAMESPACE = MYNS.get_namespace("xs")
GML_NAMESPACES = (
    MYNS.get_namespace("gml"),
    MYNS.get_namespace("gml311"),
    MYNS.get_namespace("gml32"),
)


def get_schema(
    url, typename, version="1.0.0", timeout=30, headers=None, username=None, password=None, auth=None
):
    """Parses DescribeFeatureType response and creates schema compatible
    with :class:`fiona`

    :param str url: url of the service
    :param str version: version of the service
    :param str typename: name of the layer
    :param int timeout: request timeout
    :param str username: service authentication username
    :param str password: service authentication password
    :param Authentication auth: instance of owslib.util.Authentication
    """
    if auth:
        if username:
            auth.username = username
        if password:
            auth.password = password
    else:
        auth = Authentication(username, password)
    url = _get_describefeaturetype_url(url, version, typename)
    root = _get_remote_describefeaturetype(url, timeout=timeout,
                                           headers=headers, auth=auth)

    if ":" in typename:
        typename = typename.split(":")[1]
    type_element = root.find("./{%s}element" % XS_NAMESPACE)
    if type_element is None:
        return None

    complex_type = type_element.attrib["type"].split(":")[1]
    elements = _get_elements(complex_type, root)
    nsmap = None
    if hasattr(root, "nsmap"):
        nsmap = root.nsmap
    return _construct_schema(elements, nsmap)


def _get_elements(complex_type, root):
    """Get attribute elements
    """

    found_elements = []
    element = findall(
        root,
        "{%s}complexType" % XS_NAMESPACE,
        attribute_name="name",
        attribute_value=complex_type,
    )[0]
    found_elements = findall(element, "{%s}element" % XS_NAMESPACE)

    return found_elements


def _get_datatype(element, schema_key, gml_key):
    """Extract the data type from an element based on different XML structure variants.

    :param element: The XML element to extract the data type from
    :param str schema_key: The XML namespace key for schema elements
    :param str gml_key: The XML namespace key for GML elements
    :return: The extracted data type as string
    """
    # Case 1: Type defined as attribute
    if "type" in element.attrib:
        data_type = element.attrib["type"]
        # Remove any namespace prefix
        if ":" in data_type:
            data_type = data_type.split(":")[-1]
        return data_type
    # Case 2: Reference to another element
    elif "ref" in element.attrib:
        return element.attrib["ref"].split(":")[-1]
    # Case 3: Type defined as SimpleType with Restriction
    simple_type = element.find(".//{%s}restriction" % XS_NAMESPACE)
    if simple_type is not None:
        return simple_type.attrib.get("base", "").replace(schema_key + ":", "")
    # Case 4: Complex Type Definition
    complex_type = element.find(".//{%s}complexType//{%s}element" % (XS_NAMESPACE, XS_NAMESPACE))
    if complex_type is not None and "type" in complex_type.attrib:
        return complex_type.attrib["type"].replace(schema_key + ":", "")
    return None


def _construct_schema(elements, nsmap):
    """Construct fiona schema based on given elements

    :param list Element: list of elements
    :param dict nsmap: namespace map
    :return dict: schema
    """
    if elements is None:
        return None

    schema = {"properties": {}, "required": [], "geometry": None}

    schema_key = None
    gml_key = None

    # if nsmap is defined, use it
    if nsmap:
        for key in nsmap:
            if key is not None:
                if nsmap[key] == XS_NAMESPACE:
                    schema_key = key
                if nsmap[key] in GML_NAMESPACES:
                    gml_key = key

    # if no nsmap keys are defined, we have to guess
    if gml_key is None:
        gml_key = "gml"

    if schema_key is None:
        schema_key = "xsd"

    mappings = {
        "PointPropertyType": "Point",
        "PolygonPropertyType": "Polygon",
        "LineStringPropertyType": "LineString",
        "MultiPointPropertyType": "MultiPoint",
        "MultiLineStringPropertyType": "MultiLineString",
        "MultiPolygonPropertyType": "MultiPolygon",
        "MultiGeometryPropertyType": "MultiGeometry",
        "GeometryPropertyType": "GeometryCollection",
        "SurfacePropertyType": "3D Polygon",
        "MultiSurfacePropertyType": "3D MultiPolygon",
    }

    for element in elements:
        if "name" not in element.attrib:
            continue

        name = element.attrib["name"]
        non_nillable = element.attrib.get("nillable", "false") == "false"

        data_type = _get_datatype(element, schema_key, gml_key)
        if data_type is None:
            continue

        if data_type in mappings:
            schema["geometry"] = mappings[data_type]
            schema["geometry_column"] = name
        else:
            if schema_key is not None:
                schema["properties"][name] = data_type.replace(schema_key + ":", "")

        if non_nillable:
            schema["required"].append(name)

    if schema["properties"] or schema["geometry"]:
        return schema
    else:
        return None


def _get_describefeaturetype_url(url, version, typename):
    """Get url for describefeaturetype request

    :return str: url
    """

    query_string = []
    if url.find("?") != -1:
        query_string = parse_qsl(url.split("?")[1])

    params = [x[0] for x in query_string]

    if "service" not in params:
        query_string.append(("service", "WFS"))
    if "request" not in params:
        query_string.append(("request", "DescribeFeatureType"))
    if "version" not in params:
        query_string.append(("version", version))

    query_string.append(("typeName", typename))

    urlqs = urlencode(tuple(query_string))
    return url.split("?")[0] + "?" + urlqs


def _get_remote_describefeaturetype(url, timeout, headers, auth):
    """Gets the DescribeFeatureType response from the remote server.

    :param str url: url of the service
    :param int timeout: request timeout
    :param Authentication auth: instance of owslib.util.Authentication

    :return etree.Element with the root of the DescribeFeatureType response
    """
    res = openURL(url, timeout=timeout, headers=headers, auth=auth)
    return etree.fromstring(res.read())
