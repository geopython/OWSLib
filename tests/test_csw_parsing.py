# -*- coding: utf-8 -*-

import io

from owslib import util
from owslib.etree import etree
from owslib.csw import (
    CswRecord
)
from owslib.namespaces import Namespaces


def get_md_resource(file_path):
    """Read the file and parse into an XML tree.

    Parameters
    ----------
    file_path : str
        Path of the file to read.

    Returns
    -------
    etree.ElementTree
        XML tree of the resource on disk.

    """
    namespaces = Namespaces().get_namespaces(keys=('dc', 'dct', 'ows', 'rdf', 'gml', 'csw'))

    with io.open(file_path, mode='r', encoding='utf-8') as f:
        data = f.read().encode('utf-8')
        mdelem = etree.fromstring(data)

    return mdelem


def test_md_parsing():
    """Test the parsing of a metadatarecord 

    GetRecordById response available in
    tests/resources/9250AA67-F3AC-6C12-0CB9-0662231AA181_dc.xml

    """
    md_resource = get_md_resource('tests/resources/9250AA67-F3AC-6C12-0CB9-0662231AA181_dc.xml')
    md = CswRecord(md_resource)

    assert type(md) is CswRecord

    assert md.identifier == '9250AA67-F3AC-6C12-0CB9-0662231AA181'
    assert md.title == 'ALLSPECIES'
    assert md.format == 'text/xml'
    assert md.bbox.minx == '-180'
    assert md.contributor == 'EMAN Office'
    assert md.creator == 'EMAN Coordinating Office, Environment Canada'
    assert md.created == '2009-09-03'
    assert md.language == 'eng; CAN'

def test_spatial_parsing():
    """Test the parsing of a metadatarecord 

    GetRecordById response available in
    tests/resources/9250AA67-F3AC-6C12-0CB9-0662231AA181_dc2.xml

    """
    md_resource = get_md_resource('tests/resources/9250AA67-F3AC-6C12-0CB9-0662231AA181_dc2.xml')
    md = CswRecord(md_resource)

    assert type(md) is CswRecord
    assert md.title == "Feasibility of Using the Two-Source Energy Balance Model (TSEB) with Sentinel-2 and Sentinel-3 Images to Analyze the Spatio-Temporal Variability of Vine Water Status in a Vineyard"
    assert md.bbox.minx == '-180'