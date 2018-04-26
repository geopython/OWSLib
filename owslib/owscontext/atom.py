# -*- coding: utf-8 -*-
# =============================================================================
# Authors : Alexander Kmoch <allixender@gmail.com>
#
# =============================================================================

"""
API for OGC Web Services Context Document (OWS Context) format.

ATOM XML Encoding: http://www.opengeospatial.org/standards/owc

OGC OWS Context Atom Encoding Standard 1.0 (12-084r2)
"""

from __future__ import (absolute_import, division, print_function)

from owslib.etree import etree
from owslib import util
from owslib.namespaces import Namespaces
from owslib.util import nspath_eval

from owslib.util import log

from owslib.owscontext.common import is_empty

# default variables
add_namespaces = {"georss": "http://www.georss.org/georss",
                  "owc": "http://www.opengis.net/owc/1.0",
                  "xml": "http://www.w3.org/XML/1998/namespace"}


def get_namespaces():
    n = Namespaces()
    ns = n.get_namespaces(["atom", "dc", "gml", "gml32", "xlink"])
    ns.update(add_namespaces)
    ns[None] = n.get_namespace("atom")
    return ns


ns = get_namespaces()


def nspv(path):
    """
    short-hand syntax seen in waterml2.py
    :param path: xpath namespace aware
    :return: xml element
    """
    return nspath_eval(path, ns)


def parse_owc_content(content_node):
    mimetype = util.testXMLAttribute(content_node, 'type')
    url = util.testXMLAttribute(content_node, 'href')
    title = util.testXMLAttribute(content_node, 'title')
    child_elem = None
    if len(list(content_node)) > 0:
        child_elem = etree.tostring(
            list(content_node)[0], encoding='utf8', method='xml')

    content_dict = {
        "type": mimetype,
        "url": url,
        "content": child_elem,
        "title": title
    }
    return content_dict


