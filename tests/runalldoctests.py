import doctest
import getopt
import glob
import sys

try:
    import pkg_resources
    pkg_resources.require('OWSLib')
except (ImportError, pkg_resources.DistributionNotFound):
    pass

def open_file(filename, mode='r'):
    """Helper function to open files from within the tests package."""
    import os
    return open(os.path.join(os.path.dirname(__file__), filename), mode)

EXTRA_GLOBALS = {'open_file': open_file}

def run(pattern):
    if pattern is None:
        testfiles = glob.glob('*.txt')
    else:
        testfiles = glob.glob(pattern)
    for file in testfiles: 
        doctest.testfile(file, extraglobs=EXTRA_GLOBALS)

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "t:v")
    except getopt.GetoptError:
        print "Usage: python runalldoctests.py [-t GLOB_PATTERN]"
        sys.exit(2)
    pattern = None
    for o, a in opts:
        if o == '-t':
            pattern = a
    run(pattern)

