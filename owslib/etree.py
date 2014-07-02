# =============================================================================
# OWSLib. Copyright (C) 2005 Sean C. Gillies
#
# Contact email: sgillies@frii.com
# =============================================================================

from six import iteritems, text_type, PY2


def patch_well_known_namespaces(etree_module):
    """Monkey patches the etree module to add some well-known namespaces."""
    import warnings
    from owslib.namespaces import Namespaces
    ns = Namespaces()

    try:
        register_namespace = etree_module.register_namespace
    except AttributeError:
        try:
            etree_module._namespace_map

            def register_namespace(prefix, uri):
                etree_module._namespace_map[uri] = prefix
        except AttributeError:
            def register_namespace(prefix, uri):
                pass
            warnings.warn("Only 'lxml.etree' >= 2.3 and 'xml.etree.ElementTree' >= 1.3 are fully supported!")

    for k, v in iteritems(ns.get_namespaces()):
        register_namespace(k, v)

# try to find lxml or elementtree
try:
    from lxml import etree

    if not PY2:
        _fromstring = etree.fromstring

        def _fromstring_encoded(text, *args, **kwargs):
            if isinstance(text, text_type):
                text = text.encode('utf8')
            return _fromstring(text, *args, **kwargs)

        etree.fromstring = _fromstring_encoded

    Element = etree._Element
except ImportError:
    try:
        # Python 2.5 with ElementTree included
        import xml.etree.ElementTree as etree
    except ImportError:
        try:
            # Python < 2.5 with ElementTree installed
            import elementtree.ElementTree as etree
        except ImportError:
            raise RuntimeError('You need either lxml or ElementTree to use OWSLib!')

    if PY2:
        Element = etree._Element
    else:
        Element = etree.Element

patch_well_known_namespaces(etree)
