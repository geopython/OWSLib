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

from owslib.etree import etree, ParseError
from owslib import util
from owslib.namespaces import Namespaces
from owslib.util import nspath_eval, element_to_string

from owslib.util import log

from owslib.owscontext.common import is_empty, extract_p, \
    try_int, try_float

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


def ns_elem(ns_prefix, elem_name):
    ns_uri = ns.get(ns_prefix)
    if ns_uri is not None:
        return """{%(ns_uri)s}%(elem_name)s""" % {"ns_uri": ns_uri,
                                                  "elem_name": elem_name}


def parse_owc_content(content_node):
    mimetype = util.testXMLAttribute(content_node, 'type')
    url = util.testXMLAttribute(content_node, 'href')
    title = util.testXMLAttribute(content_node, 'title')
    child_elem = None
    if len(list(content_node)) > 0:
        child_elem = element_to_string(
            list(content_node)[0],False)

    content_dict = {
        "type": mimetype,
        "url": url,
        "content": str(child_elem),
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
                "previews": [],
                "data": [],
                "via": [],
            },
            'offerings': [],
            'active': None,
            'minscaledenominator': None,
            'maxscaledenominator': None,
            'folder': None
        }
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
    resource_base_dict['properties'].update({"title": title})

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
            # xmltxt = etree.tostring(
            #     list(val)[0], encoding='utf8', method='xml')
            xmltxt = element_to_string(
                list(val)[0], False)
            # TODO here parse geometry??
            # log.debug("entry: geometry %s :: %s", xmltxt, val)
            resource_base_dict.update({"geometry": xmltxt.decode('utf-8')})

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
    links_previews = []
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
            links_previews.append(link)
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
        {"previews": links_previews})
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
    offerings = []
    for offering_node in offering_nodes:
        offering_code = util.testXMLAttribute(offering_node, 'code')
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

        offering_dict = {
            "code": offering_code,
            "operations": operations,
            "contents": contents,
            "styles": styles
        }
        if offering_code is not None:
            offerings.append(offering_dict)

    resource_base_dict['properties'].update(
        {"offerings": offerings})

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


