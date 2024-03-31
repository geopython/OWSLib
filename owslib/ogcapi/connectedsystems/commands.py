# ==============================================================================
#  Copyright (c) 2024 Ian Patterson
#
#  Author: Ian Patterson <ian@botts-inc.com>
#
#  Contact email: ian@botts-inc.com
# ==============================================================================
from owslib.ogcapi import Collections
from owslib.util import Authentication


class Commands(Collections):

    def __init__(self, url: str, json_: str = None, timeout: int = 30, headers: dict = None,
                 auth: Authentication = None):
        __doc__ = Collections.__doc__
        super().__init__(url, json_, timeout, headers, auth)

    def commands(self) -> dict:
        """
        implements /commands
        @returns: `dict` of commands object
        """

        path = 'commands'
        return self._request(path=path)

    def command(self, command_id: str) -> dict:
        """
        implements /commands/{commandId}
        @type command_id: string
        @param command_id: id of command
        @returns: `dict` of command metadata
        """

        path = f'commands/{command_id}'
        return self._request(path=path)

    def commands_of_control_channel(self, control_id: str) -> dict:
        """
        implements /controls/{control_id}/commands
        @type control_id: string
        @param control_id: id of control channel
        @returns: `dict` of commands object
        """

        path = f'controls/{control_id}/commands'
        return self._request(path=path)

    def commands_send_command_in_control_stream(self, control_id: str, data: str) -> dict:
        """
        implements /commands
        @type control_id: string
        @param control_id: id of control channel
        @type data: dict
        @param data: JSON object
        @returns: `dict` of command metadata
        """

        path = f'controls/{control_id}/commands'
        return self._request(path=path, data=data, method='POST')

    def commands_delete_command(self, command_id: str) -> dict:
        """
        implements /commands/{commandId}
        @type command_id: string
        @param command_id: id of command
        @returns: `dict` of command metadata
        """

        path = f'commands/{command_id}'
        return self._request(path=path, method='DELETE')

    def commands_add_status_report(self, command_id: str, data: str) -> dict:
        """
        implements /commands/{commandId}/status
        @type command_id: string
        @param command_id: id of command
        @type data: dict
        @param data: JSON object
        @returns: `dict` of command metadata
        """

        path = f'commands/{command_id}/status'
        return self._request(path=path, data=data, method='POST')

    def commands_retrieve_status_report(self, command_id: str, status_id: str) -> dict:
        """
        implements /commands/{commandId}/status/{statusId}
        @type command_id: string
        @param command_id: id of command
        @type status_id: string
        @param status_id: id of status
        @returns: `dict` of command metadata
        """

        path = f'commands/{command_id}/status/{status_id}'
        return self._request(path=path)

    def commands_update_status_report(self, command_id: str, status_id: str, data: str) -> dict:
        """
        implements /commands/{commandId}/status/{statusId}
        @type command_id: string
        @param command_id: id of command
        @type status_id: string
        @param status_id: id of status
        @type data: dict
        @param data: JSON object
        @returns: `dict` of command metadata
        """

        path = f'commands/{command_id}/status/{status_id}'
        return self._request(path=path, data=data, method='PUT')

    def commands_delete_status_report(self, command_id: str, status_id: str) -> dict:
        """
        implements /commands/{commandId}/status/{statusId}
        @type command_id: string
        @param command_id: id of command
        @type status_id: string
        @param status_id: id of status
        @returns: `dict` of command metadata
        """

        path = f'commands/{command_id}/status/{status_id}'
        return self._request(path=path, method='DELETE')
