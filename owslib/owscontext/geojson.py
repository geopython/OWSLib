# -*- coding: utf-8 -*-
# =============================================================================
# Authors : Alexander Kmoch <allixender@gmail.com>
#
# =============================================================================

"""
API for OGC Web Services Context Document (OWS Context) format.

GeoJson Encoding: http://www.opengeospatial.org/standards/owc

OGC OWS Context GeoJSON Encoding Standard 1.0 (14-055r2)
"""

from __future__ import (absolute_import, division, print_function)

import json
from datetime import datetime

# from owslib.util import log

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
    # log.debug("skip_nulls_rec(dict_obj): %r.", dict_obj)
    if not isinstance(dict_obj, dict):
        return dict_obj
    else:
        result = {}
        for k, v in dict_obj.items():
            # if k == "date":
            #     ts = datetime.now().timestamp()
            #     log.debug("%s k: %s v: %s.", ts, k, v)
            if v is None:
                pass
            else:
                if isinstance(v, dict):
                    tmp = skip_nulls_rec(v)
                    result.update({k: tmp})
                elif isinstance(v, list):
                    # log.debug("test isinstance(v, list): %r.", v)
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
    keys = path.split('.')
    tmp_iter = dict_obj
    for key in keys:
        try:
            # dict.get() might make KeyError exception unnecessary
            tmp_iter = tmp_iter.get(key, default)
            if key == "date":
                ts = datetime.now().timestamp()
                # log.debug("%s k: %s v: %s.", ts, key, tmp_iter)
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


class DateTimeEncoder(json.JSONEncoder):
    """
    https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable/36142844#36142844

    usage: json.dumps(yourobj, cls=DateTimeEncoder)
    """

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat() + "Z"

        return json.JSONEncoder.default(self, o)


def decode_json(jsondata):
    """
    TODO do we need to make sure everything is UTF-8?
    here parse json to an instance of OWC:Context

    :param jsondata:
    :return: dict
    """
    return json.loads(jsondata, object_hook=skip_nulls)


def encode_json(obj):
    """
    TODO do we need to make sure everything is UTF-8?
    eg. ensure_ascii=False, encoding='utf8) .encode('utf8') ?
    encode instance of OWCContext/or subclass into GeoJson encoding

    :param obj:
    :return: JSON
    """
    jsdata = json.dumps(skip_nulls_rec(obj), cls=DateTimeEncoder)

    return jsdata
