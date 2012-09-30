# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2009 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@hotmail.com>
#
# Contact email: tomkralidis@hotmail.com
# =============================================================================

"""
API for OGC Filter Encoding (FE) constructs and metadata.

Filter Encoding: http://www.opengeospatial.org/standards/filter

Currently supports version 1.1.0 (04-095).
"""

from owslib.etree import etree
from owslib.util import nspath_eval
from owslib.namespaces import OWSLibNamespaces

# default variables
schema = 'http://schemas.opengis.net/filter/1.1.0/filter.xsd'

ns = OWSLibNamespaces()
schema_location = '%s %s' % (ns.get_namespace('ogc'), schema)

class FilterRequest(object):
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

    def set(self, parent=False, qtype=None, keywords=[], typenames='csw:Record', propertyname='csw:AnyText', bbox=None, identifier=None):
        """

        Construct and process a  GetRecords request
    
        Parameters
        ----------

        - parent: the parent Element object.  If this is not, then generate a standalone request
        - qtype: type of resource to query (i.e. service, dataset)
        - keywords: list of keywords
        - propertyname: the PropertyName to Filter against 
        - bbox: the bounding box of the spatial query in the form [minx,miny,maxx,maxy]

        """

        # construct
        node0 = etree.Element(nspath_eval('ogc:Filter'))
        if parent is True:
            node0.set(nspath_eval('xsi:schemaLocation'), schema_location)

        if identifier is not None:
            self._setpropertyisequalto(node0, 'dc:identifier', identifier)
            return node0

        # decipher number of query parameters ( > 1 sets an 'And' Filter)
        pcount = 0
        if qtype is not None:
            pcount += 1
        if keywords:
            pcount += 1
        if bbox is not None:
            pcount += 1

        if pcount > 1: # Filter should be And-ed===
            node1 = etree.SubElement(node0, nspath_eval('ogc:And'))
        else: 
            node1 = None
    
        # set the query type if passed
        # TODO: need a smarter way to figure these out
        if qtype is not None:
            if node1 is not None:
                self._setpropertyisequalto(node1, 'dc:type', qtype)
            else:
                self._setpropertyisequalto(node0, 'dc:type', qtype)
    
        # set a bbox query if passed
        if bbox is not None:
            if node1 is not None:
                self._setbbox(node1, bbox)
            else:
                self._setbbox(node0, bbox)
    
        # set a keyword query if passed
        if len(keywords) > 0:
            if len(keywords) > 1: # loop multiple keywords into an Or
                if node1 is not None:
                    node3 = etree.SubElement(node1, nspath_eval('ogc:Or'))
                else:
                    node3 = etree.SubElement(node0, nspath_eval('ogc:Or'))
    
                for i in keywords:
                    self._setpropertyislike(node3, propertyname, '%%%s%%' % i)
    
            else: # one keyword
                if node1 is not None:
                    self._setpropertyislike(node1, propertyname, '%%%s%%' % keywords[0])
                else:
                    self._setpropertyislike(node0, propertyname, '%%%s%%' % keywords[0])
    
        return node0

    def _setpropertyisequalto(self, parent, propertyname, literal, matchcase=True):
        """

        construct a PropertyIsEqualTo

        Parameters
        ----------

        - parent: parent etree.Element object
        - propertyname: the PropertyName
        - literal: the Literal value
        - matchcase: whether to perform a case insensitve query (default is True)

        """

        tmp = etree.SubElement(parent, nspath_eval('ogc:PropertyIsEqualTo'))
        if matchcase is False:
            tmp.set('matchCase', 'false')
        etree.SubElement(tmp, nspath_eval('ogc:PropertyName')).text = propertyname
        etree.SubElement(tmp, nspath_eval('ogc:Literal')).text = literal
    
    def _setbbox(self, parent, bbox):
        """

        construct a BBOX search predicate

        Parameters
        ----------

        - parent: parent etree.Element object
        - bbox: the bounding box in the form [minx,miny,maxx,maxy]

        """

        tmp = etree.SubElement(parent, nspath_eval('ogc:BBOX'))
        etree.SubElement(tmp, nspath_eval('ogc:PropertyName')).text = 'ows:BoundingBox'
        tmp2 = etree.SubElement(tmp, nspath_eval('gml:Envelope'))
        etree.SubElement(tmp2, nspath_eval('gml:lowerCorner')).text = '%s %s' % (bbox[0], bbox[1])
        etree.SubElement(tmp2, nspath_eval('gml:upperCorner')).text = '%s %s' % (bbox[2], bbox[3])

    def _setpropertyislike(self, parent, propertyname, literal, wildcard='%', singlechar='_', escapechar='\\'):  
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

        tmp = etree.SubElement(parent, nspath_eval('ogc:PropertyIsLike'))
        tmp.set('wildCard', wildcard)
        tmp.set('singleChar', singlechar)
        tmp.set('escapeChar', escapechar)
        etree.SubElement(tmp, nspath_eval('ogc:PropertyName')).text = propertyname
        etree.SubElement(tmp, nspath_eval('ogc:Literal')).text = literal


class FilterCapabilities(object):
    """ Abstraction for Filter_Capabilities """
    def __init__(self, elem):
        # Spatial_Capabilities
        self.spatial_operands = [f.text for f in elem.findall(nspath_eval('ogc:Spatial_Capabilities/ogc:GeometryOperands/ogc:GeometryOperand'))]
        self.spatial_operators = []
        for f in elem.findall(nspath_eval('ogc:Spatial_Capabilities/ogc:SpatialOperators/ogc:SpatialOperator')):
            self.spatial_operators.append(f.attrib['name'])

        # Temporal_Capabilities
        self.temporal_operands = [f.text for f in elem.findall(nspath_eval('ogc:Temporal_Capabilities/ogc:TemporalOperands/ogc:TemporalOperand'))]
        self.temporal_operators = []
        for f in elem.findall(nspath_eval('ogc:Temporal_Capabilities/ogc:TemporalOperators/ogc:TemporalOperator')):
            self.temporal_operators.append(f.attrib['name'])

        # Scalar_Capabilities
        self.scalar_comparison_operators = [f.text for f in elem.findall(nspath_eval('ogc:Scalar_Capabilities/ogc:ComparisonOperators/ogc:ComparisonOperator'))]

def setsortby(parent, propertyname, order='ASC'):
    """

    constructs a SortBy element

    Parameters
    ----------

    - parent: parent etree.Element object
    - propertyname: the PropertyName
    - order: the SortOrder (default is 'ASC')

    """

    tmp = etree.SubElement(parent, nspath_eval('ogc:SortBy'))
    tmp2 = etree.SubElement(tmp, nspath_eval('ogc:SortProperty'))
    etree.SubElement(tmp2, nspath_eval('ogc:PropertyName')).text = propertyname
    etree.SubElement(tmp2, nspath_eval('ogc:SortOrder')).text = order
