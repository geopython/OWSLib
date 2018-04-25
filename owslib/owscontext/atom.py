# -*- coding: utf-8 -*-
# =============================================================================
# Authors : Alexander Kmoch <allixender@gmail.com>
#
# =============================================================================

"""
API for OGC Web Services Context Document (OWS Context) format.

ATOM XML Encoding: http://www.opengeospatial.org/standards/owc

OGC OWS Context Atom Encoding Standard 1.0 (12-084r2)
"""

from __future__ import (absolute_import, division, print_function)

from owslib.etree import etree
from owslib import util
from owslib.namespaces import Namespaces

# from owslib.util import log


def decode_atomxml(xmldata):
    """
    here parse atom xml to an instance of OWC:Context
    :param xmldata:
    :return: OWCContext
    """


def encode_atomxml(obj):
    """
    encode instance of OWCContext into atom xml encoding
    :param obj:
    :return: atomxml
    """