def decode_atomxml(xml_string):
    """
    here parse atom xml to a dict for instanciating of OWC:Context
    :param xmlstring:
    :return: OwcContext-ready dict
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
    feed_root = etree.fromstring(xml_string)
    # feed_root = etree.parse(xml_bytes)
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
            xmltxt = element_to_string(
                list(val)[0], False)
            # log.debug("geometry %s :: %s", xmltxt, val)
            context_base_dict['properties'].update({"bbox": xmltxt.decode('utf-8')})

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

    context_base_dict.update({"features": resources})
    return context_base_dict


def encode_atomxml(obj_d):
    """
    encode instance of OwcContext dict into atom xml encoding,
    because we can't do circular imports
    :param obj_d: the dict from owscontext to dict
    :return: b'atomxml'
    """

    # try:
    #     xml_tree = axml_context(obj_d)
    #     tree = etree.ElementTree(xml_tree)
    #     return tree
    # except TypeError as te:
    #     log.warn('problem encoding context to xml', te)
    #     raise te
    # except AttributeError as ae:
    #     log.warn('problem encoding context to xml', ae)
    #     raise ae
    # except ValueError as ve:
    #     log.warn('problem encoding context to xml', ve)
    #     raise ve
    # except ParseError as pe:
    #     log.warn('problem encoding context to xml', pe)
    #     raise pe
    xml_tree = axml_context(obj_d)
    tree = etree.ElementTree(xml_tree)
    return element_to_string(tree, encoding='utf-8', xml_declaration=False)


def axml_context(d):
    """
    encodes base OwcContext as dict to atom xml tree
    :param d:
    :return:
    """
    xml = etree.Element("feed", nsmap=ns)
    etree.SubElement(xml, "id").text = d['id']

    spec_reference = [axml_link(do) for do in
                      extract_p('properties.links.profiles', d, [])]
    [xml.append(el) for el in spec_reference if el is not None]

    area_of_interest = extract_p('bbox', d, None)
    if area_of_interest is not None:
        try:
            gml = etree.fromstring(area_of_interest)
            georss = etree.SubElement(xml, ns_elem("georss", "where"))
            georss.append(gml)
        except Exception as ex:
            log.warn('could encode bbox into georss:where', ex)
            pass

    context_metadata = [axml_link(do) for do in
                        extract_p('properties.links.via', d, [])]
    [xml.append(el) for el in context_metadata if el is not None]

    language = extract_p('properties.lang', d, None)
    if language is not None: xml.set(ns_elem("xml", "lang"), language)

    title = extract_p('properties.title', d, None)
    if title is not None: etree.SubElement(xml, "title").text = title

    # <subtitle type = "html"
    subtitle = extract_p('properties.abstract', d, None)
    if subtitle is not None: etree.SubElement(xml, "subtitle").text = subtitle

    update_date = extract_p('properties.updated', d, None)
    if update_date is not None: etree.SubElement(xml, "updated").text = update_date

    authors = [axml_author(do) for do in extract_p('properties.authors', d, [])]
    [xml.append(el) for el in authors if el is not None]

    publisher = extract_p('properties.publisher', d, None)
    if publisher is not None: etree.SubElement(xml, ns_elem("dc", "publisher")).text = publisher

    creator_application = axml_creator_app(extract_p('properties.generator', d, None))
    if creator_application is not None and not is_empty(creator_application): xml.append(creator_application)

    creator_display = axml_display(extract_p('properties.display', d, None))
    if creator_display is not None: xml.append(creator_display)

    rights = extract_p('properties.rights', d, None)
    if rights is not None: etree.SubElement(xml, "rights").text = rights

    time_interval_of_interest = extract_p('properties.date', d, None)
    if time_interval_of_interest is not None: etree.SubElement(xml,
                                                               ns_elem("dc", "date")).text = time_interval_of_interest

    keywords = [axml_category(do) for do in
                extract_p('properties.categories', d, [])]
    [xml.append(el) for el in keywords if el is not None]

    # here we generate single elements and attach them
    resources = [axml_resource(do) for do in
                 extract_p('features', d, [])]
    [xml.append(el) for el in resources if el is not None]

    return xml


def axml_resource(d):
    """
    encodes an OwcResource as dict into atom xml tree
    :param d:
    :return:
    """
    entry = etree.Element("entry", nsmap=ns)

    etree.SubElement(entry, "id").text = d['id']

    geospatial_extent = extract_p('geometry', d, None)
    if geospatial_extent is not None:
        try:
            gml = etree.fromstring(geospatial_extent)
            georss = etree.SubElement(entry, ns_elem("georss", "where"))
            georss.append(gml)
        except Exception as ex:
            log.warn('could encode geometry into georss:where', ex)
            pass

    title = d['properties']['title']
    if title is not None: etree.SubElement(entry, "title").text = title

    subtitle = extract_p('properties.abstract', d, None)
    # <content type = "text" >
    if subtitle is not None: etree.SubElement(entry, "content").text = subtitle

    update_date = extract_p('properties.updated', d, None)
    if update_date is not None: etree.SubElement(entry, "updated").text = update_date

    authors = [axml_author(do) for do in
               extract_p('properties.authors', d, [])]
    [entry.append(el) for el in authors if el is not None]

    publisher = extract_p('properties.publisher', d, None)
    if update_date is not None: etree.SubElement(entry, ns_elem("dc", "publisher")).text = publisher

    rights = extract_p('properties.rights', d, None)
    if update_date is not None: etree.SubElement(entry, ns_elem("dc", "rights")).text = rights

    temporal_extent = extract_p('properties.date', d, None)
    if temporal_extent is not None: etree.SubElement(entry, "date").text = temporal_extent

    keywords = [axml_category(do) for do in
                extract_p('properties.categories', d, [])]
    [entry.append(el) for el in keywords if el is not None]

    resource_metadata = [axml_link(do) for do in
                         extract_p('properties.links.via', d, [])]
    [entry.append(el) for el in resource_metadata if el is not None]

    content_description = [axml_content(do)
                           for do in extract_p(
            'properties.links.alternates', d, [])]
    [entry.append(el) for el in content_description if el is not None]

    preview = [axml_link(do) for do in
               extract_p('properties.links.preview', d, [])]
    [entry.append(el) for el in preview if el is not None]

    content_by_ref = [axml_link(do) for do in
                      extract_p('properties.links.data', d, [])]
    [entry.append(el) for el in content_by_ref if el is not None]

    offerings = [axml_offering(do) for do in
                 extract_p('properties.offerings', d, [])]
    [entry.append(el) for el in offerings if el is not None]

    # TODO no examples for active attribute
    active = extract_p('properties.active', d, None)
    if active is not None: etree.SubElement(entry, "active").text = active

    min_scale_denominator = try_float(extract_p(
        'properties.minscaledenominator', d, None))
    # <owc:minScaleDenominator>2500</owc:minScaleDenominator>
    if min_scale_denominator is not None: etree.SubElement(entry, ns_elem("owc",
                                                                          "minScaleDenominator")).text = str(min_scale_denominator)

    max_scale_denominator = try_float(extract_p(
        'properties.maxscaledenominator', d, None))
    # <owc:maxScaleDenominator>25000</owc:maxScaleDenominator>
    if max_scale_denominator is not None: etree.SubElement(entry, ns_elem("owc",
                                                                          "maxScaleDenominator")).text = str(max_scale_denominator)

    # TODO no examples for folder attribute
    folder = extract_p('properties.folder', d, None)
    if folder is not None: etree.SubElement(entry, "folder").text = folder

    # xml.append(entry)
    return entry


def axml_creator_app(d):
    # <generator uri="http://w.." version="1.0">MiraMon</generator>
    if is_empty(d):
        return None
    else:
        try:
            creator_app = etree.Element("generator", nsmap=ns)
            title = extract_p('title', d, None)
            if title is not None: creator_app.text = title
            uri = extract_p('uri', d, None)
            if uri is not None: creator_app.set("uri", uri)
            version = extract_p('version', d, None)
            if version is not None: creator_app.set("version", version)
            return creator_app
        except Exception as ex:
            log.warn('could encode creator_app', ex)
            return None


def axml_display(d):
    # <owc:display>
    # 		<owc:pixelWidth>
    if is_empty(d):
        return None
    else:
        try:
            creator_display = etree.Element(ns_elem("owc", "display"), nsmap=ns)
            pixel_width = try_int(extract_p('pixelWidth', d, None))
            if pixel_width is not None: etree.SubElement(creator_display,
                                                         ns_elem("owc", "pixelWidth")).text = str(pixel_width)
            pixel_height = try_int(extract_p('pixelHeight', d, None))
            if pixel_height is not None: etree.SubElement(creator_display,
                                                          ns_elem("owc", "pixelHeight")).text = str(pixel_height)
            mm_per_pixel = try_float(extract_p('mmPerPixel', d, None))
            if mm_per_pixel is not None: etree.SubElement(creator_display,
                                                          ns_elem("owc", "mmPerPixel")).text = str(mm_per_pixel)
            return creator_display
        except Exception as ex:
            log.warn('could encode creator_display', ex)
            return None


def axml_link(d):
    # < link rel = "via" type = "application/xml" href = "..." title = "..."
    if is_empty(d):
        return None
    else:
        try:
            link = etree.Element("link", nsmap=ns)
            href = extract_p('href', d, None)
            if href is not None: link.set("href", href)
            rel = extract_p('rel', d, None)
            if rel is not None: link.set("rel", rel)
            mimetype = extract_p('type', d, None)
            if mimetype is not None: link.set("type", mimetype)
            lang = extract_p('lang', d, None)
            if lang is not None: link.set("lang", lang)
            title = extract_p('title', d, None)
            if title is not None: link.set("title", title)
            length = try_int(extract_p('length', d, None))
            if length is not None: link.set("length", str(length))
            return link
        except Exception as ex:
            log.warn('could not encode link', ex)
            return None


def axml_category(d):
    # <category term="maps" label="This file contains maps"/>
    if is_empty(d):
        return None
    else:
        try:
            category = etree.Element("category", nsmap=ns)
            term = extract_p('term', d, None)
            if term is not None: category.set("term", term)
            scheme = extract_p('scheme', d, None)
            if scheme is not None: category.set("scheme", scheme)
            label = extract_p('label', d, None)
            if label is not None: category.set("label", label)
            return category
        except Exception as ex:
            log.warn('could encode category', ex)
            return None


def axml_author(d):
    # <author> ..
    # 		<name>
    #       <email>
    if is_empty(d):
        return None
    else:
        try:
            author = etree.Element("author", nsmap=ns)
            name = extract_p('name', d, None)
            if name is not None: etree.SubElement(author, "name").text = name
            email = extract_p('email', d, None)
            if email is not None: etree.SubElement(author, "email").text = email
            uri = extract_p('uri', d, None)
            if uri is not None: etree.SubElement(author, "uri").text = uri
            return author
        except Exception as ex:
            log.warn('could encode author', ex)
            return None


def axml_offering(d):
    # <owc:offering code="http://www.opengis.net/spec/owc-at...">
    #   <owc:offering code="http://www.opengis.net/spec....l">
    # 			<owc:content type="application/gml+xml">
    if is_empty(d):
        return None
    else:
        try:
            offering_code = extract_p('code', d, None)
            offering = etree.Element(ns_elem("owc", "offering"), attrib={"code": offering_code}, nsmap=ns)

            # use axml_operation here
            operations = [axml_operation(do) for do in
                          extract_p('operations', d, [])]
            [offering.append(el) for el in operations if el is not None]
            # use axml_content here
            contents = [axml_content(do) for do in
                        extract_p('contents', d, [])]
            [offering.append(el) for el in contents if el is not None]
            # use axml_styeset here
            styles = [axml_styleset(do) for do in
                      extract_p('styles', d, [])]
            [offering.append(el) for el in styles if el is not None]
            return offering
        except Exception as ex:
            log.warn('could encode offering', ex)
            return None


def axml_operation(d):
    #   <owc:operation code="GetCapabilities" method="GET"
    #       type="applica..." href="..."
    #       <owc:request type="application/xml"> ..
    # etree.SubElement(entry, ns_elem("owc", "offering"), name="blah").text = "some value1"
    if is_empty(d):
        return None
    else:
        try:
            operation = etree.Element(ns_elem("owc", "operation"), nsmap=ns)

            operations_code = extract_p('code', d, None)
            if operations_code is not None: operation.set("code", operations_code)
            http_method = extract_p('method', d, None)
            if http_method is not None: operation.set("method", http_method)
            mimetype = extract_p('type', d, None)
            if mimetype is not None: operation.set("type", mimetype)
            request_url = extract_p('href', d, None)
            if request_url is not None: operation.set("href", request_url)

            # use axml_content here
            request = extract_p('request', d, None)
            request_enc = None if request is None else axml_content(request)
            if request_enc is not None: operation.append(request_enc)
            # use axml_content here
            result = extract_p('result', d, None)
            result_enc = None if result is None else axml_content(result)
            if result_enc is not None: operation.append(result_enc)
            return operation
        except Exception as ex:
            log.warn('could encode operation', ex)
            return None


def axml_styleset(d):
    #     <owc:styleSet>
    #       <owc:name>raster</owc:name>
    #       <owc:title>Default Raster</owc:title>
    #       <owc:abstract>A sample style that draws a </owc:abstract>
    #       <owc:legendURL href="h...." type="image/png"/>
    #     </owc:styleSet>
    if is_empty(d):
        return None
    else:
        try:
            styleset = etree.Element(ns_elem("owc", "styleSet"), nsmap=ns)

            name = extract_p('name', d, None)
            if name is not None: etree.SubElement(styleset, ns_elem("owc", "name")).text = name
            title = extract_p('title', d, None)
            if title is not None: etree.SubElement(styleset, ns_elem("owc", "title")).text = title
            subtitle = extract_p('abstract', d, None)
            if subtitle is not None: etree.SubElement(styleset, ns_elem("owc", "abstract")).text = subtitle
            is_default = extract_p('default', d, None)
            # TODO no example for default setting on style set
            if is_default is not None: etree.SubElement(styleset, ns_elem("owc", "default")).text = is_default
            legend_url = extract_p('legendURL', d, None)
            if legend_url is not None: etree.SubElement(styleset, ns_elem("owc", "legendURL")).text = legend_url
            # TODO no example for content on style set
            content = extract_p('content', d, None)
            content_enc = None if content is None else axml_content(content)
            if content_enc is not None: styleset.append(content_enc)
            return styleset
        except Exception as ex:
            log.warn('could encode styleset', ex)
            return None


def axml_content(d):
    """
    OwcContent dict to Atom XML
    :param d:
    :return:
    """
    #   <owc:content type="image/tiff" href=".."
    if is_empty(d):
        return None
    else:
        try:
            content_elem = etree.Element(ns_elem("owc", "content"), nsmap=ns)

            mimetype = extract_p('type', d, None)
            if mimetype is not None: content_elem.set("type", mimetype)
            url = extract_p('url', d, None)
            if url is not None: content_elem.set("href", url)
            title = extract_p('title', d, None)
            if title is not None: content_elem.set("title", title)

            content = extract_p('content', d, None)
            if content is None: content_elem.text = content
            return content_elem
        except Exception as ex:
            log.warn('could encode content', ex)
            return None
