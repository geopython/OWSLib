# =============================================================================
# Copyright (c) 2020 Tom Kralidis
#
# Author: Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

import json
import logging

from urllib.parse import urljoin

from owslib.ogcapi import API, REQUEST_HEADERS
from owslib.util import http_get

LOGGER = logging.getLogger(__name__)


class Features(API):
    """Abstraction for OGC API - Features"""

    def __init__(self, url, json_=None, timeout=30, headers=None, auth=None):
        __doc__ = API.__doc__  # noqa
        super().__init__(url, json_, timeout, headers, auth)

    def collection_items(self, collection_id, **kwargs):
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

        @returns: feature results
        """

        if 'bbox' in kwargs:
            kwargs['bbox'] = ','.join(kwargs['bbox'])

        path = 'collections/{}/items'.format(collection_id)
        url = self._build_url(path)
        LOGGER.debug('Request: {}'.format(url))
        response = http_get(
            url, headers=self.headers, params=kwargs, auth=self.auth
        ).json()
        return response

    def collection_item(self, collection_id, identifier):
        """
        implements /collections/{collectionId}/items/{featureId}

        @type collection_id: string
        @param collection_id: id of collection
        @type identifier: string
        @param identifier: feature identifier

        @returns: single feature result
        """

        path = 'collections/{}/items/{}'.format(collection_id, identifier)
        url = self._build_url(path)
        LOGGER.debug('Request: {}'.format(url))
        response = http_get(url, headers=self.headers, auth=self.auth).json()
        return response
