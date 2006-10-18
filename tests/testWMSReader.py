# $Id: runalltests.py,v 1.1.1.1 2004/12/06 03:28:23 sgillies Exp $

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
# =============================================================================

import unittest

try:
    import pkg_resources
    pkg_resources.require('OWSLib')
except (ImportError, pkg_resources.DistributionNotFound):
    pass

from owslib.wms import WMSCapabilitiesReader

class Reader111Test(unittest.TestCase):

    def test_reader(self):
        reader = WMSCapabilitiesReader('1.1.1')
        cap = reader.read('http://wms.jpl.nasa.gov/wms.cgi')
        self.assertEqual(cap.getroot().tag, 'WMT_MS_Capabilities')
        self.assertEqual(cap.servicename(), 'OGC:WMS')
        self.assertEqual(cap.servicetitle(), 'JPL Global Imagery Service')
        self.assertEqual(cap.getmapformats(), 
            ('image/jpeg', 'image/png', 'image/geotiff', 'image/tiff')
            )
        self.assertEqual(cap.layersrs(), ('EPSG:4326', 'AUTO:42003'))
        self.assertEqual(cap.layernames(), (
            'global_mosaic', 'global_mosaic_base', 'us_landsat_wgs84', 'srtm_mag', 'daily_terra_721', 'daily_aqua_721', 'daily_terra_ndvi', 'daily_aqua_ndvi', 'daily_terra', 'daily_aqua', 'BMNG', 'modis', 'huemapped_srtm', 'srtmplus', 'worldwind_dem', 'us_ned', 'us_elevation', 'us_colordem')
            )
        self.assert_('WMS Global Mosaic, pan sharpened' in cap.layertitles(),
            cap.layertitles()
            )
    
# ============================================================================
if __name__ == '__main__':
    unittest.main()
        
