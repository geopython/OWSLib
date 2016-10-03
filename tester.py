import owslib
from owslib.wcs import WebCoverageService


t = WebCoverageService('http://earthserver.pml.ac.uk/rasdaman/ows?', version='2.0.0')

print t.contents['CCI_V2_release_chlor_a'].supportedFormats

for x in t.contents['CCI_V2_release_chlor_a'].timepositions:
 	print x.isoformat()

# print t.provider

# print t.provider.contact

# print t.provider.contact.name

# print t.provider.name

def dump(obj):
	for attr in dir(obj):
		if "_" not in attr:
			print "obj.%s = %s" % (attr, getattr(obj, attr))





# dump(t.provider) 
# dump(t.provider.contact)

# print t.contents


# print t.contents['CCI_V2_monthly_chlor_a_bias'].grid.dimension
# print t.contents['CCI_V2_monthly_chlor_a_bias'].grid.lowlimits
# print t.contents['CCI_V2_monthly_chlor_a_bias'].grid.highlimits
# print t.contents['CCI_V2_monthly_chlor_a_bias'].grid.axislabels
# print t.contents['CCI_V2_monthly_chlor_a_bias'].grid.origin
# print t.contents['CCI_V2_monthly_chlor_a_bias'].grid.offsetvectors

# print t.contents['CCI_V2_monthly_chlor_a_bias'].boundingboxes 

# print t.contents['CCI_V2_monthly_chlor_a_bias'].supportedFormats

#        http://earthserver.pml.ac.uk/rasdaman/ows?&SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage
#        &COVERAGEID=V2_monthly_CCI_chlor_a_insitu_test&SUBSET=Lat(40,50)&SUBSET=Long(-10,0)&SUBSET=ansi(144883,145000)&FORMAT=application/netcdf
# #         cvg=wcs.getCoverage(identifier=['myID'], format='application/netcdf', subsets=[('axisName',min,max),('axisName',min,max),('axisName',min,max)])

cov = t.getCoverage(identifier=['CCI_V2_monthly_chlor_a_bias'], format='application/netcdf', subsets=[('Long',-10,0), ('Lat',40,50),('ansi',"2000-01-31T00:00:00Z","2000-02-29T00:00:00Z")])


filename = 'wcs200test.nc'
f=open(filename, 'wb')
bytes_written = f.write(cov.read())
f.close()


# s = WebCoverageService('http://earthserver.ecmwf.int/rasdaman/ows?', version='2.0.0')
# print s.contents

# print s.contents['temp2m']

# dump(s.contents['temp2m'].grid)
# for x in s.contents['temp2m'].timepositions[0:100]:
# 	print x.isoformat()

# print s.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].grid.dimension
# print s.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].grid.lowlimits
# print s.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].grid.highlimits
# print s.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].grid.axislabels
# print s.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].grid.origin
# print s.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].grid.offsetvectors

# print s.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].boundingboxes
