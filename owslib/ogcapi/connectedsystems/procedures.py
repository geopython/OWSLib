# ==============================================================================
#  Copyright (c) 2024 Ian Patterson
#
#  Author: Ian Patterson <ian@botts-inc.com>
#
#  Contact email: ian@botts-inc.com
# ==============================================================================
from owslib.ogcapi import API
from owslib.util import Authentication


class Procedures(API):
    def __init__(self, url: str, json_: str = None, timeout: int = 30, headers: dict = None,
                 auth: Authentication = None):
        __doc__ = API.__doc__  # noqa
        super().__init__(url, json_, timeout, headers, auth)

    def procedures(self) -> dict:
        """
        implements /procedures
        @returns: `dict` of procedures object
        """

        path = 'procedures'
        return self._request(path=path)

    def procedure(self, procedure_id: str) -> dict:
        """
        implements /procedures/{procedureId}
        @type procedure_id: string
        @param procedure_id: id of procedure
        @returns: `dict` of procedure metadata
        """

        path = f'procedures/{procedure_id}'
        return self._request(path=path)

    def procedure_create(self, data: str) -> dict:
        """
        implements /procedures
        @type data: dict
        @param data: JSON object
        @returns: `dict` of procedure metadata
        """

        path = 'procedures'
        return self._request(path=path, data=data, method='POST')

    def procedure_update(self, procedure_id: str, data: str) -> dict:
        """
        implements /procedures/{procedureId}
        @type procedure_id: string
        @param procedure_id: id of procedure
        @type data: dict
        @param data: JSON object
        @returns: `dict` of procedure metadata
        """

        path = f'procedures/{procedure_id}'
        return self._request(path=path, data=data, method='PUT')

    def procedure_delete(self, procedure_id: str) -> dict:
        """
        implements /procedures/{procedureId}
        @type procedure_id: string
        @param procedure_id: id of procedure
        @returns: `dict` of procedure metadata
        """

        path = f'procedures/{procedure_id}'
        return self._request(path=path, method='DELETE')
