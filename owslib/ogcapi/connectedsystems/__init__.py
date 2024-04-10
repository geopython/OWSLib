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


class SystemEvents(Collections):

    def __init__(self, url: str, json_: str = None, timeout: int = 30, headers: dict = None, ):
        __doc__ = Collections.__doc__
        super().__init__(url, json_, timeout, headers)

    def system_events(self) -> dict:
        """
        implements /systemEvents
        @returns: `dict` of system events object
        """

        path = 'systemEvents'
        return self._request(path=path)

    def system_events_of_specific_system(self, system_id: str) -> dict:
        """
        implements /systems/{systemId}/events
        @type system_id: string
        @param system_id: id of system
        @returns: `dict` of system events object
        """

        path = f'systems/{system_id}/events'
        return self._request(path=path)

    def system_event_add_se_to_system(self, system_id: str, data: str) -> dict:
        """
        implements /systems/{systemId}/events
        @type system_id: string
        @param system_id: id of system
        @type data: dict
        @param data: JSON object
        @returns: `dict` of system event metadata
        """

        path = f'systems/{system_id}/events'
        return self._request(path=path, data=data)

    def system_event(self, system_id: str, event_id: str) -> dict:
        """
        implements /systems/{systemId}/events/{event_id}
        @type system_id: string
        @param system_id: id of system
        @type event_id: string
        @param event_id: id of system event
        @returns: `dict` of system event metadata
        """

        path = f'systems/{system_id}/events/{event_id}'
        return self._request(path=path)

    def system_event_update(self, system_id: str, event_id: str, data: str) -> dict:
        """
        implements /systems/{systemId}/events/{event_id}
        @type system_id: string
        @param system_id: id of system
        @type event_id: string
        @param event_id: id of system event
        @type data: dict
        @param data: JSON object
        @returns: `dict` of system event metadata
        """

        path = f'systems/{system_id}/events/{event_id}'
        return self._request(path=path, data=data)

    def system_event_delete(self, system_id: str, event_id: str) -> dict:
        """
        implements /systems/{systemId}/events/{event_id}
        @type system_id: string
        @param system_id: id of system
        @type event_id: string
        @param event_id: id of system event
        @returns: `dict` of system event metadata
        """

        path = f'systems/{system_id}/events/{event_id}'
        return self._request(path=path, method='DELETE')


class SystemHistory(Collections):

    def __init__(self, url: str, json_: str = None, timeout: int = 30, headers: dict = None,
                 auth: Authentication = None):
        __doc__ = Collections.__doc__
        super().__init__(url, json_, timeout, headers, auth)

    def system_history(self, system_id: str) -> dict:
        """
        implements /systems/{system_id}/history
        @type system_id: string
        @param system_id: id of system
        @returns: `dict` of system history
        """

        path = f'systems/{system_id}/history'
        return self._request(path=path)

    def system_history_by_id(self, system_id: str, history_id: str) -> dict:
        """
        implements /systems/{system_id}/history/{history_id}
        @type system_id: string
        @param system_id: id of system
        @type history_id: string
        @param history_id: id of history
        @returns: `dict` of system history
        """

        path = f'systems/{system_id}/history/{history_id}'
        return self._request(path=path)

    def system_history_update_description(self, system_id: str, history_id: str, data: str) -> dict:
        """
        implements /systems/{system_id}/history/{history_id}
        @type system_id: string
        @param system_id: id of system
        @type history_id: string
        @param history_id: id of history
        @type data: dict
        @param data: JSON object
        @returns: `dict` of system history
        """

        path = f'systems/{system_id}/history/{history_id}'
        return self._request(path=path, data=data, method='PUT')

    def system_history_delete(self, system_id: str, history_id: str) -> dict:
        """
        implements /systems/{system_id}/history/{history_id}
        @type system_id: string
        @param system_id: id of system
        @type history_id: string
        @param history_id: id of history
        @returns: `dict` of system history
        """

        path = f'systems/{system_id}/history/{history_id}'
        return self._request(path=path, method='DELETE')
