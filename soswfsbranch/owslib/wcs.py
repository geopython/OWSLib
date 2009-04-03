# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2004, 2006 Sean C. Gillies
# Copyright (c) 2007 STFC <http://www.stfc.ac.uk>
#
# Authors : 
#          Dominic Lowe <d.lowe@rl.ac.uk>
#
# Contact email: d.lowe@rl.ac.uk
# =============================================================================

"""
Web Coverage Server (WCS) methods and metadata. Factory function.
"""

from coverage import wcs100, wcs110 
def WebCoverageService(url, version='1.1.0', xml=None):
    ''' wcs factory function, returns a version specific WebCoverageService object '''
    if version == '1.0.0':
        return wcs100.WebCoverageService_1_0_0.__new__(wcs100.WebCoverageService_1_0_0, url, xml)
    elif version == '1.1.0':
        return wcs110.WebCoverageService_1_1_0.__new__(wcs110.WebCoverageService_1_1_0,url, xml)