# =============================================================================
# Copyright (c) 2020 Tom Kralidis
#
# Author: Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

import logging

from owslib.ogcapi import API
from owslib.util import Authentication

LOGGER = logging.getLogger(__name__)


class Features(API):
    """Abstraction for OGC API - Features"""

    def __init__(self, url: str, json_: str = None, timeout: int = 30,
                 headers: dict = None, auth: Authentication = None):
        __doc__ = API.__doc__  # noqa
        super().__init__(url, json_, timeout, headers, auth)

    def feature_collections(self) -> dict:
        """
        implements /collections filtered on features

        @returns: `dict` of filtered collections object
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
        @type datetime: string
        @param datetime: time extent or time instant
        @type limit: int
        @param limit: limit number of features
        @type startindex: int
        @param startindex: start position of results
        @type q: string
        @param q: full text search

        @returns: feature results
        """

        if 'bbox' in kwargs:
            kwargs['bbox'] = ','.join(kwargs['bbox'])

        path = 'collections/{}/items'.format(collection_id)
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

        path = 'collections/{}/items/{}'.format(collection_id, identifier)
        return self._request(path=path)
