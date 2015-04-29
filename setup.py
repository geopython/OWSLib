from __future__ import absolute_import
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
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

readme = open('README.txt').read()
reqs = [line.strip() for line in open('requirements.txt')]

if sys.version[:3] < '2.7':
    reqs += [line.strip() for line in open('requirements-2.6.txt')]

setup(name              = 'OWSLib',
      version           = owslib.__version__,
      description       = 'OGC Web Service utility library',
      long_description  = readme,
      license           = 'BSD',
      keywords          = 'gis ogc iso 19115 fgdc dif ows wfs wms sos csw wps wcs capabilities metadata wmts',
      author            = 'Sean Gillies',
      author_email      = 'sean.gillies@gmail.com',
      maintainer        = 'Tom Kralidis',
      maintainer_email  = 'tomkralidis@gmail.com',
      url               = 'http://geopython.github.io/OWSLib',
      install_requires  = reqs,
      cmdclass          = {'test': PyTest},
      packages          = find_packages(exclude=["docs", "etc", "examples", "tests"]),
      classifiers       = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
        ],
)

