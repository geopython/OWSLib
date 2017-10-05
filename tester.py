from owslib.wcs import WebCoverageService


#t = WebCoverageService('https://eodataservice.org/rasdaman/ows?', version='2.0.0')

eoxt = WebCoverageService('http://ows.eox.at/cite/mapserver?', version="2.0.1")

#print t.contents['CCI_V2_release_chlor_a'].supportedFormats

# for x in eoxt.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].timepositions:
# 	print x.isoformat()

# print t.provider

# print t.provider.contact

# print t.provider.contact.name

# print t.provider.name

# def dump(obj):
# 	for attr in dir(obj):
# 		if "_" not in attr:
# 			print "obj.%s = %s" % (attr, getattr(obj, attr))





# dump(t.provider) 
# dump(t.provider.contact)

# print t.contents


print eoxt.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].grid.dimension
print eoxt.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].grid.lowlimits
print eoxt.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].grid.highlimits
print eoxt.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].grid.axislabels
print eoxt.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].grid.origin
print eoxt.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].grid.offsetvectors

# print t.contents['CCI_V2_monthly_chlor_a_bias'].boundingboxes 

print eoxt.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].supportedFormats

#        http://earthserver.pml.ac.uk/rasdaman/ows?&SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage
#        &COVERAGEID=V2_monthly_CCI_chlor_a_insitu_test&SUBSET=Lat(40,50)&SUBSET=Long(-10,0)&SUBSET=ansi(144883,145000)&FORMAT=application/netcdf
# #         cvg=wcs.getCoverage(identifier=['myID'], format='application/netcdf', subsets=[('axisName',min,max),('axisName',min,max),('axisName',min,max)])

# cov = t.getCoverage(identifier=['CCI_V2_release_chlor_a'], format='application/netcdf', subsets=[('Long',-10,0), ('Lat',40,50),('ansi',"2011-02-28T23:59:00","2011-03-31T23:59:00")])


# filename = 'wcs200test.nc'
# f=open(filename, 'wb')
# bytes_written = f.write(cov.read())
# f.close()

cov = eoxt.getCoverage(identifier=['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'], format='image/png', subsets=[('Long',-50,-40),('Lat',-30,-4)])#,('ansi',"2008-04-01T00:00:00.000Z")])


filename = 'eox_test.png'
f=open(filename, 'wb')
bytes_written = f.write(cov.read())
f.close()



# s = WebCoverageService('http://earthserver.ecmwf.int/rasdaman/ows?', version='2.0.0')
# # print s.contents

# print s.contents['temp2m']

# # dump(s.contents['temp2m'].grid)
# for x in s.contents['temp2m'].timepositions[0:100]:
# 	print x.isoformat()

# print s.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].grid.dimension
# print s.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].grid.lowlimits
# print s.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].grid.highlimits
# print s.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].grid.axislabels
# print s.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].grid.origin
# print s.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].grid.offsetvectors

# print s.contents['MER_FRS_1PNUPA20090701_124435_000005122080_00224_38354_6861_RGB'].boundingboxes
