from setuptools import setup, find_packages
import owslib
from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)



readme = open('README.txt', 'rb').read()

setup(name          = 'OWSLib',
      version       = owslib.__version__,
      description   = 'OGC Web Service utility library',
      long_description = readme,
      license       = 'BSD',
      keywords      = 'gis ogc iso 19115 fgdc dif ows wfs wms sos csw wps wcs capabilities metadata wmts',
      author        = 'Sean Gillies',
      author_email  = 'sgillies@frii.com',
      maintainer        = 'Sean Gillies',
      maintainer_email  = 'sgillies@frii.com',
      url           = 'https://geopython.github.com/OWSLib',
      packages      = find_packages(),
    #test_suite    = 'tests.test_suite',
    #XXX rewwrite tests so they can be called simply with
    # python setup.py test
      classifiers   = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
        ],
)

