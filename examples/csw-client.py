#!/usr/bin/python
# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2009 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

from __future__ import absolute_import
from __future__ import print_function
import sys
import getopt

from owslib.csw import CatalogueServiceWeb

def usage():
    print("""
    %s [options]

Required Parameters
-------------------

    --url=[URL] the URL of the CSW
    --request=[REQUEST] the request (GetCapabilities, DescribeRecord, GetDomain, GetRecords, GetRecordById)

Optional Parameters
-------------------

    --lang=[LANG] the language of the CSW
    --version=[VERSION] the CSW server version
    --print-request print the request
    --validate perform XML validation against the request

Request Specific Parameters
---------------------------

DescribeRecord
    --typename=[TypeName] the typename to describe 

GetDomain
    --dname=[NAME] the domain to query
    --dtype=[property|parameter] the type of domain query

GetRecords
    --sortby=[dc:title|dct:abstract|ows:BoundingBox] sort by property
    --keyword=[KEYWORD] the keyword(s) to query
    --bbox=[BBOX] the bounding box to spatially query in the form of "minx miny maxx maxy"
    --esn=[brief|full|summary] verbosity of results
    --qtype=[dataset|service] query for data or services
    --schema=[iso] the outputSchema (default is csw)

GetRecordById
    --id=[ID] the ID of the record

""" % sys.argv[0])

# check args
if len(sys.argv) == 1:
    usage()
    sys.exit(1)

try:
    opts, args = getopt.getopt(sys.argv[1:], '', ['typename=', 'request=', 'lang=', 'version', 'keyword=', 'bbox=', 'schema=', 'qtype=', 'esn=', 'url=', 'print-request', 'sortby=', 'id=', 'dtype=', 'dname=', 'validate'])
except getopt.GetoptError as err:
    print(str(err))
    usage()
    sys.exit(2)

request = None
keyword = None
bbox = None
schema = None
qtype = None
esn = 'full'
url = None
print_request = False
validate = False
sortby = None
id = None
version = '2.0.2'
lang = 'en-US'
dname = None
dtype = None
typename = None

# set args
for o, a in opts:
    if o in '--request':
        request = a
    elif o in '--keyword':
        keyword = a
    elif o in '--bbox':
        bbox = a.split()
    elif o in '--typename':
        typename = a
    elif o in '--schema':
        schema = a
    elif o in '--qtype':
        qtype = a
    elif o in '--esn':
        esn = a
    elif o in '--url':
        url = a
    elif o in '--sortby':
        sortby = a
    elif o in '--id':
        id = a
    elif o in '--dname':
        dname = a
    elif o in '--dtype':
        dtype= a
    elif o in '--version':
        version = a
    elif o in '--lang':
        lang = a
    elif o in '--print-request':
        print_request = True
    elif o in '--validate':
        validate = True
    else:
        assert False, 'unhandled option'

if request is None or url is None:
    usage()
    sys.exit(3)

if schema == 'iso':
  outputschema = 'http://www.isotc211.org/2005/gmd'

# init
c = CatalogueServiceWeb(url, lang, version)

if request == 'GetCapabilities':
    pass
elif request == 'DescribeRecord':
    c.describerecord(typename)
elif request == 'GetRecordById':
    c.getrecordbyid([id])
elif request == 'GetDomain':
    c.getdomain(dname, dtype)
elif request == 'GetRecords':
    c.getrecords(qtype, [keyword], bbox, esn, sortby, schema)

if print_request is True: # print the request
    print(c.request)

if validate is True: # do XML validation
    print('Validating request XML')
    if util.xmlvalid(c.request, csw.schema_location.split()[1]) is True:
        print('request is valid XML')
    else:
        print('request is NOT valid XML')

# print response
print(c.response)

