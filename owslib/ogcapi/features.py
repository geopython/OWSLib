# =============================================================================
# Copyright (c) 2022 Tom Kralidis
#
# Author: Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

from copy import deepcopy
import logging
from urllib.parse import urlencode

from owslib.ogcapi import Collections
from owslib.util import Authentication

LOGGER = logging.getLogger(__name__)


class Features(Collections):
    """Abstraction for OGC API - Features"""

    def __init__(self, url: str, json_: str = None, timeout: int = 30,
                 headers: dict = None, auth: Authentication = None):
        __doc__ = Collections.__doc__  # noqa
        super().__init__(url, json_, timeout, headers, auth)

    def feature_collections(self) -> list:
        """
        implements /collections filtered on features

        @returns: `list` of filtered collections object
        """

        features_ = []
        collections_ = super().collections()

        for c_ in collections_['collections']:
            if 'itemType' in c_ and c_['itemType'].lower() == 'feature':
                features_.append(c_['id'])

        return features_

    def collection_items(self, collection_id: str, **kwargs: dict) -> dict:
        """
        implements /collection/{collectionId}/items

        @type collection_id: string
        @param collection_id: id of collection
        @type bbox: list
        @param bbox: list of minx,miny,maxx,maxy
        @type datetime_: string
        @param datetime_: time extent or time instant
        @type limit: int
        @param limit: limit number of features
        @type offset: int
        @param offset: start position of results
        @type q: string
        @param q: full text search
        @type filter: string
        @param filter: CQL TEXT expression
        @type cql: dict
        @param cql: CQL JSON payload

        @returns: feature results
        """

        if 'bbox' in kwargs:
            kwargs['bbox'] = ','.join(list(map(str, kwargs['bbox'])))
        if 'datetime_' in kwargs:
            kwargs['datetime'] = kwargs['datetime_']

        if 'cql' in kwargs:
            LOGGER.debug('CQL query detected')
            kwargs2 = deepcopy(kwargs)
            cql = kwargs2.pop('cql')
            path = f'collections/{collection_id}/items?{urlencode(kwargs2)}'
            return self._request(method='POST', path=path, data=cql, kwargs=kwargs2)
        else:
            path = f'collections/{collection_id}/items'
            return self._request(path=path, kwargs=kwargs)

    def collection_item(self, collection_id: str, identifier: str) -> dict:
        """
        implements /collections/{collectionId}/items/{featureId}

        @type collection_id: string
        @param collection_id: id of collection
        @type identifier: string
        @param identifier: feature identifier

        @returns: single feature result
        """

        path = f'collections/{collection_id}/items/{identifier}'
        return self._request(path=path)

    def collection_item_create(self, collection_id: str, data: str) -> bool:
        """
        implements POST /collections/{collectionId}/items

        @type collection_id: string
        @param collection_id: id of collection
        @type data: string
        @param data: raw representation of data

        @returns: single feature result
        """

        path = f'collections/{collection_id}/items'

        if isinstance(data, dict):  # JSON
            LOGGER.debug('Detected JSON payload')
            self.headers['Content-Type'] = 'application/geo+json'
        elif data.startswith('<'):  # XML
            data = data.strip()
            LOGGER.debug('Detected XML payload')
            self.headers['Content-Type'] = 'application/xml'

        _ = self._request(method='POST', path=path, data=data)

        return True

    def collection_item_update(self, collection_id: str, identifier: str,
                               data: str) -> bool:
        """
        implements PUT /collections/{collectionId}/items/{featureId}

        @type collection_id: string
        @param collection_id: id of collection
        @type identifier: string
        @param identifier: feature identifier
        @type data: string
        @param data: raw representation of data

        @returns: ``bool`` of deletion result
        """

        path = f'collections/{collection_id}/items/{identifier}'
        _ = self._request(method='PUT', path=path, data=data)

        return True

    def collection_item_delete(self, collection_id: str, identifier: str) -> bool:
        """
        implements DELETE /collections/{collectionId}/items/{featureId}

        @type collection_id: string
        @param collection_id: id of collection
        @type identifier: string
        @param identifier: feature identifier

        @returns: ``bool`` of deletion result
        """

        path = f'collections/{collection_id}/items/{identifier}'
        _ = self._request(method='DELETE', path=path)

        return True
