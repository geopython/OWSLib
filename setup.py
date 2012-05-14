from setuptools import setup, find_packages, Command
import os

readme = open('README.txt', 'rb').read()

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

setup(name          = 'OWSLib',
      version       = '0.4.0',
      description   = 'OGC Web Service utility library',
      long_description = readme,
      license       = 'BSD',
      keywords      = 'gis ogc iso 19115 fgdc dif ows wfs wms sos csw capabilities metadata',
      author        = 'Sean Gillies',
      author_email  = 'sgillies@frii.com',
      maintainer        = 'Sean Gillies',
      maintainer_email  = 'sgillies@frii.com',
      url           = 'https://sourceforge.net/apps/trac/owslib',
      packages      = find_packages(),
      cmdclass = {'test': PyTest},
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

