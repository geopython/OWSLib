# =============================================================================
# Copyright (c) 2023 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

"""
API for A9 OpenSearch (description and query syntax).

https://github.com/dewitt/opensearch

Supports version 1.1 core as well as geo, time and parameters extensions.
"""

import logging
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from owslib.etree import etree
from owslib.owscontext.atom import decode_atomxml
from owslib.util import Authentication, http_get, nspath_eval, testXMLValue

LOGGER = logging.getLogger(__name__)

namespaces = {
    'os': 'http://a9.com/-/spec/opensearch/1.1/',
    'geo': 'http://a9.com/-/spec/opensearch/extensions/geo/1.0/',
    'parameters': 'http://a9.com/-/spec/opensearch/extensions/parameters/1.0/',  # noqa
    'time': 'http://a9.com/-/spec/opensearch/extensions/time/1.0/'
}


class OpenSearch(object):
    """ OpenSearch request class """
    def __init__(self, url, lang='en-US', version='1.1', timeout=10, xml=None,
                 username=None, password=None, auth=None, headers=None):
        """

        Initialize an OpenSearch client

        Parameters
        ----------

        - url: the URL of the OpenSearch endpoint
        - lang: the language (default is 'en-US')
        - version: version (default is '2.0.2')
        - timeout: timeout in seconds
        - xml: string of OpenSearch Description Document
        - username: username for HTTP basic authentication
        - password: password for HTTP basic authentication
        - auth: instance of owslib.util.Authentication
        - headers: HTTP headers to send with requests
        """

        if auth:
            if username:
                auth.username = username
            if password:
                auth.password = password

        self.url = url
        self.lang = lang
        self.version = version
        self.timeout = timeout
        self.auth = auth or Authentication(username, password)
        self.headers = headers

        if xml is not None:
            LOGGER.debug('Loading from XML stream')
            self._exml = etree.fromstring(xml)
        else:
            LOGGER.debug('Loading from URL')
            self.request = self.url
            response = http_get(self.request, timeout=self.timeout)
            self._exml = etree.fromstring(response.content)

        self.description = Description(self._exml)

    def search(self, type_: str, **kwargs) -> dict:
        """
        Invoke an OpenSearch search

        :param type_: media type of search
        :param kwargs: `dict` of key value pairs. When an OpenSearch
                       description document has URL Parameters, kwargs keys must
                       match accordingly.  When no OpenSearch URL Parameters
                       are defined, To pass kwargs keys which are OpenSearch
                       parameters such as `geo:time` or `eo:orbitNumber`, pass
                       the keys as `geo_time` or `eo_orbitNumber`.

        :returns: dict of response
        """

        if type_ not in self.description.urls.keys():
            msg = 'Invalid URL type'
            raise RuntimeError(msg)

        template = self.description.urls[type_]['template']

        if self.description.urls[type_]['parameters']:
            LOGGER.debug('Validating kwargs against defined parameters')
            for key, value in kwargs.items():
                if key not in self.description.urls[type_]['parameters']:
                    msg = f'parameter {key} not found'
                    LOGGER.debug(msg)
                    raise RuntimeError(msg)
                if 'options' in self.description.urls[type_]['parameters'][key]:
                    LOGGER.debug('Validating against parameter options')
                    if value not in self.description.urls[type_]['parameters'][key]['options']:
                        msg = f"{value} not in {self.description.urls[type_]['parameters'][key]['options']}"
                        LOGGER.debug(msg)
                        raise RuntimeError(msg)

                LOGGER.debug(f'Setting parameter {key} in URL template')

                template = template_replace_token(
                    template,
                    self.description.urls[type_]['parameters'][key]['value'],
                    value)

        else:
            LOGGER.debug('Best effort against no defined parameters')
            for key, value in kwargs.items():
                template = template_replace_token(
                    template,
                    key.replace('_', ':'),
                    value)

        response = http_get(prune_url(template), timeout=self.timeout)

        if 'json' in type_:
            LOGGER.debug('Returning dict of JSON response')
            response = response.json()
        elif 'atom' in type_:
            LOGGER.debug('Returning dict of Atom response')
            response = decode_atomxml(response.content)
        else:
            LOGGER.debug('Unknown/unsupported response, returning as is')

        return response


class Description:
    def __init__(self, md):

        self.urls = {}

        LOGGER.debug('Parsing Description')

        val = md.find(nspath_eval('os:ShortName', namespaces))
        self.shortname = testXMLValue(val)

        val = md.find(nspath_eval('os:LongName', namespaces))
        self.longname = testXMLValue(val)

        val = md.find(nspath_eval('os:Description', namespaces))
        self.description = testXMLValue(val)

        val = md.find(nspath_eval('os:Language', namespaces))
        self.language = testXMLValue(val)

        val = md.find(nspath_eval('os:InputEncoding', namespaces))
        self.inputencoding = testXMLValue(val)

        val = md.find(nspath_eval('os:OutputEncoding', namespaces))
        self.outputencoding = testXMLValue(val)

        val = md.find(nspath_eval('os:Tags', namespaces))
        self.tags = testXMLValue(val).split()

        val = md.find(nspath_eval('os:Contact', namespaces))
        self.contact = testXMLValue(val)

        val = md.find(nspath_eval('os:Developer', namespaces))
        self.developer = testXMLValue(val)

        val = md.find(nspath_eval('os:Attribution', namespaces))
        self.attribution = testXMLValue(val)

        val = md.find(nspath_eval('os:SyndicationRight', namespaces))
        self.syndicationright = testXMLValue(val)

        val = md.find(nspath_eval('os:AdultContent', namespaces))
        self.adultcontent = testXMLValue(val)

        for u in md.findall(nspath_eval('os:Url', namespaces)):
            url_type = u.attrib.get('type')

            url_def = {
                'rel': u.attrib.get('rel'),
                'template': u.attrib.get('template'),
                'parameters': {}
            }
            for p in u.findall(nspath_eval('parameters:Parameter', namespaces)):
                p_name = p.attrib.get('name')
                p_def = {
                    'pattern': p.attrib.get('pattern'),
                    'title': p.attrib.get('title'),
                    'value': p.attrib.get('value'),
                    'options': []
                }
                for o in p.findall(nspath_eval('parameters:Option', namespaces)):
                    p_def['options'].append(o.attrib.get('value'))

                url_def['parameters'][p_name] = p_def

            self.urls[url_type] = url_def


def template_replace_token(template: str, token: str, value: str) -> str:
    """
    Helper function to replace OpenSearch token in a URL template

    :param template: URL template
    :param token: token to replace
    :param value: value to replace token with

    :returns: updated URL template
    """

    token2 = token.replace('}', '?}')

    if token2 in template:
        LOGGER.debug('Replacing optional token')
        token_to_replace = token2
    else:
        LOGGER.debug('Replacing required token')
        token_to_replace = token

    LOGGER.debug(f'Token to replace: {token_to_replace}')

    LOGGER.debug(f'Template: {template}')
    template2 = template.replace(token_to_replace, value)
    LOGGER.debug(f'Template (replaced): {template2}')

    return template2


def prune_url(url: str) -> str:
    """
    Helper function to prune URL of unused template parameters

    https://stackoverflow.com/a/2506477

    :param url: URL

    :returns: updated URL without unused template parameters
    """

    query_params_out = {}

    url_parts = list(urlparse(url))

    query_params_in = dict(parse_qsl(url_parts[4]))

    for key, value in query_params_in.items():
        if '{' not in value and '}' not in value:
            query_params_out[key] = value

    url_parts[4] = urlencode(query_params_out)

    return urlunparse(url_parts)
