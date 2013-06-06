# =============================================================================
# OWSLib. Copyright (C) 2005 Sean C. Gillies
#
# Contact email: sgillies@frii.com
# =============================================================================

def patch_well_known_namespaces(etree_module):

    from owslib.namespaces import Namespaces
    ns = Namespaces()

    """Monkey patches the etree module to add some well-known namespaces."""
    for k,v in ns.get_namespaces().iteritems():
        etree_module.register_namespace(k, v)

# try to find lxml or elementtree
try:
    from lxml import etree
    patch_well_known_namespaces(etree)
except ImportError:
    try:
        # Python 2.5 with ElementTree included
        import xml.etree.ElementTree as etree
        patch_well_known_namespaces(etree)
    except ImportError:
        try:
            # Python < 2.5 with ElementTree installed
            import elementtree.ElementTree as etree
            patch_well_known_namespaces(etree)
        except ImportError:
            raise RuntimeError('You need either lxml or ElementTree to use OWSLib!')
