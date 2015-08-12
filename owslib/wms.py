# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2004, 2006 Sean C. Gillies
# Copyright (c) 2009 STFC <http://www.stfc.ac.uk>
#
# Authors :
#          Dominic Lowe <dominic.lowe@stfc.ac.uk>
#
# Contact email: dominic.lowe@stfc.ac.uk
# =============================================================================

"""
Web Map Server (WFS) methods and metadata. Factory function.
"""

from __future__ import (absolute_import, division, print_function)

from owslib.map import wms111, wms130


def WebMapService(url, version='1.1.1', xml=None, parse_remote_metadata=False,
                  timeout=30):

    '''wms factory function, returns a version specific WebMapService object

    @type url: string
    @param url: url of WFS capabilities document
    @type xml: string
    @param xml: elementtree object
    @type parse_remote_metadata: boolean
    @param parse_remote_metadata: whether to fully process MetadataURL elements
    @param timeout: time (in seconds) after which requests should timeout
    @return: initialized WebFeatureService_2_0_0 object
    '''
    if version in ['1.1.1']:
        return wms111.WebMapService_1_1_1(url, version, xml, parse_remote_metadata,
                                          timeout=timeout)
    elif version in ['1.3.0']:
        return wms130.WebMapService_1_3_0(url, version, xml, parse_remote_metadata,
                                          timeout=timeout)
    raise NotImplementedError('The WMS version (%s) you requested is not implemented. Please use 1.1.1 or 1.3.0.' % version)
