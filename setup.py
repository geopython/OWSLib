
try:
    from setuptools import setup
except ImportError:
    from distutils import setup

setup(name          = 'OWSLib',
      version       = '0.1.0',
      description   = 'OGC Web Service utility package',
      license       = 'GPL',
      keywords      = 'ogc ows wfs wms capabilities metadata',
      author        = 'Sean Gillies',
      author_email  = 'sgillies@frii.com',
      maintainer        = 'Sean Gillies',
      maintainer_email  = 'sgillies@frii.com',
      url           = 'http://www.gispython.org',
      packages      = ['owslib'],
      classifiers   = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GPL License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
        ],
)

