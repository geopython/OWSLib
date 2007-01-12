# =============================================================================
# OWSLib. Copyright (C) 2005 Sean C. Gillies
#
# Contact email: sgillies@frii.com
# =============================================================================

# try to find elementtree or lxml
try:
    import elementtree.ElementTree as etree
    # Monkey Patch adds to the default well known namespaces
    etree._namespace_map.update({
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#":  "rdf", 
        "http://purl.org/rss/1.0/":                     "rss", 
        "http://purl.org/rss/1.0/modules/taxonomy/":    "taxo", 
        "http://purl.org/dc/elements/1.1/":             "dc", 
        "http://purl.org/rss/1.0/modules/syndication/": "syn", 
        "http://www.w3.org/2003/01/geo/wgs84_pos#":     "geo"})
except ImportError:
    from lxml import etree

