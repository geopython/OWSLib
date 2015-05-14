#!/usr/bin/python
# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2010 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

# simple process to harvest CSW catalogues via Harvest operations

from __future__ import absolute_import
from __future__ import print_function
import sys
from owslib.csw import CatalogueServiceWeb

stop = 0
flag = 0
maxrecords = 10

if len(sys.argv) < 3:
    print('Usage: %s <source_catalogue_url> <destination_catalogue_url> [maxrecords]' \
        % sys.argv[0])
    sys.exit(1)

src = CatalogueServiceWeb(sys.argv[1])
dest = CatalogueServiceWeb(sys.argv[2])

if len(sys.argv) == 4:
    maxrecords = sys.argv[3]

while stop == 0:
    if flag == 0:  # first run, start from 0
        startposition = 0
    else:  # subsequent run, startposition is now paged
        startposition = src.results['nextrecord']

    src.getrecords(esn='brief', startposition=startposition, maxrecords=maxrecords)

    print(src.results)

    if src.results['nextrecord'] == 0 \
        or src.results['returned'] == 0 \
        or src.results['nextrecord'] > src.results['matches']:  # end the loop, exhausted all records
        stop = 1
        break

    # harvest each record to destination CSW
    for i in list(src.records):
        source = '%s?service=CSW&version=2.0.2&request=GetRecordById&id=%s' % \
            (sys.argv[1], i)
        dest.harvest(source=source, \
            resourcetype='http://www.isotc211.org/2005/gmd')
        #print dest.request
        #print dest.response

    flag = 1
