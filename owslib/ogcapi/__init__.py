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

from owslib import __version__
from owslib.util import http_get

LOGGER = logging.getLogger(__name__)

REQUEST_HEADERS = {
    'User-Agent': 'OWSLib {} (https://geopython.github.io/OWSLib)'.format(__version__)
}


class API(object):
    """Abstraction for OGC API Common version 1.0"""

    def __init__(self, url, json_=None, timeout=30, headers=None, auth=None):
        """
        Initializer; implements /

        @type url: string
        @param url: url of WFS root document
        @type json_: string
        @param json_: json object
        @param headers: HTTP headers to send with requests
        @param timeout: time (in seconds) after which requests should timeout
        @param username: service authentication username
        @param password: service authentication password
        @param auth: instance of owslib.util.Authentication

        @returns: `owslib.ogcapi.API`
        """

        if '?' in url:
            self.url, self.url_query_string = url.split('?')
        else:
            self.url = url.rstrip('/') + '/'
            self.url_query_string = None

        self.json_ = json_
        self.timeout = timeout
        self.headers = REQUEST_HEADERS
        if headers:
            self.headers = self.headers.update(headers)
        self.auth = auth

        if json_ is not None:  # static JSON string
            self.links = json.loads(json_)['links']
        else:
            response = http_get(url, headers=self.headers, auth=self.auth).json()
            self.links = response['links']

    def api(self):
        """
        implements /api

        @returns: `dict` of OpenAPI definition object
        """

        url = None

        for l in self.links:
            if l['rel'] == 'service-desc':
                url = l['href']

        if url is not None:
            LOGGER.debug('Request: {}'.format(url))
            response = http_get(url, headers=REQUEST_HEADERS, auth=self.auth).json()
            return response
        else:
            msg = 'Did not find service-desc link'
            LOGGER.error(msg)
            raise RuntimeError(msg)

    def conformance(self):
        """
        implements /conformance

        @returns: `dict` of conformance object
        """

        url = self._build_url('conformance')
        LOGGER.debug('Request: {}'.format(url))
        response = http_get(url, headers=self.headers, auth=self.auth).json()

        return response

    def collections(self):
        """
        implements /collections

        @returns: `dict` of collections object
        """

        url = self._build_url('collections')
        LOGGER.debug('Request: {}'.format(url))
        response = http_get(url, headers=self.headers, auth=self.auth).json()

        return response['collections']

    def collection(self, collection_id):
        """
        implements /collections/{collectionId}

        @type collection_id: string
        @param collection_id: id of collection

        @returns: `dict` of feature collection metadata
        """

        path = 'collections/{}'.format(collection_id)
        url = self._build_url(path)
        LOGGER.debug('Request: {}'.format(url))
        response = http_get(url, headers=self.headers, auth=self.auth).json()

        return response

    def _build_url(self, path=None):
        """
        helper function to build an OGC API URL

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
