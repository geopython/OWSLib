
from setuptools import setup

setup(name          = 'OWSLib',
      version       = '0.2.0',
      description   = 'OGC Web Service utility library',
      license       = 'BSD',
      keywords      = 'gis ogc ows wfs wms capabilities metadata',
      author        = 'Sean Gillies',
      author_email  = 'sgillies@frii.com',
      maintainer        = 'Sean Gillies',
      maintainer_email  = 'sgillies@frii.com',
      url           = 'http://trac.gispython.org/projects/PCL/wiki/OwsLib',
      packages      = ['owslib'],
      classifiers   = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
        ],
)

