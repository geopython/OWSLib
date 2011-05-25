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
            "http://www.w3.org/2003/01/geo/wgs84_pos#":     "geo",
            "http://www.opengis.net/cat/csw/2.0.2":         "csw",
            "http://purl.org/dc/terms/":                    "dct",
            "http://www.isotc211.org/2005/gco":             "gco",
            "http://www.isotc211.org/2005/gmd":             "gmd",
            "http://www.isotc211.org/2005/gts":             "gts",
            "http://www.isotc211.org/2005/srv":             "srv",
            "http://www.fgdc.gov":                          "fgdc",
            "http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/":   "dif",
            "http://www.opengis.net/gml":                   "gml",
            "http://www.opengis.net/ogc":                   "ogc",
            "http://www.opengis.net/ows":                   "ows",
            "http://www.opengis.net/ows/1.1":               "ows",
            "http://www.opengis.net/ows/2.0":               "ows",
            "http://www.opengis.net/wms":                   "wms",
            "http://www.opengis.net/context":               "wmc",
            "http://www.opengis.net/wfs":                   "wfs",
            "http://www.opengis.net/sos/1.0":               "sos",
            "urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0":  "rim",
            "http://www.w3.org/2001/XMLSchema":             "xs",
            "http://www.w3.org/XML/Schema":                 "xs2",
            "http://www.w3.org/2001/XMLSchema-instance":    "xsi",
            "http://www.w3.org/1999/xlink":                 "xlink"})

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

