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


import urllib2
import etree
from coverage import wcs100, wcs110, wcsBase

def WebCoverageService(url, version=None, xml=None, opener=None, cookies=None, username=None, password=None):
    ''' wcs factory function, returns a version specific WebCoverageService object '''

    possibly_created_opener = None    
    if version is None:
        if xml is None:
            reader = wcsBase.WCSCapabilitiesReader(opener=opener, cookies=cookies, username=username, password=password, url_base=url) 
            possibly_created_opener = reader.opener 
            request = reader.capabilities_url(url)
            xml = reader.opener.open(request).read()
        capabilities = etree.etree.fromstring(xml)
        version = capabilities.get('version')
        del capabilities
        
    if version == '1.0.0':
        service_class = wcs100.WebCoverageService_1_0_0
        return wcs100.WebCoverageService_1_0_0.__new__(wcs100.WebCoverageService_1_0_0, url, xml, cookies)
    elif version == '1.1.0':
        service_class = wcs110.WebCoverageService_1_1_0 

    if possibly_created_opener is None: 
        return service_class.__new__(service_class, url, xml, opener, cookies, username, password) 
    else: 
        return service_class.__new__(service_class, url, xml, possibly_created_opener, None, None, None)
