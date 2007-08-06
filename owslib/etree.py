# =============================================================================
# OWSLib. Copyright (C) 2005 Sean C. Gillies
#
# Contact email: sgillies@frii.com
# =============================================================================

def patch_well_known_namespaces(etree_module):
    """Monkey patches the etree module to add some well-known namespaces."""
    etree_module._namespace_map.update({
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#":  "rdf", 
            "http://purl.org/rss/1.0/":                     "rss", 
            "http://purl.org/rss/1.0/modules/taxonomy/":    "taxo", 
            "http://purl.org/dc/elements/1.1/":             "dc", 
            "http://purl.org/rss/1.0/modules/syndication/": "syn", 
            "http://www.w3.org/2003/01/geo/wgs84_pos#":     "geo"})
    

# try to find elementtree or lxml
try:
    # Python < 2.5 with ElementTree installed
    import elementtree.ElementTree as etree
    patch_well_known_namespaces(etree)
except ImportError:
    try:
        # Python 2.5 with ElementTree included
        import xml.etree.ElementTree as etree
        patch_well_known_namespaces(etree)
    except ImportError:
        try:
            from lxml import etree
        except ImportError:
            raise RuntimeError('You need either ElementTree or lxml to use OWSLib!')

