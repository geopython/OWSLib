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
Web Feature Server (WFS) methods and metadata. Factory function.
"""

from feature import wfs100, wfs200 
def WebFeatureService(url, version='1.0.0', xml=None):
    ''' wfs factory function, returns a version specific WebFeatureService object '''
    if version in  ['1.0', '1.0.0']:
        return wfs100.WebFeatureService_1_0_0.__new__(wfs100.WebFeatureService_1_0_0, url, version, xml)
    elif version in ['2.0', '2.0.0']:
        return wfs200.WebFeatureService_2_0_0.__new__(wfs200.WebFeatureService_2_0_0, url,  version, xml)

