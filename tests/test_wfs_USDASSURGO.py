# Test ability of OWSLib.wfs to interact with USDA SSURGO WFS 1.0.0 web service
# Contact e-mail: selimnairb@gmail.com
import unittest

from owslib.wfs import WebFeatureService

class USDASSURGOWFSTestCase(unittest.TestCase):
    
    def runTest(self):
        minX = -76.766960
        minY = 39.283611
        maxX = -76.684120
        maxY = 39.338394
        
        filter = "<Filter><BBOX><PropertyName>Geometry</PropertyName> <Box srsName='EPSG:4326'><coordinates>%f,%f %f,%f</coordinates> </Box></BBOX></Filter>" % (minX, minY, maxX, maxY)
        wfs = WebFeatureService('http://SDMDataAccess.nrcs.usda.gov/Spatial/SDMWGS84Geographic.wfs', version='1.0.0')
        response = wfs.getfeature(typename=('MapunitPolyExtended',), filter=filter, propertyname=None)
        self.assertTrue(response.read().find('<wfs:FeatureCollection') > 0,
                        'Unable to find feature dataset in WFS response')


