# =============================================================================
# OWSLib. Copyright (C) 2005 Sean C. Gillies
#
# Contact email: sgillies@frii.com
# =============================================================================

from owslib.namespaces import Namespaces


def patch_well_known_namespaces(etree_module):
    """Monkey patches the etree module to add some well-known namespaces."""

    ns = Namespaces()

    try:
        register_namespace = etree_module.register_namespace
    except AttributeError:
        etree_module._namespace_map

        def register_namespace(prefix, uri):
            etree_module._namespace_map[uri] = prefix

    for k, v in list(ns.get_namespaces().items()):
        register_namespace(k, v)


# try to find lxml or elementtree
try:
    from lxml import etree
    from lxml.etree import ParseError
    ElementType = etree._Element
except ImportError:
    import xml.etree.ElementTree as etree
    ElementType = etree.Element
    try:
        from xml.etree.ElementTree import ParseError
    except ImportError:
        from xml.parsers.expat import ExpatError as ParseError

patch_well_known_namespaces(etree)
