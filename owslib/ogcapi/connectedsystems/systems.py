# ==============================================================================
#  Copyright (c) 2024 Ian Patterson
#
#  Author: Ian Patterson <ian@botts-inc.com>
#
#  Contact email: ian@botts-inc.com
# ==============================================================================

import logging

from owslib.ogcapi import Collections
from owslib.util import Authentication

LOGGER = logging.getLogger(__name__)


# TODO: add query kwargs to all methods
# TODO: perform checks against schema or add extra argument to account for the valid types
# TODO: create tests
# TODO: improve docstrings
# TODO: may need to deactivate som collections features if CSAPI doesn't align totally with Common
class Systems(Collections):
    """Abstraction for OGC API - Connected Systems - Systems"""

    def __init__(self, url: str, json_: str = None, timeout: int = 30,
                 headers: dict = None, auth: Authentication = None):
        __doc__ = Collections.__doc__  # noqa
        super().__init__(url, json_, timeout, headers, auth)

    def system_collections(self) -> list:
        """
        implements /collections filtered on systems

        @returns: `list` of filtered collections object
        """

        systems_ = []
        collections_ = super().collections()

        for c_ in collections_['collections']:
            if 'itemType' in c_ and c_['itemType'].lower() == 'system':
                systems_.append(c_['id'])

        return systems_

    def collection_queryables(self, collection_id: str) -> dict:
        """
        implements /collections/{collectionId}/queryables

        @type collection_id: string
        @param collection_id: id of collection

        @returns: `dict` of system collection queryables
        """

        path = f'collections/{collection_id}/queryables'
        return self._request(path=path)

    def collection_items(self, collection_id: str, **kwargs: dict) -> dict:
        """
        implements /collection/{collectionId}/items

        @type collection_id: string
        @param collection_id: id of collection

        @returns: system collection results
        """

        path = f'collections/{collection_id}/items'
        return self._request(path=path, **kwargs)

    def collection_item(self, collection_id: str, item_id: str) -> dict:
        """
        implements /collection/{collectionId}/items/{itemId}

        @type collection_id: string
        @param collection_id: id of collection
        @type item_id: string
        @param item_id: id of item

        @returns: system collection item result
        """

        path = f'collections/{collection_id}/items/{item_id}'
        return self._request(path=path)

    def collection_item_create(self, collection_id: str, data: str) -> dict:
        """
        implements POST /collection/{collectionId}/items

        @type collection_id: string
        @param collection_id: id of collection
        @type data: string
        @param data: raw representation of data

        @returns: single item result
        """

        path = f'collections/{collection_id}/items'
        return self._request(method='POST', path=path, data=data)

    def systems(self) -> dict:
        """
        implements /systems

        @returns: `dict` of systems object
        """

        path = 'systems'
        return self._request(path=path)

    def system(self, system_id: str) -> dict:
        """
        implements /systems/{systemId}

        @type system_id: string
        @param system_id: id of system

        @returns: `dict` of system metadata
        """

        path = f'systems/{system_id}'
        return self._request(path=path)

    def system_create(self, system_id: str, data: str) -> dict:
        """
        implements /systems/{systemId}

        @type system_id: string
        @param system_id: id of system
        @type data: string
        @param data: system data

        @returns: `dict` of system metadata
        """

        path = f'systems/{system_id}'
        return self._request(path=path, method='POST', data=data)

    def system_update(self, system_id: str, data: str) -> dict:
        """
        implements /systems/{systemId}

        @type system_id: string
        @param system_id: id of system
        @type data: string
        @param data: system data

        @returns: `dict` of system metadata
        """

        path = f'systems/{system_id}'
        return self._request(path=path, method='PUT', data=data)

    def system_delete(self, system_id: str) -> bool:
        """
        implements /systems/{systemId}

        @type system_id: string
        @param system_id: id of system

        @returns: `bool` of deletion result
        """

        path = f'systems/{system_id}'
        return self._request(path=path, method='DELETE')

    def system_components(self, system_id: str) -> dict:
        """
        implements /systems/{systemId}/components

        @type system_id: string
        @param system_id: id of system

        @returns: `dict` of system components
        """

        path = f'systems/{system_id}/components'
        return self._request(path=path)

    def system_components_create(self, system_id: str, data: str) -> dict:
        """
        implements POST /systems/{systemId}/components

        @type system_id: string
        @param system_id: id of system
        @type data: string
        @param data: raw representation of data

        @returns: single component result
        """

        path = f'systems/{system_id}/components'
        return self._request(method='POST', path=path, data=data)

    def system_deployments(self, system_id: str) -> dict:
        """
        implements /systems/{systemId}/deployments

        @type system_id: string
        @param system_id: id of system

        @returns: `dict` of system deployments
        """

        path = f'systems/{system_id}/deployments'
        return self._request(path=path)

    def system_sampling_features(self, system_id: str) -> dict:
        """
        implements /systems/{systemId}/samplingFeatures

        @type system_id: string
        @param system_id: id of system

        @returns: `dict` of system sampling features
        """

        path = f'systems/{system_id}/samplingFeatures'
        return self._request(path=path)
