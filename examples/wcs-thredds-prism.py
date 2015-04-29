# Very simple script demonstrating how to interact with a THREDDS based WCS.
# ---
#
# The GetCapabilities and DescribeCoverage requests for this dataset are: 
# http://cida.usgs.gov/thredds/wcs/prism?service=WCS&version=1.0.0&request=GetCapabilities
# http://cida.usgs.gov/thredds/wcs/prism?service=WCS&version=1.0.0&request=DescribeCoverage
#
# The equivalent GetCoverage request that is equivalent ot hte example is:
# http://cida.usgs.gov/thredds/wcs/prism?request=GetCoverage&version=1.0.0&service=WCS&format=GeoTIFF&coverage=tmx&time=1895-01-01T00:00:00Z&bbox=-90,40,-89,41
# ---
# 
# Example to find the equivalent information using OWSLib:
# 
from __future__ import absolute_import
from __future__ import print_function
from owslib.wcs import WebCoverageService
wcs=WebCoverageService('http://cida.usgs.gov/thredds/wcs/prism',version='1.0.0')
# Take a look at the contents (coverages) of the wcs.
print(wcs.contents)
tmax=wcs['tmx']
# Take a look at the attributes of the coverage
dir(tmax)
print(tmax.boundingBoxWGS84)
print(tmax.timepositions)
print(tmax.supportedFormats)
# mock up a simple GetCoverage request.
output=wcs.getCoverage(identifier='tmx',time=['1895-01-01T00:00:00Z'],bbox=(-90,40,-89,41),format='GeoTIFF')
# Write the file out to disk.
f=open('foo.tif','wb')
f.write(output.read())
f.close()
