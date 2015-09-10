#!/usr/bin/python
# -*- coding: UTF-8 -*-
__author__ = 'Juergen Weichand'

from owslib.wms import WebMapService
wms = WebMapService('http://geoserv.weichand.de:8080/geoserver/wms')

# GetMap (image/jpeg)
response = wms.getmap(
    layers=['bvv:gmd_ex'],
    srs='EPSG:31468',
    bbox=(4500000,5500000,4505000,5505000),
    size=(500,500),
    format='image/jpeg')

out = open('/tmp/getmap-response.jpeg', 'wb')
out.write(response.read())
out.close()

# GetFeatureInfo (text/html)
response = wms.getfeatureinfo(
    layers=['bvv:gmd_ex'],
    srs='EPSG:31468',
    bbox=(4500000,5500000,4505000,5505000),
    size=(500,500),
    format='image/jpeg',
    query_layers=['bvv:gmd_ex'],
    info_format="text/html",
    xy=(250,250))

out = open('/tmp/getfeatureinfo-response.html', 'wb')
out.write(response.read())
out.close()