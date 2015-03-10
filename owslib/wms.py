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

"""

from __future__ import (absolute_import, division, print_function)

from .map import wms111, wms130


def WebMapService(url, version='1.1.1', xml=None, parse_remote_metadata=False,
                  timeout=30):
    '''wms factory function, returns a version specific WebMapService object)

    @type url: string
    @param url: url of WMS capabilities document
    @type xml: string
    @param xml: elementtree object
    @type parse_remote_metadata: boolean
    @param parse_remote_metadata: whether to fully process MetadataURL elements
    @return: initialized WebMapService_x_x_x object
    '''
    if version in ['1.1.1']:
        return wms111.WebMapService_1_1_1(url, version=version, xml=xml,
                                          parse_remote_metadata=parse_remote_metadata)
    elif version in ['1.3.0']:
        return wms130.WebMapService_1_3_0(url, version=version, xml=xml,
                                          parse_remote_metadata=parse_remote_metadata)
