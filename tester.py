import owslib
from owslib.wcs import WebCoverageService


t = WebCoverageService('http://earthserver.pml.ac.uk/rasdaman/ows?', version='2.0.0')


print t.contents
