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

import json
from datetime import datetime
from owslib.owscontext.common import skip_nulls, skip_nulls_rec


# from owslib.util import log

class DateTimeEncoder(json.JSONEncoder):
    """
    https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable/36142844#36142844

    usage: json.dumps(yourobj, cls=DateTimeEncoder)
    """

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

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
