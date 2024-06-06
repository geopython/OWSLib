# -*- coding: utf-8 -*-
# =============================================================================
# Authors : Alexander Kmoch <allixender@gmail.com>
#
# =============================================================================

"""
initial test setup for Ows Context
"""

import os

from owslib.owscontext.atom import decode_atomxml
from owslib.owscontext.core import OwcContext
from tests.utils import resource_file, setup_logging, scratch_file

from owslib.etree import etree
from owslib import util
from owslib.namespaces import Namespaces
from owslib.util import nspath_eval

from owslib.owscontext.common import is_empty

# default variables
add_namespaces = {"georss": "http://www.georss.org/georss",
                  "owc": "http://www.opengis.net/owc/1.0",
                  "xml": "http://www.w3.org/XML/1998/namespace"}


def get_namespaces():
    n = Namespaces()
    ns = n.get_namespaces(["atom", "dc", "gml", "gml32", "xlink"])
    ns.update(add_namespaces)
    ns[None] = n.get_namespace("atom")
    return ns


ns = get_namespaces()


def nspv(path):
    """
    short-hand syntax seen in waterml2.py
    :param path: xpath namespace aware
    :return: xml element
    """
    return nspath_eval(path, ns)


logger = setup_logging(loglevel='DEBUG')


def setup_module(module):
    """Setup for the owc test module"""
    logger.debug('Setup logging in debug')
    # Do actual setup stuff here if necessary
    pass


def test_load_feeds_bulk():
    atom1 = open(resource_file(os.path.join('owc_atom_examples', 'geotiff.xml')), 'rb').read()
    atom2 = open(resource_file(os.path.join('owc_atom_examples', 'csw_10entries.xml')), 'rb').read()
    atom3 = open(resource_file(os.path.join('owc_atom_examples', 'gml_road.xml')), 'rb').read()
    atom4 = open(resource_file(os.path.join('owc_atom_examples', 'gmlcov.xml')), 'rb').read()
    atom5 = open(resource_file(os.path.join('owc_atom_examples', 'meris.atom')), 'rb').read()
    atom6 = open(resource_file(os.path.join('owc_atom_examples', 'meris_borders_users.atom')), 'rb').read()
    atom7 = open(resource_file(os.path.join('owc_atom_examples', 'meris_noauthor.xml')), 'rb').read()
    atom8 = open(resource_file(os.path.join('owc_atom_examples', 'meris_noprofile.xml')), 'rb').read()
    atom9 = open(resource_file(os.path.join('owc_atom_examples', 'sea_ice_extent_01.atom')), 'rb').read()
    atom10 = open(resource_file(os.path.join('owc_atom_examples', 'wcs_kml.xml')), 'rb').read()
    atom11 = open(resource_file(os.path.join('owc_atom_examples', 'wfs_100entries.xml')), 'rb').read()
    atom12 = open(resource_file(os.path.join('owc_atom_examples', 'wms_gml_hurricane_tomas.xml')), 'rb').read()
    atom13 = open(resource_file(os.path.join('owc_atom_examples', 'wms_meris.xml')), 'rb').read()
    atom14 = open(resource_file(os.path.join('owc_atom_examples', 'wms_scale.xml')), 'rb').read()
    atom15 = open(resource_file(os.path.join('owc_atom_examples', 'wmstestdata.xml')), 'rb').read()
    atom16 = open(resource_file(os.path.join('owc_atom_examples', 'wmts.xml')), 'rb').read()
    atom17 = open(resource_file(os.path.join('owc_atom_examples', 'wps_52north.xml')), 'rb').read()

    feeds = [atom1, atom2, atom3, atom4, atom5, atom6, atom7, atom8, atom9, atom10,
             atom11, atom12, atom13, atom14, atom15, atom16, atom17]

    for f in feeds:
        dict_obj = decode_atomxml(f)
        assert dict_obj is not None
        owc = OwcContext.from_dict(dict_obj)
        assert owc is not None
        for res in owc.resources:
            assert res.title is not None

        jsdata = owc.to_json()
        assert jsdata is not None
        assert len(jsdata) > 10
        re_owc = OwcContext.from_json(jsdata)
        assert re_owc is not None

        assert owc.to_dict() == re_owc.to_dict()

        # and other way round
        a_owc = OwcContext.from_atomxml(f)
        assert a_owc is not None
        assert len(a_owc.resources) > 0
        for a_res in a_owc.resources:
            assert len(a_res.offerings) > 0
            for a_off in a_res.offerings:
                ops = len(a_off.operations)
                con = len(a_off.contents)
                sty = len(a_off.styles)
                assert (ops + con + sty) > 0

        a_jsdata = a_owc.to_json()
        a_re_owc = OwcContext.from_json(a_jsdata)
        assert len(a_re_owc.resources) > 0
        for a_re_res in a_owc.resources:
            assert len(a_re_res.offerings) > 0
            for a_re_off in a_re_res.offerings:
                ops = len(a_re_off.operations)
                con = len(a_re_off.contents)
                sty = len(a_re_off.styles)
                assert (ops + con + sty) > 0
        assert a_owc.to_dict() == a_re_owc.to_dict()


def test_single_atomxml_coding():
    atom1 = open(resource_file(os.path.join('owc_atom_examples', 'wms_meris.xml')), 'rb').read()
    owc = OwcContext.from_atomxml(atom1)
    assert owc is not None
    for res in owc.resources:
        assert res.title is not None
        assert len(res.offerings) > 0
        for off in res.offerings:
            assert off.operations is not None
            assert len(off.operations) > 0

    jsdata = owc.to_json()
    assert jsdata is not None
    assert len(jsdata) > 10
    re_owc = OwcContext.from_json(jsdata)
    assert re_owc is not None
    for res in re_owc.resources:
        assert res.title is not None
        assert len(res.offerings) > 0
        for off in res.offerings:
            assert off.operations is not None
            assert len(off.operations) > 0
    assert owc.to_dict() == re_owc.to_dict()
