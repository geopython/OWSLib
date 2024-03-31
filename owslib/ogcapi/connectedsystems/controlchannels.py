# ==============================================================================
#  Copyright (c) 2024 Ian Patterson
#
#  Author: Ian Patterson <ian@botts-inc.com>
#
#  Contact email: ian@botts-inc.com
# ==============================================================================
from owslib.ogcapi import Collections
from owslib.util import Authentication


class ControlChanels(Collections):

    def __init__(self, url: str, json_: str = None, timeout: int = 30, headers: dict = None,
                 auth: Authentication = None):
        __doc__ = Collections.__doc__
        super().__init__(url, json_, timeout, headers, auth)

    def controls(self) -> dict:
        """
        implements /controls
        @returns: `dict` of control channel objects
        """

        path = 'controls'
        return self._request(path=path)

    def control(self, control_id: str) -> dict:
        """
        implements /controls/{control_id}
        @type control_id: string
        @param control_id: id of control channel
        @returns: `dict` of control channels
        """

        path = f'controls/{control_id}'
        return self._request(path=path)

    def controls_of_system(self, system_id: str) -> dict:
        """
        implements /systems/{system_id}/controls
        @type system_id: string
        @param system_id: id of system
        @returns: `dict` of control channels
        """

        path = f'systems/{system_id}/controls'
        return self._request(path=path)

    def control_create_in_system(self, system_id: str, data: str) -> dict:
        """
        implements /controls
        @type system_id: string
        @param system_id: id of system
        @type data: dict
        @param data: JSON object
        @returns: `dict` of control channels
        """

        path = f'systems/{system_id}/controls'
        return self._request(path=path, data=data, method='POST')

    def control_update(self, control_id: str, data: str) -> dict:
        """
        implements /controls/{control_id}
        @type control_id: string
        @param control_id: id of control channel
        @type data: dict
        @param data: JSON object
        @returns: `dict` of control channels
        """

        path = f'controls/{control_id}'
        return self._request(path=path, data=data, method='PUT')

    def control_delete(self, control_id: str) -> dict:
        """
        implements /controls/{control_id}
        @type control_id: string
        @param control_id: id of control channel
        @returns: `dict` of control channels
        """

        path = f'controls/{control_id}'
        return self._request(path=path, method='DELETE')

    def control_retrieve_schema(self, control_id: str) -> dict:
        """
        implements /controls/{control_id}/schema
        @type control_id: string
        @param control_id: id of control channel
        @returns: `dict` of control channels
        """

        path = f'controls/{control_id}/schema'
        return self._request(path=path)

    def control_update_schema(self, control_id: str, data: str) -> dict:
        """
        implements /controls/{control_id}/schema
        @type control_id: string
        @param control_id: id of control channel
        @type data: dict
        @param data: JSON object
        @returns: `dict` of control channels
        """

        path = f'controls/{control_id}/schema'
        return self._request(path=path, data=data, method='PUT')
