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

import requests
import yaml

from owslib import __version__
from owslib.util import Authentication, http_get

LOGGER = logging.getLogger(__name__)

REQUEST_HEADERS = {
    'User-Agent': 'OWSLib {} (https://geopython.github.io/OWSLib)'.format(__version__)
}


class API(object):
    """Abstraction for OGC API - Common version 1.0"""

    def __init__(self, url: str, json_: str = None, timeout: int = 30,
                 headers: dict = None, auth: Authentication = None):
        """
        Initializer; implements /

        @type url: string
        @param url: url of OGC API landing page document
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
            self.headers.update(headers)
        self.auth = auth

        if json_ is not None:  # static JSON string
            self.links = json.loads(json_)['links']
        else:
            response = http_get(url, headers=self.headers, auth=self.auth).json()
            self.links = response['links']

    def api(self) -> dict:
        """
        implements /api

        @returns: `dict` of OpenAPI definition object
        """

        url = None
        openapi_format = None

        openapi_json_mimetype = 'application/vnd.oai.openapi+json;version=3.0'
        openapi_yaml_mimetype = 'application/vnd.oai.openapi;version=3.0'

        LOGGER.debug('Searching for OpenAPI JSON Document')
        for link in self.links:
            if link['rel'] == 'service-desc' and link['type'] == openapi_json_mimetype:
                openapi_format = openapi_json_mimetype
                url = link['href']
                break

            LOGGER.debug('Searching for OpenAPI YAML Document')
            if url is None:
                if link['rel'] == 'service-desc' and link['type'] == openapi_yaml_mimetype:
                    openapi_format = openapi_yaml_mimetype
                    url = link['href']
                    break

        if url is not None:
            LOGGER.debug('Request: {}'.format(url))
            response = http_get(url, headers=REQUEST_HEADERS, auth=self.auth)
            if openapi_format == openapi_json_mimetype:
                content = response.json()
            elif openapi_format == openapi_yaml_mimetype:
                content = yaml.load(response.text)
            return content
        else:
            msg = 'Did not find service-desc link'
            LOGGER.error(msg)
            raise RuntimeError(msg)

    def conformance(self) -> dict:
        """
        implements /conformance

        @returns: `dict` of conformance object
        """

        path = 'conformance'
        return self._request(path)

    def collections(self) -> dict:
        """
        implements /collections

        @returns: `dict` of collections object
        """

        path = 'collections'
        return self._request(path)

    def collection(self, collection_id: str) -> dict:
        """
        implements /collections/{collectionId}

        @type collection_id: string
        @param collection_id: id of collection

        @returns: `dict` of feature collection metadata
        """

        path = 'collections/{}'.format(collection_id)
        return self._request(path)

    def collection_queryables(self, collection_id: str) -> dict:
        """
        implements /collections/{collectionId}/queryables

        @type collection_id: string
        @param collection_id: id of collection

        @returns: `dict` of feature collection queryables
        """

        path = 'collections/{}/queryables'.format(collection_id)
        return self._request(path)

    def _build_url(self, path: str = None) -> str:
        """
        helper function to build an OGC API URL

        @type path: string
        @param path: path of OGC API URL

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

    def _request(self, path: str = None, as_dict: bool = True,
                 kwargs: dict = {}) -> dict:
        """
        helper function for request/response patterns against OGC API endpoints

        @type path: string
        @param path: path of request
        @type as_dict: bool
        @param as_dict: whether to return JSON dict (default True)
        @type kwargs: string
        @param kwargs: ``dict`` of keyword value pair request parameters

        @returns: response as JSON ``dict``
        """

        url = self._build_url(path)

        LOGGER.debug('Request: {}'.format(url))
        LOGGER.debug('Params: {}'.format(kwargs))

        response = http_get(url, headers=self.headers, auth=self.auth,
                            params=kwargs)

        LOGGER.debug('URL: {}'.format(response.url))

        if response.status_code != requests.codes.ok:
            raise RuntimeError(response.text)

        if as_dict:
            return response.json()
        else:
            return response.content
