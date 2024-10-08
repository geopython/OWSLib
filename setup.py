# =============================================================================
# Copyright (c) 2024 Tom Kralidis
#
# Author: Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

from pathlib import Path
import re
from setuptools import setup, find_packages
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


def read(filename, encoding='utf-8'):
    """read file contents"""

    fullpath = Path(__file__).resolve().parent / filename

    with fullpath.open() as fh:
        contents = fh.read().strip()
    return contents


def get_package_version():
    """get version from top-level package init"""
    version_file = read('owslib/__init__.py')
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


readme = open('README.md').read()
reqs = [line.strip() for line in open('requirements.txt')]

MANIFEST = Path('MANIFEST')

if MANIFEST.exists():
    MANIFEST.unlink()


setup(
    name='OWSLib',
    version=get_package_version(),
    description='OGC Web Service utility library',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    license='BSD',
    keywords=' '.join([
        'gis',
        'ogc',
        'ogcapi',
        'ows',
        'opensearch',
        'iso',
        '19115',
        'fgdc',
        'dif',
        'ows',
        'wfs',
        'wms',
        'sos',
        'csw',
        'wps',
        'wcs',
        'capabilities',
        'metadata',
        'wmts',
        'connectedsystems'
    ]),
    author='Sean Gillies',
    author_email='sean.gillies@gmail.com',
    maintainer='Tom Kralidis',
    maintainer_email='tomkralidis@gmail.com',
    url='https://owslib.readthedocs.io',
    install_requires=reqs,
    python_requires='>=3.10',
    cmdclass={'test': PyTest},
    packages=find_packages(exclude=["docs", "etc", "examples", "tests"]),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS'
    ]
)
