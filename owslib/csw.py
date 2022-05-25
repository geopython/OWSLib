# =============================================================================
# Copyright (c) 2021 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

"""
API for Catalogue Service for the Web (CSW) methods and metadata.

Supports version 2.0.2 and 3.0.0 of the CSW specification.
"""

from .catalogue import csw2, csw3
from .catalogue.csw2 import CswRecord
from .util import clean_ows_url, Authentication


def CatalogueServiceWeb(url, lang='en-US', version='2.0.2', timeout=10, skip_caps=False,
                        username=None, password=None, auth=None, headers=None):
    """
    CSW factory function, returns a version specific CatalogueServiceWeb object

    @type url: string
    @paramurl: the URL of the CSW
    @type lang: string
    @param lang: the language (default is 'en-US')
    @type version: string
    @param version: version (default is '2.0.2')
    @type timeout: string
    @param timeout: timeout in seconds
    @type skip_caps: string
    @param skip_caps: whether to skip GetCapabilities processing on
                      init (default is False)
    @type username: string
    @param username: username for HTTP basic authentication
    @type password: string
    @param password: password for HTTP basic authentication
    @type auth: string
    @param auth: instance of owslib.util.Authentication
    @type headers: dict
    @param headers: HTTP headers to send with requests

    @return: initialized CatalogueServiceWeb object
    """

    if auth:
        if username:
            auth.username = username
        if password:
            auth.password = password
    else:
        auth = Authentication(username, password)

    clean_url = clean_ows_url(url)

    if version == '2.0.2':
        return csw2.CatalogueServiceWeb(
            clean_url, lang=lang, version=version, timeout=timeout,
            skip_caps=skip_caps, username=username, password=password,
            auth=auth, headers=headers)
    if version == '3.0.0':
        return csw3.CatalogueServiceWeb(
            clean_url, lang=lang, version=version, timeout=timeout,
            skip_caps=skip_caps, username=username, password=password,
            auth=auth, headers=headers)

    raise NotImplementedError('The CSW version ({}) you requested is'
                              ' not implemented. Please use 2.0.2 or'
                              ' 3.0.0'.format(version))
