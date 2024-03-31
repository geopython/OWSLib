# ==============================================================================
#  Copyright (c) 2024 Ian Patterson
#
#  Author: Ian Patterson <ian@botts-inc.com>
#
#  Contact email: ian@botts-inc.com
# ==============================================================================
from owslib.ogcapi import API
from owslib.util import Authentication


class Properties(API):

    def __init__(self, url: str, json_: str = None, timeout: int = 30, headers: dict = None,
                 auth: Authentication = None):
        __doc__ = API.__doc__
        super().__init__(url, json_, timeout, headers, auth)

    def properties(self) -> dict:
        """
        implements /properties
        @returns: `dict` of properties object
        """

        path = 'properties'
        return self._request(path=path)

    def property(self, property_id: str) -> dict:
        """
        implements /properties/{propertyId}
        @type property_id: string
        @param property_id: id of property
        @returns: `dict` of property metadata
        """

        path = f'properties/{property_id}'
        return self._request(path=path)

    def property_create(self, data: str) -> dict:
        """
        implements /properties
        @type data: dict
        @param data: JSON object
        @returns: `dict` of property metadata
        """

        path = 'properties'
        return self._request(path=path, data=data, method='POST')

    def property_update(self, property_id: str, data: str) -> dict:
        """
        implements /properties/{propertyId}
        @type property_id: string
        @param property_id: id of property
        @type data: dict
        @param data: JSON object
        @returns: `dict` of property metadata
        """

        path = f'properties/{property_id}'
        return self._request(path=path, data=data, method='PUT')

    def property_delete(self, property_id: str) -> dict:
        """
        implements /properties/{propertyId}
        @type property_id: string
        @param property_id: id of property
        @returns: `dict` of property metadata
        """

        path = f'properties/{property_id}'
        return self._request(path=path, method='DELETE')
