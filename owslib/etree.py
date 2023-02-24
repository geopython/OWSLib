# =============================================================================
# OWSLib. Copyright (C) 2005 Sean C. Gillies
#
# Contact email: sgillies@frii.com
# =============================================================================


from lxml import etree
from lxml.etree import ParseError
ElementType = etree._Element

from owslib.namespaces import Namespaces


def patch_well_known_namespaces():
    """Monkey patches lxml.etree to add some well-known namespaces."""

    ns = Namespaces()

    try:
        register_namespace = etree.register_namespace
    except AttributeError:
        etree._namespace_map

        def register_namespace(prefix, uri):
            etree._namespace_map[uri] = prefix

    for k, v in list(ns.get_namespaces().items()):
        register_namespace(k, v)

    etree.set_default_parser(
        parser=etree.XMLParser(resolve_entities=False)
    )


patch_well_known_namespaces()
