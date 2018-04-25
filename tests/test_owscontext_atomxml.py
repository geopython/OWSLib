# -*- coding: utf-8 -*-
# =============================================================================
# Authors : Alexander Kmoch <allixender@gmail.com>
#
# =============================================================================

"""
initial test setup for Ows Context
"""

from __future__ import (absolute_import, division, print_function)

import os

from owslib.owscontext.atom import decode_atomxml
from owslib.owscontext.core import OwcContext
from tests.utils import resource_file, setup_logging

logger = setup_logging(loglevel='INFO')


def setup_module(module):
    """Setup for the owc test module"""
    logger.debug('Setup logging in debug')
    # Do actual setup stuff here if necessary
    pass


def test_load_feeds_bulk():
    atom1 = open(resource_file(os.path.join('owc_atom_examples','geotiff.xml')), 'rb').read()
    atom2 = open(resource_file(os.path.join('owc_atom_examples','csw_10entries.xml')), 'rb').read()
    atom3 = open(resource_file(os.path.join('owc_atom_examples','gml_road.xml')), 'rb').read()
    atom4 = open(resource_file(os.path.join('owc_atom_examples','gmlcov.xml')), 'rb').read()
    atom5 = open(resource_file(os.path.join('owc_atom_examples','meris.atom')), 'rb').read()
    atom6 = open(resource_file(os.path.join('owc_atom_examples','meris_borders_users.atom')), 'rb').read()
    atom7 = open(resource_file(os.path.join('owc_atom_examples','meris_noauthor.xml')), 'rb').read()
    atom8 = open(resource_file(os.path.join('owc_atom_examples','meris_noprofile.xml')), 'rb').read()
    atom9 = open(resource_file(os.path.join('owc_atom_examples','sea_ice_extent_01.atom')), 'rb').read()
    atom10 = open(resource_file(os.path.join('owc_atom_examples','wcs_kml.xml')), 'rb').read()
    atom11 = open(resource_file(os.path.join('owc_atom_examples','wfs_100entries.xml')), 'rb').read()
    atom12 = open(resource_file(os.path.join('owc_atom_examples','wms_gml_hurricane_tomas.xml')), 'rb').read()
    atom13 = open(resource_file(os.path.join('owc_atom_examples','wms_meris.xml')), 'rb').read()
    atom14 = open(resource_file(os.path.join('owc_atom_examples','wms_scale.xml')), 'rb').read()
    atom15 = open(resource_file(os.path.join('owc_atom_examples','wmstestdata.xml')), 'rb').read()
    atom16 = open(resource_file(os.path.join('owc_atom_examples','wmts.xml')), 'rb').read()
    atom17 = open(resource_file(os.path.join('owc_atom_examples','wps_52north.xml')), 'rb').read()

    feeds = [atom1, atom2, atom3, atom4, atom5, atom6, atom7, atom8, atom9, atom10,
             atom11, atom12, atom13, atom14, atom15, atom16, atom17]

    for f in feeds:
        logger.debug(f)
        dict_obj = decode_atomxml(f)
        assert dict_obj is not None
        # logger.debug(dict_obj)
        owc = OwcContext.from_dict(dict_obj)
        assert owc is not None
        # logger.debug(OwcContext.from_dict(dict_obj).to_json())
        jsdata = owc.to_json()
        assert jsdata is not None
        assert len(jsdata) > 10
        re_owc = OwcContext.from_json(jsdata)
        assert re_owc is not None






