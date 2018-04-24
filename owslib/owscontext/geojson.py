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


def skip_nulls(o):
    """
    removes dict key/val pairs where value is None, not needed in the JSON
    :param o:
    :return:
    """
    reduced = {k: v for k, v in o.items() if v is not None}
    return reduced


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
    here parse json to an instance of OWC:Context

    :param jsondata:
    :return: OWCContext
    """
    return json.loads(jsondata, object_hook=skip_nulls)


def encode_json(obj):
    """
    encode instance of OWCContext/or subclass into GeoJson encoding

    :param obj:
    :return: JSON
    """
    jsdata = json.dumps(vars(skip_nulls(obj)), cls=DateTimeEncoder)

    return jsdata
