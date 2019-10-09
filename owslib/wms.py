# -*- coding: iso-8859-15 -*-
# =============================================================================
# Copyright (c) 2004, 2006 Sean C. Gillies
# Copyright (c) 2005 Nuxeo SARL <http://nuxeo.com>
#
# Authors : Sean Gillies <sgillies@frii.com>
#           Julien Anguenot <ja@nuxeo.com>
#
# Contact email: sgillies@frii.com
# =============================================================================

"""
API for Web Map Service (WMS) methods and metadata.

Currently supports only version 1.1.1 of the WMS protocol.
"""

from .map import wms111, wms130
from .util import clean_ows_url, Authentication


def WebMapService(url, version='1.1.1', xml=None, username=None, password=None,
                  parse_remote_metadata=False, timeout=30, headers=None, auth=None):

    '''wms factory function, returns a version specific WebMapService object

    @type url: string
    @param url: url of WFS capabilities document
    @type xml: string
    @param xml: elementtree object
    @type parse_remote_metadata: boolean
    @param parse_remote_metadata: whether to fully process MetadataURL elements
    @param headers: HTTP headers to send with requests
    @param timeout: time (in seconds) after which requests should timeout
    @param username: service authentication username
    @param password: service authentication password
    @param auth: instance of owslib.util.Authentication
    @return: initialized WebFeatureService_2_0_0 object
    '''
    if auth:
        if username:
            auth.username = username
        if password:
            auth.password = password
    else:
        auth = Authentication(username, password)
    clean_url = clean_ows_url(url)

    if version in ['1.1.1']:
        return wms111.WebMapService_1_1_1(
            clean_url, version=version, xml=xml, parse_remote_metadata=parse_remote_metadata,
            timeout=timeout, headers=headers, auth=auth)
    elif version in ['1.3.0']:
        return wms130.WebMapService_1_3_0(
            clean_url, version=version, xml=xml, parse_remote_metadata=parse_remote_metadata,
            timeout=timeout, headers=headers, auth=auth)
    raise NotImplementedError(
        'The WMS version ({}) you requested is not implemented. Please use 1.1.1 or 1.3.0.'.format(version))
