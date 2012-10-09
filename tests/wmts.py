from owslib.wmts import WebMapTileService
wmts = WebMapTileService("http://map1.vis.earthdata.nasa.gov/wmts-geo/wmts.cgi")
print wmts.identification.type
print wmts.identification.version
print wmts.identification.title
print wmts.identification.abstract
print
print list(wmts.contents)
print
print wmts['MODIS_Aqua_Cloud_Top_Temp_Night'].title
print wmts['MODIS_Aqua_Cloud_Top_Temp_Night'].boundingBoxWGS84
print wmts['MODIS_Aqua_Cloud_Top_Temp_Night'].crsOptions # broken
print wmts['MODIS_Aqua_Cloud_Top_Temp_Night'].styles # broken
print "layer formats:", wmts['MODIS_Aqua_Cloud_Top_Temp_Night'].formats
print
print "known operations:", [op.name for op in wmts.operations]
print "known capabilities methods:", wmts.getOperationByName('GetCapabilities').methods
print "known tiles methods:", wmts.getOperationByName('GetTile').methods # broken
print "known tiles formatOptions:",  wmts.getOperationByName('GetTile').formatOptions # broken

# TODO test gettile