def parse_entry(entry_node):
    """
    parse an aotm entry into a feature/resource dict to build OwcResource from

    :param entry_node: xml element root node of the atom:entry
    :return: dictionary for OwcResource.from_dict()
    """
    resource_base_dict = {
        "type": "Feature",
        "id": None,
        "geometry": None,
        "properties": {
            'title': None,
            'abstract': None,
            'updated': None,
            'date': None,
            'authors': [],

            'publisher': None,
            'rights': None,
            'categories': [],
            "links": {
                "alternates": [],
                "preview": [],
                "data": [],
                "via": [],
            },
            'offerings': [],
            'active': None,
            'minscaledenominator': None,
            'maxscaledenominator': None,
            'folder': None
        },
        'features': []
    }

    # <id>ftp://ftp.remotesensing.org/pub/geotiff/samples/gdal_eg/cea.txt</id>
    val = entry_node.find(util.nspath_eval('atom:id', ns))
    id = util.testXMLValue(val)
    # log.debug("entry :id %s :: %s", id, val)
    resource_base_dict.update({"id": id})

    # <title>GeoTIFF Example</title>
    val = entry_node.find(util.nspath_eval('atom:title', ns))
    title = util.testXMLValue(val)
    # log.debug("entry: title %s :: %s", id, val)
    resource_base_dict.update({"title": title})

    # <updated>2011-11-01T00:00:00Z</updated>
    val = entry_node.find(util.nspath_eval('atom:updated', ns))
    update_date = util.testXMLValue(val)
    # log.debug("entry: updated %s :: %s", update_date, val)
    resource_base_dict['properties'].update({"updated": update_date})

    # <dc:publisher>
    val = entry_node.find(util.nspath_eval('dc:publisher', ns))
    publisher = util.testXMLValue(val)
    # log.debug("entry: dc:publisher %s :: %s", publisher, val)
    resource_base_dict['properties'].update({"publisher": publisher})

    # <dc:rights>
    val = entry_node.find(util.nspath_eval('dc:rights', ns))
    rights = util.testXMLValue(val)
    # log.debug("entry: rights %s :: %s", rights, val)
    resource_base_dict['properties'].update({"rights": rights})

    # <georss:where>
    val = entry_node.find(util.nspath_eval('georss:where', ns))
    if val is not None:
        if len(list(val)) > 0:
            xmltxt = etree.tostring(
                list(val)[0], encoding='utf8', method='xml')
            # TODO here parse geometry??
            # log.debug("entry: geometry %s :: %s", xmltxt, val)
            resource_base_dict['properties'].update({"geometry": xmltxt})

    # <content type = "text" > aka subtitle, aka abstract
    val = entry_node.find(util.nspath_eval('atom:content', ns))
    subtitle = util.testXMLValue(val)
    # log.debug("entry: subtitle %s :: %s", subtitle, val)
    resource_base_dict['properties'].update({"abstract": subtitle})

    # <author> ..
    # 		<name>
    #       <email>
    vals = entry_node.findall(util.nspath_eval('atom:author', ns))
    authors = []
    for val in vals:
        val_name = val.find(util.nspath_eval('atom:name', ns))
        val_email = val.find(util.nspath_eval('atom:email', ns))
        val_uri = val.find(util.nspath_eval('atom:uri', ns))
        name = util.testXMLValue(val_name)
        email = util.testXMLValue(val_email)
        uri = util.testXMLValue(val_uri)
        author = {
            "name": name,
            "email": email,
            "uri": uri
        }
        # log.debug("entry: author %s :: %s", author, vals)
        if not is_empty(author):
            authors.append(author)

    resource_base_dict['properties'].update({"authors": authors})

    # <link rel="enclosure" type="image/png"
    #   length="12345" title="..." href="http://o..."/>
    # <link rel="icon" type="image/png" title="Preview f..."
    #   href="http://..."/>
    # <link rel="via" type="application/vnd.ogc.wms_xml"
    #   title="Original .." href="...."/>
    vals = entry_node.findall(util.nspath_eval('atom:link', ns))
    links_alternates = []
    links_preview = []
    links_data = []
    links_via = []
    for val in vals:
        rel = util.testXMLAttribute(val, 'rel')
        href = util.testXMLAttribute(val, 'href')
        mimetype = util.testXMLAttribute(val, 'type')
        lang = util.testXMLAttribute(val, 'lang')
        title = util.testXMLAttribute(val, 'title')
        length = util.testXMLAttribute(val, 'length')
        link = {
            "href": href,
            "type": mimetype,
            "length": length,
            "lang": lang,
            "title": title,
            "rel": rel
        }
        # log.debug("entry: link %s :: %s", link, vals)
        if link.get("rel") == "alternate" and not is_empty(link):
            links_alternates.append(link)
        elif link.get("rel") == "icon" and not is_empty(link):
            links_preview.append(link)
        elif link.get("rel") == "enclosure" and not is_empty(link):
            links_data.append(link)
        elif link.get("rel") == "via" and not is_empty(link):
            links_via.append(link)
        else:
            log.warn(
                "unknown link type in Ows Resource entry section: %r", link)

    resource_base_dict['properties']['links'].update(
        {"alternates": links_alternates})
    resource_base_dict['properties']['links'].update(
        {"preview": links_preview})
    resource_base_dict['properties']['links'].update({"data": links_data})
    resource_base_dict['properties']['links'].update({"via": links_via})

    # <owc:offering code="http://www.opengis.net/spec/owc-at...">
    #   <owc:content type="image/tiff" href=".."
    #   <owc:offering code="http://www.opengis.net/spec....l">
    # 			<owc:content type="application/gml+xml">
    #   <owc:operation code="GetCapabilities" method="GET"
    #       type="applica..." href="..."
    #       <owc:request type="application/xml"> ..
    #     <owc:styleSet>
    #       <owc:name>raster</owc:name>
    #       <owc:title>Default Raster</owc:title>
    #       <owc:abstract>A sample style that draws a </owc:abstract>
    #       <owc:legendURL href="h...." type="image/png"/>
    #     </owc:styleSet>
    offering_nodes = entry_node.findall(util.nspath_eval('owc:offering', ns))
    for offering_node in offering_nodes:
        operations = []
        contents = []
        styles = []
        operation_nodes = offering_node.findall(
            util.nspath_eval('owc:operation', ns))
        for op_val in operation_nodes:
            operations_code = util.testXMLAttribute(op_val, 'code')
            http_method = util.testXMLAttribute(op_val, 'method')
            mimetype = util.testXMLAttribute(op_val, 'type')
            request_url = util.testXMLAttribute(op_val, 'href')
            req_content_val = val.find(util.nspath_eval('owc:request', ns))
            req_content = None
            if req_content_val is not None:
                request_content = parse_owc_content(req_content_val)

            # TODO no example for result/response
            op_dict = {
                "code": operations_code,
                "method": http_method,
                "type": mimetype,
                "href": request_url,
                "request": None if is_empty(req_content) else req_content,
                "result": None
            }
            # log.debug("entry: operation %s :: %s", op_dict, vals)
            if not is_empty(op_dict):
                operations.append(op_dict)

        content_nodes = offering_node.findall(
            util.nspath_eval('owc:content', ns))
        for cont_val in content_nodes:
            content_dict = parse_owc_content(cont_val)
            # log.debug("entry: content_dict %s :: %s", content_dict, vals)
            if not is_empty(content_dict):
                contents.append(content_dict)

        style_nodes = offering_node.findall(
            util.nspath_eval('owc:styleSet', ns))
        for style_val in style_nodes:
            val_name = style_val.find(util.nspath_eval('owc:name', ns))
            val_title = style_val.find(util.nspath_eval('owc:title', ns))
            val_abstr = style_val.find(util.nspath_eval('owc:abstract', ns))
            val_uri = style_val.find(util.nspath_eval('owc:legendURL', ns))
            name = util.testXMLValue(val_name)
            title = util.testXMLValue(val_title)
            abstr = util.testXMLValue(val_abstr)
            legend_url = util.testXMLAttribute(val_uri, 'href')
            style_set = {
                "name": name,
                "title": title,
                "abstract": abstr,
                "default": None,
                "legendURL": legend_url,
                "content": None
            }
            # log.debug("entry: style_set %s :: %s", style_set, vals)
            if not is_empty(style_set):
                styles.append(style_set)

    # TODO no examples for active attribute
    # <owc:minScaleDenominator>2500</owc:minScaleDenominator>
    val = entry_node.find(util.nspath_eval('owc:minScaleDenominator', ns))
    min_scale_denominator = util.testXMLValue(val)
    # log.debug("entry: min-scale-... %s :: %s", min_scale_denominator, val)
    resource_base_dict['properties'].update(
        {"minscaledenominator": min_scale_denominator})

    # <owc:maxScaleDenominator>25000</owc:maxScaleDenominator>
    val = entry_node.find(util.nspath_eval('owc:maxScaleDenominator', ns))
    max_scale_denominator = util.testXMLValue(val)
    # log.debug("entry: max_scale_... %s :: %s", max_scale_denominator, val)
    resource_base_dict['properties'].update(
        {"maxscaledenominator": max_scale_denominator})
    # TODO no examples for folder attribute

    return resource_base_dict


