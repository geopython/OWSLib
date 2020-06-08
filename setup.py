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

readme = open('README.rst').read()
reqs = [line.strip() for line in open('requirements.txt')]

setup(name              = 'OWSLib',
      version           = owslib.__version__,
      description       = 'OGC Web Service utility library',
      long_description  = readme,
      long_description_content_type = 'text/x-rst',
      license           = 'BSD',
      keywords          = 'gis ogc iso 19115 fgdc dif ows wfs wms sos csw wps wcs capabilities metadata wmts',
      author            = 'Sean Gillies',
      author_email      = 'sean.gillies@gmail.com',
      maintainer        = 'Tom Kralidis',
      maintainer_email  = 'tomkralidis@gmail.com',
      url               = 'https://geopython.github.io/OWSLib',
      install_requires  = reqs,
      python_requires   = '>=3.6',
      cmdclass          = {'test': PyTest},
      packages          = find_packages(exclude=["docs", "etc", "examples", "tests"]),
      classifiers       = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering :: GIS',
        ],
)
