#!/usr/bin/python
# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2009 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@hotmail.com>
#
# Contact email: tomkralidis@hotmail.com
# =============================================================================

from lxml import etree
from owslib import util

# default variables

schema = 'http://schemas.opengis.net/filter/1.1.0/filter.xsd'

namespaces = {
    None : 'http://www.opengis.net/ogc',
    'gml': 'http://www.opengis.net/gml',
    'ogc': 'http://www.opengis.net/ogc',
    'xs' : 'http://www.w3.org/2001/XMLSchema',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}

schema_location = '%s %s' % (namespaces['ogc'], schema)

class filter:
    """ filter class """
    def __init__(self, version='1.1.0'):
        """

        filter Constructor

        Parameters 
        ----------

        - parent: parent etree.Element object (default is None)
        - version: version (default is '1.1.0')

        """

        self.version = version

    def Filter(self, parent=None):
        if parent is None:
            tmp = etree.Element(util.nspath('Filter', namespaces['ogc']), nsmap=namespaces)
            tmp.set(util.nspath('schemaLocation', namespaces['xsi']), schema_location)
            return tmp
        else:
            etree.SubElement(parent, util.nspath('Filter', namespaces['ogc']))

    def PropertyIsEqualTo(self, parent, propertyname, literal):
        """

        construct a PropertyIsEqualTo

        Parameters
        ----------

        - parent: parent etree.Element object
        - propertyname: the PropertyName
        - literal: the Literal value

        """

        tmp = etree.SubElement(parent, util.nspath('PropertyIsEqualTo', namespaces['ogc']))
        etree.SubElement(tmp, util.nspath('PropertyName', namespaces['ogc'])).text = propertyname
        etree.SubElement(tmp, util.nspath('Literal', namespaces['ogc'])).text = literal
    
    def BBOX(self, parent, bbox):
        """

        construct a BBOX search predicate

        Parameters
        ----------

        - parent: parent etree.Element object
        - bbox: the bounding box in the form [minx,miny,maxx,maxy]

        """

        tmp = etree.SubElement(parent, util.nspath('BBOX', namespaces['ogc']))
        etree.SubElement(tmp, util.nspath('PropertyName', namespaces['ogc'])).text = 'ows:BoundingBox'
        tmp2 = etree.SubElement(tmp, util.nspath('Envelope', namespaces['gml']))
        etree.SubElement(tmp2, util.nspath('lowerCorner', namespaces['gml'])).text = '%s %s' % (bbox[0], bbox[1])
        etree.SubElement(tmp2, util.nspath('upperCorner', namespaces['gml'])).text = '%s %s' % (bbox[2], bbox[3])

    def PropertyIsLike(self, parent, propertyname, literal, wildcard='%', singlechar='_', escapechar='\\'):  
        """

        construct a PropertyIsLike

        Parameters
        ----------

        - parent: parent etree.Element object
        - propertyname: the PropertyName
        - literal: the Literal value
        - wildcard: the wildCard character (default is '%')
        - singlechar: the singleChar character (default is '_')
        - escapechar: the escapeChar character (default is '\')

        """

        tmp = etree.SubElement(parent, util.nspath('PropertyIsLike', namespaces['ogc']))
        tmp.set('wildCard', wildcard)
        tmp.set('singleChar', singlechar)
        tmp.set('escapeChar', escapechar)
        etree.SubElement(tmp, util.nspath('PropertyName', namespaces['ogc'])).text = propertyname
        etree.SubElement(tmp, util.nspath('Literal', namespaces['ogc'])).text = literal

    def SortBy(self, parent, propertyname, order='ASC'):
        """

        constructs a SortBy element

        Parameters
        ----------

        - parent: parent etree.Element object
        - propertyname: the PropertyName
        - order: the SortOrder (default is 'ASC')

        """

        tmp = etree.SubElement(parent, util.nspath('SortBy', namespaces1['ogc']))
        tmp2 = etree.SubElement(tmp, util.nspath('SortProperty', namespaces1['ogc']))
        etree.SubElement(tmp2, util.nspath('PropertyName', namespaces['ogc'])).text = propertyname
        etree.SubElement(tmp2, util.nspath('SortOrder', namespaces['ogc'])).text = order
