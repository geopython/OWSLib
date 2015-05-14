#!/usr/bin/python
# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2010 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

# get a list of entries for a given code list dictionary

from __future__ import absolute_import
from __future__ import print_function
import sys
import urllib2

from owslib.etree import etree
from owslib.iso import CodelistCatalogue

if len(sys.argv) < 3:
    print('Usage: %s <path/to/gmxCodelists.xml> <CodeListDictionary>' % sys.argv[0])
    sys.exit(1)

e=etree.parse(sys.argv[1])
c=CodelistCatalogue(e)

clds = c.getcodelistdictionaries()

def valid_clds():
    return  '''
Valid code list dictionaries are:

%s
''' % '\n'.join(clds)


if len(sys.argv) < 2:
    print('''
Usage: %s <codelistdictionary>
%s
''' % (sys.argv[0], valid_clds()))
    sys.exit(1)

cld = c.getcodedefinitionidentifiers(sys.argv[2])

if cld is None:
    print('''
Invalid code list dictionary: %s
%s
''' % (sys.argv[2],valid_clds()))
    sys.exit(2)

print('''

CodeListDictionary: %s

codeEntry's:

 %s

''' % (sys.argv[2],'\n '.join(cld)))
