# ==============================================================================
#  Copyright (c) 2024 Ian Patterson
#
#  Author: Ian Patterson <ian@botts-inc.com>
#
#  Contact email: ian@botts-inc.com
# ==============================================================================
from owslib.ogcapi import Collections


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
