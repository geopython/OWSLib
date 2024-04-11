# ==============================================================================
#  Copyright (c) 2024 Ian Patterson
#
#  Author: Ian Patterson <ian@botts-inc.com>
#
#  Contact email: ian@botts-inc.com
# ==============================================================================

import logging

from owslib import __version__
from owslib.ogcapi import Collections
from owslib.util import (Authentication)

LOGGER = logging.getLogger(__name__)

REQUEST_HEADERS = {
    'User-Agent': f'OWSLib {__version__} (https://owslib.readthedocs.io)'
}


class QueryParams:

    @staticmethod
    def check_for_params(**kwargs) -> dict:
        """
        checks for query parameters in kwargs passed from some API parent method
        @type id: string
        @param id: identifier of the resource
        @type bbox: list
        @param bbox: list of minx, miny, maxx, maxy
        @type datetime_: string
        @param datetime_: time extent or time instant
        @type geom: string
        @param geom: WKT representation of geometry
        @type q: list
        @param q: free text query strings, comma separated
        @type parent: list
        @param parent: local IDs or unique IDs, only returns resources the have a parent resource with an identifier in the list
        @type foi: list
        @param foi: local IDs or unique IDs, only returns resources that are associated with a feature of interest with an identifier in the list
        @type observedProperty: list
        @param observedProperty: local IDs or unique IDs, only returns resources that are associated with an observed property with an identifier in the list
        @type controlledProperty: list
        @param controlledProperty: local IDs or unique IDs, only returns resources that are associated with a controlled property with an identifier in the list
        @type recursive: boolean
        @param recursive: default false, if true, instructs server to include subsystems in the response
        @type limit: integer
        @param limit: default 10, maximum number of resources presented in the response
        @type system: list
        @param system: local IDs or unique IDs, only returns resources that are associated with a system with an identifier in the list

        @returns: 'string' of comma separated query parameters
        """

        if 'id' in kwargs:
            pass
        if 'bbox' in kwargs:
            kwargs['bbox'] = ','.join(list(map(str, kwargs['bbox'])))
        if 'datetime_' in kwargs:
            kwargs['datetime'] = kwargs['datetime']
        if 'geom' in kwargs:
            # TODO: make sure this serializes correctly
            pass
        if 'q' in kwargs:
            kwargs['q'] = ','.join(list(map(str, kwargs['q'])))
        if 'parent' in kwargs:
            kwargs['parent'] = ','.join(list(map(str, kwargs['parent'])))
        if 'foi' in kwargs:
            kwargs['foi'] = ','.join(list(map(str, kwargs['foi'])))
        if 'observedProperty' in kwargs:
            kwargs['observedProperty'] = ','.join(list(map(str, kwargs['observedProperty'])))
        if 'controlledProperty' in kwargs:
            kwargs['controlledProperty'] = ','.join(list(map(str, kwargs['controlledProperty'])))
        if 'recursive' in kwargs:
            pass
        if 'limit' in kwargs:
            pass
        if 'system' in kwargs:
            kwargs['system'] = ','.join(list(map(str, kwargs['system'])))
        return kwargs



