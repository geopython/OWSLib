# ==============================================================================
#  Copyright (c) 2024 Ian Patterson
#
#  Author: Ian Patterson <ian@botts-inc.com>
#
#  Contact email: ian@botts-inc.com
# ==============================================================================

from owslib.ogcapi import Collections
from owslib.util import Authentication


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
