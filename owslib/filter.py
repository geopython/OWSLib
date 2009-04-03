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

from etree import etree

class Filter_Capabilities:
    """ Abstraction for Filter_Capabilities """
    def __init__(self, elem):
        """Initialize a Filter_Capabilities construct"""

        # Spatial_Capabilities
        self.spatial_operands = [f.text for f in elem.findall('{http://www.opengis.net/ogc}Spatial_Capabilities/{http://www.opengis.net/ogc}GeometryOperands/{http://www.opengis.net/ogc}GeometryOperand')]
        self.spatial_operators = []
        for f in elem.findall('{http://www.opengis.net/ogc}Spatial_Capabilities/{http://www.opengis.net/ogc}SpatialOperators/{http://www.opengis.net/ogc}SpatialOperator'):
            self.spatial_operators.append(f.attrib['name'])

        # Temporal_Capabilities
        self.temporal_operands = [f.text for f in elem.findall('{http://www.opengis.net/ogc}Temporal_Capabilities/{http://www.opengis.net/ogc}TemporalOperands/{http://www.opengis.net/ogc}TemporalOperand')]
        self.temporal_operators = []
        for f in elem.findall('{http://www.opengis.net/ogc}Temporal_Capabilities/{http://www.opengis.net/ogc}TemporalOperators/{http://www.opengis.net/ogc}TemporalOperator'):
            self.temporal_operators.append(f.attrib['name'])

        # Scalar_Capabilities
        self.scalar_comparison_operators = [f.text for f in elem.findall('{http://www.opengis.net/ogc}Scalar_Capabilities/{http://www.opengis.net/ogc}ComparisonOperators/{http://www.opengis.net/ogc}ComparisonOperator')]

