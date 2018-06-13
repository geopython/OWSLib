# -*- coding: utf-8 -*-
# =============================================================================
# Authors : Alexander Kmoch <allixender@gmail.com>
#
# =============================================================================

"""
place for some constants to avoid circular imports
"""

from __future__ import (absolute_import, division, print_function)

# seen in wms.py
from six.moves.urllib.parse import urlparse

from datetime import datetime
from dateutil import parser

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

# FIXME are the geosjson and atom offering codes ok,
# because ATOM offering codes are different (spec vs conf vs req)

ATOM_OFFERING_CODES = [
    'http://www.opengis.net/spec/owc/1.0/conf/atom/gml',
    'http://www.opengis.net/spec/owc/1.0/req/atom/wms'
    'http://www.opengis.net/spec/owc-atom/1.0/req/gml',
    'http://www.opengis.net/spec/owc-atom/1.0/req/csw',
]


def encodedspecurl_to_genericspecurl(encodedspecurl, genericspecurl):
    parsed = urlparse(encodedspecurl)
    speccode = "/" + parsed.path.split("/").last.trim
    return genericspecurl + speccode


def genericspecurl_to_encodedspecurl(genericspecurl, encodedspecurl):
    parsed = urlparse(genericspecurl)
    speccode = parsed.path.split("/").last.trim
    return encodedspecurl + speccode


class TimeIntervalFormat(object):
    """
    little helper to have time intervals
    """

    def __init__(self,
                 start,
                 end=None):
        """
        constructor:

        :param start: datetime
        :param end: datetime
        """
        self.start = start
        self.end = end

    def __str__(self):
        if self.end is None:
            return self.start.isoformat()
        else:
            return self.start.isoformat() + "/" + self.end.isoformat()

    def to_dict(self):
        """
        dict representation of object, for simple object comparison
        :return: dict
        """
        return {
            "start": None if self.start is None else self.start.isoformat(),
            "end": None if self.start is None else self.start.isoformat()
        }

    @classmethod
    def from_string(cls, date_str):
        if date_str is None:
            return None
        try:
            date_arr = date_str.split("/")
            if len(date_arr) > 1:
                start_dt = parser.parse(date_arr[0])
                end_dt = parser.parse(date_arr[1])
                return TimeIntervalFormat(start_dt, end_dt)
            else:
                single_dt = parser.parse(date_str)
                return TimeIntervalFormat(single_dt)
        except:
            raise ValueError("Error parsing datetime string: %s" % date_str)


def skip_nulls(dict_obj):
    """
    drops key/val pairs where js value is null, not needed in the JSON
    :param o: needs to be dict
    :return:
    """
    reduced = {k: v for k, v in dict_obj.items() if v is not None}
    return reduced


def skip_nulls_rec(dict_obj):
    """
    removes dict key/val pairs recursively where value is None,
    not needed/wanted(?) in the JSON
    :param o: needs to be dict
    :return: the trimed dict, or exceptionally the value if it wasn't a dict
    """
    if not isinstance(dict_obj, dict):
        return dict_obj
    else:
        result = {}
        for k, v in dict_obj.items():
            if v is None:
                pass
            else:
                if isinstance(v, dict):
                    tmp = skip_nulls_rec(v)
                    result.update({k: tmp})
                elif isinstance(v, list):
                    tmp = [skip_nulls_rec(o) for o in v]
                    result.update({k: tmp})
                else:
                    result.update({k: v})
        return result


def extract_p(path, dict_obj, default):
    """
    try to extract dict value in key path, if key error provide default
    :param path: the nested dict key path, separated by '.'
    (therefore no dots in key names allowed)
    :param dict_obj: the dictinary object from which to extract
    :param default: a default return value if key error
    :return: extracted value
    """
    if dict_obj is None:
        return default

    keys = path.split('.')
    tmp_iter = dict_obj
    for key in keys:
        try:
            # dict.get() might make KeyError exception unnecessary
            tmp_iter = tmp_iter.get(key, default)
        except KeyError:
            return default
    return tmp_iter


def build_from_xp(path, dict_obj, build_class, default):
    """
    try to build class instance from extracted path, else return default
    :param path: path: the nested dict key path, separated by '.'
    (therefore no dots in key names allowed)
    :param dict_obj: the dictinary object from which to extract
    :param build_class: the class name from which to build
    :param default: default return value
    :return: ideally the inquired class instance, else default
    """
    xp = extract_p(path, dict_obj, default)
    if xp is None:
        return default
    elif xp == default:
        return default
    else:
        return build_class.from_dict(xp)


def is_empty(dict_obj):
    """
    query if a dict is empty

    :param dict_obj: the to be tested dictionary
    :return: True, if it is empty, False if not empty
    """
    if isinstance(dict_obj, dict):
        if len(dict_obj.items()) <= 0:
            return True
        else:
            switch = True
            for k, v in dict_obj.items():
                if v is None:
                    pass
                else:
                    switch = False
            return switch
    else:
        return False


def try_int(num_string):
    """
    short hand cast to number

    :param num_string:
    :return: int or None
    """
    if num_string is not None:
        try:
            return int(num_string)
        except ValueError:
            pass
    return None


def try_float(num_string):
    """
    short hand cast to number

    :param num_string:
    :return: float or None
    """
    if num_string is not None:
        try:
            return float(num_string)
        except ValueError:
            pass
    return None
