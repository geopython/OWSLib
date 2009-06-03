# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2008 Tom Kralidis
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

from lxml import etree
from owslib import util

FE_NAMESPACE = 'http://www.opengis.net/ogc'

class Filter_Capabilities:
    """ Abstraction for Filter_Capabilities """
    def __init__(self, elem):
        """Initialize a Filter_Capabilities construct"""

        # Spatial_Capabilities
        self.spatial_operands = [f.text for f in elem.findall(util.nspath('Spatial_Capabilities/GeometryOperands/GeometryOperand', FE_NAMESPACE))]
        self.spatial_operators = []
        for f in elem.findall(util.nspath('Spatial_Capabilities/SpatialOperators/SpatialOperator', FE_NAMESPACE)):
            self.spatial_operators.append(f.attrib['name'])

        # Temporal_Capabilities
        self.temporal_operands = [f.text for f in elem.findall(util.nspath('Temporal_Capabilities/TemporalOperands/TemporalOperand', FE_NAMESPACE))]
        self.temporal_operators = []
        for f in elem.findall(util.nspath('Temporal_Capabilities/TemporalOperators/TemporalOperator', FE_NAMESPACE)):
            self.temporal_operators.append(f.attrib['name'])

        # Scalar_Capabilities
        self.scalar_comparison_operators = [f.text for f in elem.findall(util.nspath('Scalar_Capabilities/ComparisonOperators/ComparisonOperator', FE_NAMESPACE))]

