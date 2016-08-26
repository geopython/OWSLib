import owslib
from owslib.wcs import WebCoverageService


t = WebCoverageService('http://earthserver.pml.ac.uk/rasdaman/ows?', version='2.0.0')


print t.contents


print t.contents['CCI_V2_monthly_chlor_a_bias'].grid.dimension
print t.contents['CCI_V2_monthly_chlor_a_bias'].grid.lowlimits
print t.contents['CCI_V2_monthly_chlor_a_bias'].grid.highlimits
print t.contents['CCI_V2_monthly_chlor_a_bias'].grid.axislabels
print t.contents['CCI_V2_monthly_chlor_a_bias'].grid.origin
print t.contents['CCI_V2_monthly_chlor_a_bias'].grid.offsetvectors

s = WebCoverageService('http://geo.weather.gc.ca/geomet-beta?', version='2.0.0')

print s.contents
print s.contents['RDPA.6P_PR'].grid.dimension
print s.contents['RDPA.6P_PR'].grid.lowlimits
print s.contents['RDPA.6P_PR'].grid.highlimits
print s.contents['RDPA.6P_PR'].grid.axislabels
print s.contents['RDPA.6P_PR'].grid.origin
print s.contents['RDPA.6P_PR'].grid.offsetvectors
