import doctest
import glob
import pkg_resources

try:
    pkg_resources.require('OWSLib')
except (ImportError, pkg_resources.DistributionNotFound):
    pass

testfiles = glob.glob('*.txt')

for file in testfiles: 
    doctest.testfile(file)

