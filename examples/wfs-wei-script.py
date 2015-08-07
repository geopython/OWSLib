#!/usr/bin/python
# -*- coding: UTF-8 -*-
__author__ = 'Juergen Weichand'


from owslib.wfs import WebFeatureService

wfs = WebFeatureService(url='http://geoserv.weichand.de:8080/geoserver/wfs', version='2.0.0', timeout=30)

# List StoredQueries
print('\nStoredQueries for %s' % wfs.identification.title)
for storedquery in wfs.storedqueries:
    print(storedquery.id, storedquery.title)

# List Parameter for a given StoredQuery
storedquery = wfs.storedqueries[5]
print('\nStoredQuery parameters for %s' % storedquery.id)
for parameter in storedquery.parameters:
    print(parameter.name, parameter.type)

# GetFeature StoredQuery
print('\nDownload data from %s' % wfs.identification.title)
response = wfs.getfeature(
    storedQueryID='GemeindeByGemeindeschluesselEpsg31468',
    storedQueryParams={'gemeindeschluessel':'09162000'})
out = open('/tmp/test-storedquery.gml', 'wb')
out.write(response.read())
out.close()
print('... done')