def decode_atomxml(xml_bytes):
    """
    here parse atom xml to a dict for instanciating of OWC:Context
    :param xmlstring:
    :return: OwcContext-reday dict
    """
    context_base_dict = {
        "type": "FeatureCollection",
        "id": None,
        "bbox": None,
        "properties": {
            "lang": None,
            "links": {
                "profiles": [],
                "via": [],
            },
            'title': None,
            'abstract': None,
            'updated': None,
            'authors': [],
            'publisher': None,
            'generator': None,
            'display': None,
            'rights': None,
            'date': None,
            'categories': [],
        },
        'features': []
    }
    feed_root = etree.fromstring(xml_bytes)
    # feed_root xml lang use?
    # # log.debug(feed_root)
    # feed xml:lang=en
    # lang = feed_root.get('{http://www.w3.org/XML/1998/namespace}lang')
    lang = util.testXMLAttribute(
        feed_root, '{http://www.w3.org/XML/1998/namespace}lang')
    # log.debug("lang %s ", lang)
    context_base_dict['properties'].update({"lang": lang})

    # <id>
    val = feed_root.find(util.nspath_eval('atom:id', ns))
    id = util.testXMLValue(val)
    # log.debug("id %s :: %s", id, val)
    context_base_dict.update({"id": id})

    # <link rel="profile"
    #   href="http://www.opengis.net/spec/owc-atom/1.0/req/core"
    #   title="compliant bla bla"
    # < link rel = "via" type = "application/xml" href = "..." title = "..."
    vals = feed_root.findall(util.nspath_eval('atom:link', ns))
    links_profile = []
    links_via = []
    for val in vals:
        rel = util.testXMLAttribute(val, 'rel')
        href = util.testXMLAttribute(val, 'href')
        mimetype = util.testXMLAttribute(val, 'type')
        lang = util.testXMLAttribute(val, 'lang')
        title = util.testXMLAttribute(val, 'title')
        length = util.testXMLAttribute(val, 'length')
        link = {
            "href": href,
            "type": mimetype,
            "length": length,
            "lang": lang,
            "title": title,
            "rel": rel
        }
        # log.debug("link %s :: %s", link, vals)
        if link.get("rel") == "profile" and not is_empty(link):
            links_profile.append(link)
        elif link.get("rel") == "via" and not is_empty(link):
            links_via.append(link)
        else:
            log.warn("unknown link type in Ows Context section: %r", link)

    context_base_dict['properties']['links'].update(
        {"profiles": links_profile})
    context_base_dict['properties']['links'].update({"via": links_via})

    # <title>
    val = feed_root.find(util.nspath_eval('atom:title', ns))
    title = util.testXMLValue(val)
    # log.debug("title %s :: %s", title, val)
    context_base_dict['properties'].update({"title": title})

    # <subtitle type = "html"
    val = feed_root.find(util.nspath_eval('atom:subtitle', ns))
    subtitle = util.testXMLValue(val)
    # log.debug("subtitle %s :: %s", subtitle, val)
    context_base_dict['properties'].update({"abstract": subtitle})

    # <author> ..
    # 		<name>
    #       <email>
    vals = feed_root.findall(util.nspath_eval('atom:author', ns))
    authors = []
    for val in vals:
        val_name = val.find(util.nspath_eval('atom:name', ns))
        val_email = val.find(util.nspath_eval('atom:email', ns))
        val_uri = val.find(util.nspath_eval('atom:uri', ns))
        name = util.testXMLValue(val_name)
        email = util.testXMLValue(val_email)
        uri = util.testXMLValue(val_uri)
        author = {
            "name": name,
            "email": email,
            "uri": uri
        }
        # log.debug("author %s :: %s", author, vals)
        if not is_empty(author):
            authors.append(author)

    context_base_dict['properties'].update({"authors": authors})

    # <georss:where>
    val = feed_root.find(util.nspath_eval('georss:where', ns))
    if val is not None:
        if len(list(val)) > 0:
            xmltxt = etree.tostring(
                list(val)[0], encoding='utf8', method='xml')
            # TODO here parse geometry??
            # log.debug("geometry %s :: %s", xmltxt, val)
            context_base_dict['properties'].update({"bbox": xmltxt})

    # <updated>2012-11-04T17:26:23Z</updated>
    val = feed_root.find(util.nspath_eval('atom:updated', ns))
    update_date = util.testXMLValue(val)
    # log.debug("updated %s :: %s", update_date, val)
    context_base_dict['properties'].update({"updated": update_date})

    # <dc:date>2009-01-23T09:08:56.000Z/2009-01-23T09:14:08.000Z</dc:date>
    val = feed_root.find(util.nspath_eval('dc:date', ns))
    time_interval_of_interest = util.testXMLValue(val)
    # log.debug("dc:date %s :: %s", time_interval_of_interest, val)
    context_base_dict['properties'].update(
        {"date": time_interval_of_interest})

    # <rights>
    val = feed_root.find(util.nspath_eval('atom:rights', ns))
    rights = util.testXMLValue(val)
    # log.debug("rights %s :: %s", rights, val)
    context_base_dict['properties'].update({"rights": rights})

    # <dc:publisher>
    val = feed_root.find(util.nspath_eval('dc:publisher', ns))
    publisher = util.testXMLValue(val)
    # log.debug("dc:publisher %s :: %s", publisher, val)
    context_base_dict['properties'].update({"publisher": publisher})

    # <owc:display>
    # 		<owc:pixelWidth>
    val_display = feed_root.find(util.nspath_eval('owc:display', ns))
    val_pixel_width = None if val_display is None \
        else val_display.find(util.nspath_eval('owc:pixelWidth', ns))
    val_pixel_height = None if val_display is None \
        else val_display.find(util.nspath_eval('owc:pixelHeight', ns))
    val_mm_per_pixel = None if val_display is None \
        else val_display.find(util.nspath_eval('owc:mmPerPixel', ns))
    pixel_width = util.testXMLValue(val_pixel_width)
    pixel_height = util.testXMLValue(val_pixel_height)
    mm_per_pixel = util.testXMLValue(val_mm_per_pixel)
    owc_display = {
        "pixelWidth": pixel_width,
        "pixelHeight": pixel_height,
        "mmPerPixel": mm_per_pixel
    }
    # log.debug("display %s :: %s", owc_display, val_display)
    if not is_empty(owc_display):
        context_base_dict['properties'].update({"display": owc_display})

    # <generator uri="http://w.." version="1.0">MiraMon</generator>
    val = feed_root.find(util.nspath_eval('atom:generator', ns))
    name = util.testXMLValue(val)
    version = util.testXMLAttribute(val, 'version')
    uri = util.testXMLAttribute(val, 'uri')
    owc_generator = {
        "name": name,
        "version": version,
        "uri": uri
    }
    # log.debug("generator %s :: %s", owc_generator, val)
    if not is_empty(owc_generator):
        context_base_dict['properties'].update({"generator": owc_generator})

    # <category term="maps" label="This file contains maps"/>
    vals = feed_root.findall(util.nspath_eval('atom:category', ns))
    categories = []
    for val in vals:
        term = util.testXMLAttribute(val, 'term')
        scheme = util.testXMLAttribute(val, 'scheme')
        label = util.testXMLAttribute(val, 'label')
        category = {
            "term": term,
            "scheme": scheme,
            "label": label
        }
        # log.debug("category %s :: %s", category, vals)
        if not is_empty(category):
            categories.append(category)

    context_base_dict['properties'].update({"categories": categories})

    # <entry> ...
    entries = feed_root.findall(util.nspath_eval('atom:entry', ns))
    resources = []
    for entry in entries:
        entry_dict = parse_entry(entry)
        if entry_dict.get("id") is not None:
            resources.append(entry_dict)
        else:
            log.warn("feature entry has no id, not allowed: skipping!")
            pass

    context_base_dict['properties'].update({"features": resources})
    return context_base_dict


def encode_atomxml(obj):
    """
    TODO implement this
    encode instance of OwcContext dict into atom xml encoding,
    because we can't do circular imports
    :param obj:
    :return: atomxml
    """
