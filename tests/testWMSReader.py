# $Id: runalltests.py,v 1.1.1.1 2004/12/06 03:28:23 sgillies Exp $

# =============================================================================
# Cartographic Objects for Zope. Copyright (C) 2004 Sean C. Gillies
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

from framework import ogclib
from ogclib.wms import WMSCapabilitiesReader

class Reader111Test(unittest.TestCase):

    def test_reader(self):
        reader = WMSCapabilitiesReader('1.1.1')
        cap = reader.read('http://wms.jpl.nasa.gov/wms.cgi')
        self.assert_(cap.getroot().tag == 'WMT_MS_Capabilities', cap.getroot())
        self.assert_(cap.servicename() == 'OGC:WMS', cap.servicename())
        self.assert_(cap.servicetitle() == 'JPL World Map Service', cap.servicetitle())
        self.assert_(cap.getmapformats() == ('image/jpeg', 'image/png', 'image/geotiff', 'image/tiff'), cap.getmapformats())
        self.assert_(cap.layersrs() == ('EPSG:4326', 'AUTO:42003'), cap.layersrs())
        self.assert_(cap.layernames() == ('global_mosaic', 'global_mosaic_base', 'us_landsat_wgs84', 'srtm_mag', 'us_overlays', 'us90_overlays', 'daily_terra', 'daily_aqua', 'BMNG', 'modis', 'huemapped_srtm', 'srtmplus', 'worldwind_dem', 'us_ned', 'us_elevation', 'us_colordem'), cap.layernames())
        self.assert_(cap.layertitles() == ('WMS Global Mosaic, pan sharpened', 'WMS Global Mosaic, not pan sharpened', 'CONUS mosaic of 1990 MRLC dataset', 'SRTM reflectance magnitude, 30m', 'Progressive US overlay map, white background', 'MRLC US mosaic with progressive overlay map', 'Daily composite of MODIS-TERRA images ', 'Daily composite of MODIS-AQUA images ', 'Blue Marble Next Generation, Global MODIS derived image', 'Blue Marble, Global MODIS derived image', 'SRTM derived global elevation, 3 arc-second, hue mapped', 'Global 1km elevation, seamless SRTM land elevation and ocean depth', 'SRTM derived global elevation, 3 arc-second', 'United States elevation, 30m', 'Digital Elevation Map of the United States, DTED dataset, 3 second resolution, grayscale', 'Digital Elevation Map of the United States, DTED dataset, 3 second resolution, hue mapped'), cap.layertitles())

    
# ============================================================================
if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
    

    
