# -*- coding: utf-8 -*-
# =============================================================================
# Authors : Alexander Kmoch <allixender@gmail.com>
#
# =============================================================================

"""
place for some constants to avoid circular imports
"""

# seen in wms.py
from six.moves.urllib.parse import urlparse

"""
The spec reference uri is of course difference for each encoding,
so holding it in the context container object is maybe a bit silly,
thus I use a generic spec reference and and only encode at serialisation time
"""

GENERIC_OWCSPEC_URL = "http://www.opengis.net/spec/owc-generic/1.0/req"
ATOM_OWCSPEC_URL = "http://www.opengis.net/spec/owc-atom/1.0/req"
GEOJSON_OWCSPEC_URL = "http://www.opengis.net/spec/owc-geojson/1.0/req"

"""
supported geojson profiles
"""

SUPPORTED_GEOJSON_PROFILES = [GEOJSON_OWCSPEC_URL + "/core"]

"""
those are for compliance testing when parsing geojson owc input
"""

SUPPORTED_GEOJSON_OFFERING_EXTENSIONS = [
    GEOJSON_OWCSPEC_URL + "/wms",
    GEOJSON_OWCSPEC_URL + "/wfs",
    GEOJSON_OWCSPEC_URL + "/wcs",
    GEOJSON_OWCSPEC_URL + "/wps",
    GEOJSON_OWCSPEC_URL + "/csw",
    GEOJSON_OWCSPEC_URL + "/geotiff",
    GEOJSON_OWCSPEC_URL + "/sos"
]


def encodedspecurl_to_genericspecurl(encodedspecurl, genericspecurl):
    parsed = urlparse(encodedspecurl)
    speccode = "/" + parsed.path.split("/").last.trim
    return genericspecurl + speccode


def genericspecurl_to_encodedspecurl(genericspecurl, encodedspecurl):
    parsed = urlparse(genericspecurl)
    speccode = parsed.path.split("/").last.trim
    return encodedspecurl + speccode
