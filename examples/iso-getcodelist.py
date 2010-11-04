#!/usr/bin/python
# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2010 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@hotmail.com>
#
# Contact email: tomkralidis@hotmail.com
# =============================================================================

# get a list of entries for a given code list dictionary

import sys
import urllib2

from owslib.etree import etree
from owslib.iso import CodelistCatalogue

e=etree.fromstring(urllib2.urlopen('http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml').read())
c=CodelistCatalogue(e)

clds = c.getcodelistdictionaries()

def valid_clds():
    return  '''
Valid code list dictionaries are:

%s
''' % '\n'.join(clds)


if len(sys.argv) < 2:
    print '''
Usage: %s <codelistdictionary>
%s
''' % (sys.argv[0], valid_clds())
    sys.exit(1)

cld = c.getcodedefinitionidentifiers(sys.argv[1])

if cld is None:
    print '''
Invalid code list dictionary: %s
%s
''' % (sys.argv[1],valid_clds())
    sys.exit(2)

print '''

CodeListDictionary: %s

codeEntry's:

 %s

''' % (sys.argv[1],'\n '.join(cld))
