from setuptools import setup, find_packages
import owslib

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
      test_suite    = 'tests.test_suite',
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

