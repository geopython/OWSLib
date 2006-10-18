import doctest
import glob
import pkg_resources

pkg_resources.require('OWSLib')

testfiles = glob.glob('*WFS*.txt')

for file in testfiles: 
    doctest.testfile(file)

