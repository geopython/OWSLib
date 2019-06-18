# =============================================================================
# Copyright (c) 2018 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

import json
import logging

from six.moves.urllib.parse import urljoin

from owslib import __version__
from owslib.util import Authentication, http_get

LOGGER = logging.getLogger(__name__)

REQUEST_HEADERS = {
    'User-Agent': 'OWSLib {} (https://geopython.github.io/OWSLib)'.format(
        __version__)
}


class WebFeatureService_3_0_0(object):
    """Abstraction for OGC Web Feature Service (WFS) version 3.0"""
    def __init__(self, url, version, json_, timeout=30, username=None,
                 password=None, auth=None):
        """
        initializer; implements Requirement 1 (/req/core/root-op)

        @type url: string
        @param url: url of WFS root document
        @type json_: string
        @param json_: json object
        @param timeout: time (in seconds) after which requests should timeout
        @param username: service authentication username
        @param password: service authentication password
        @param auth: instance of owslib.util.Authentication

        @return: initialized WebFeatureService_3_0_0 object
        """

        if '?' in url:
            self.url, self.url_query_string = url.split('?')
        else:
            self.url = url.rstrip('/') + '/'
            self.url_query_string = None

        self.version = version
        self.json_ = json_
        self.timeout = timeout
        if auth:
            if username:
                auth.username = username
            if password:
                auth.password = password
        self.auth = auth or Authentication(username, password)

        if json_ is not None:  # static JSON string
            self.links = json.loads(json_)['links']
        else:
            response = http_get(url, headers=REQUEST_HEADERS, auth=self.auth).json()
            self.links = response['links']

    def api(self):
        """
        implements Requirement 3 (/req/core/api-definition-op)

        @returns: OpenAPI definition object
        """

        url = self._build_url('api')
        LOGGER.debug('Request: {}'.format(url))
        response = http_get(url, headers=REQUEST_HEADERS, auth=self.auth).json()
        return response

    def conformance(self):
        """
        implements Requirement 5 (/req/core/conformance-op)

        @returns: conformance object
        """

        url = self._build_url('conformance')
        LOGGER.debug('Request: {}'.format(url))
        response = http_get(url, headers=REQUEST_HEADERS, auth=self.auth).json()
        return response

    def collections(self):
        """
        implements Requirement 9 (/req/core/collections-op)

        @returns: collections object
        """

        url = self._build_url('collections')
        LOGGER.debug('Request: {}'.format(url))
        response = http_get(url, headers=REQUEST_HEADERS, auth=self.auth).json()
        return response['collections']

    def collection(self, collection_name):
        """
        implements Requirement 15 (/req/core/sfc-md-op)

        @type collection_name: string
        @param collection_name: name of collection

        @returns: feature collection metadata
        """

        path = 'collections/{}'.format(collection_name)
        url = self._build_url(path)
        LOGGER.debug('Request: {}'.format(url))
        response = http_get(url, headers=REQUEST_HEADERS, auth=self.auth).json()
        return response

    def collection_items(self, collection_name, **kwargs):
        """
        implements Requirement 17 (/req/core/fc-op)

        @type collection_name: string
        @param collection_name: name of collection
        @type bbox: list
        @param bbox: list of minx,miny,maxx,maxy
        @type time: string
        @param time: time extent or time instant
        @type limit: int
        @param limit: limit number of features
        @type startindex: int
        @param startindex: start position of results

        @returns: feature results
        """

        if 'bbox' in kwargs:
            kwargs['bbox'] = ','.join(kwargs['bbox'])

        path = 'collections/{}/items'.format(collection_name)
        url = self._build_url(path)
        LOGGER.debug('Request: {}'.format(url))
        response = http_get(url, headers=REQUEST_HEADERS, params=kwargs, auth=self.auth).json()
        return response

    def collection_item(self, collection_name, identifier):
        """
        implements Requirement 30 (/req/core/f-op)

        @type collection_name: string
        @param collection_name: name of collection
        @type identifier: string
        @param identifier: feature identifier

        @returns: single feature result
        """

        path = 'collections/{}/items/{}'.format(collection_name, identifier)
        url = self._build_url(path)
        LOGGER.debug('Request: {}'.format(url))
        response = http_get(url, headers=REQUEST_HEADERS, auth=self.auth).json()
        return response

    def _build_url(self, path=None):
        """
        helper function to build a WFS 3.0 URL

        @type path: string
        @param path: path of WFS URL

        @returns: fully constructed URL path
        """

        url = self.url
        if self.url_query_string is not None:
            LOGGER.debug('base URL has a query string')
            url = urljoin(url, path)
            url = '?'.join([url, self.url_query_string])
        else:
            url = urljoin(url, path)

        LOGGER.debug('URL: {}'.format(url))
        return url
