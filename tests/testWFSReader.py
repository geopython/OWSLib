# $Id: testWFSReader.py 503 2006-02-01 17:09:12Z dokai $

# =============================================================================
# OWSLib. Copyright (C) 2005 Sean C. Gillies
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA
#
# Contact email: sgillies@frii.com
#
# $Id: testWFSReader.py 503 2006-02-01 17:09:12Z dokai $ 
#
# =============================================================================

import unittest

try:
    import pkg_resources
    pkg_resources.require('OWSLib')
except (ImportError, pkg_resources.DistributionNotFound):
    pass
    
from owslib.wfs import WFSCapabilitiesReader, nspath, OGC_NAMESPACE

class Reader111Test(unittest.TestCase):

    def test_reader(self):
        reader = WFSCapabilitiesReader('1.0.0')
        cap = reader.read('http://zcologia.com:9001/mapserver/members/capabilities.rpy')
        
        # XML nodes
        self.assertEquals(nspath('Service'), cap.getServiceNode().tag)
        self.assertEquals(nspath('Capability'), cap.getCapabilitiesNode().tag)
        self.assertEquals(nspath('FeatureTypeList'), cap.getFeatureTypeNode().tag)
        #self.assertEquals(nspath('Filter_Capabilities', OGC_NAMESPACE),
        #                  cap.getFilterNode().tag)

        # Service info
        serviceinfo = cap.getServiceInfo()
        self.assertEquals('Cheapo WFS', serviceinfo.get('name'))
        self.assertEquals('Really Cheap WFS',
                          serviceinfo.get('title'))
        self.assertEquals('http://zcologia.com:9001',
                          serviceinfo.get('onlineresource'))

        # Capability info
        capinfo = cap.getCapabilityInfo()
        self.assertEquals('http://zcologia.com:9001/mapserver/members/capabilities.rpy',
                          capinfo.get('capabilities'))
        self.assertEquals('http://zcologia.com:9001/mapserver/members/description.rpy',
                          capinfo.get('description'))
        self.assertEquals('http://zcologia.com:9001/mapserver/members/features.rpy',
                          capinfo.get('features'))

        # Feature type info
        featinfo = cap.getFeatureTypeInfo()
        self.assertEquals(1, len(featinfo))
        self.assertEquals('points', featinfo[0].get('name'))
        self.assertEquals('EPSG:4326', featinfo[0].get('srs'))
        self.assertEquals(['-120,30,-100,50'], featinfo[0].get('latlongboundingbox'))
        

# ============================================================================
if __name__ == '__main__':
    unittest.main()

    
