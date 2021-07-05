# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2021 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

"""
API for OGC Filter Encoding (FE) constructs and metadata.

Filter Encoding: http://www.opengeospatial.org/standards/filter

Supports version 2.0.2 (09-026r2).
"""

from owslib.etree import etree
from owslib import util
from owslib.namespaces import Namespaces
from abc import ABCMeta, abstractmethod


# default variables
def get_namespaces():
    n = Namespaces()
    ns = n.get_namespaces(["dif", "fes", "gml", "ogc", "ows110", "xs", "xsi"])
    ns[None] = n.get_namespace("fes")
    return ns


namespaces = get_namespaces()
schema = 'http://schemas.opengis.net/filter/2.0/filterAll.xsd'
schema_location = '%s %s' % (namespaces['fes'], schema)


class FilterRequest(object):
    """ filter class """
    def __init__(self, parent=None, version='2.0.0'):
        """

        filter Constructor

        Parameters
        ----------

        - parent: parent etree.Element object (default is None)
        - version: version (default is '2.0.0')

        """

        self.version = version
        self._root = etree.Element(util.nspath_eval('fes:Filter', namespaces))
        if parent is not None:
            self._root.set(util.nspath_eval('xsi:schemaLocation', namespaces), schema_location)

    def set(self, parent=False, qtype=None, keywords=[], typenames='csw:Record', propertyname='csw:AnyText', bbox=None,
            identifier=None):
        """

        Construct and process a  GetRecords request

        Parameters
        ----------

        - parent: the parent Element object.  If this is not, then generate a standalone request
        - qtype: type of resource to query (i.e. service, dataset)
        - keywords: list of keywords
        - propertyname: the ValueReference to Filter against
        - bbox: the bounding box of the spatial query in the form [minx,miny,maxx,maxy]
        - identifier: the dc:identifier to query against with a PropertyIsEqualTo.  Ignores all other inputs.

        """

        # Set the identifier if passed.  Ignore other parameters
        dc_identifier_equals_filter = None
        if identifier is not None:
            dc_identifier_equals_filter = PropertyIsEqualTo('dc:identifier', identifier)
            self._root.append(dc_identifier_equals_filter.toXML())
            return self._root

        # Set the query type if passed
        dc_type_equals_filter = None
        if qtype is not None:
            dc_type_equals_filter = PropertyIsEqualTo('dc:type', qtype)

        # Set a bbox query if passed
        bbox_filter = None
        if bbox is not None:
            bbox_filter = BBox(bbox)

        # Set a keyword query if passed
        keyword_filter = None
        if len(keywords) > 0:
            if len(keywords) > 1:  # loop multiple keywords into an Or
                ks = []
                for i in keywords:
                    ks.append(PropertyIsLike(propertyname, "*%s*" % i, wildCard="*"))
                keyword_filter = Or(operations=ks)
            elif len(keywords) == 1:  # one keyword
                keyword_filter = PropertyIsLike(propertyname, "*%s*" % keywords[0], wildCard="*")

        # And together filters if more than one exists
        filters = [_f for _f in [keyword_filter, bbox_filter, dc_type_equals_filter] if _f]
        if len(filters) == 1:
            self._root.append(filters[0].toXML())
        elif len(filters) > 1:
            self._root.append(And(operations=filters).toXML())

        return self._root

    def setConstraint(self, constraint, tostring=False):
        """
        Construct and process a  GetRecords request

        Parameters
        ----------

        - constraint: An OgcExpression object
        - tostring (optional): return as string

        """
        self._root.append(constraint.toXML())

        if tostring:
            return util.element_to_string(self._root, xml_declaration=False)

        return self._root

    def setConstraintList(self, constraints, tostring=False):
        """
        Construct and process a  GetRecords request

        Parameters
        ----------

        - constraints: A list of OgcExpression objects
                       The list is interpretted like so:

                       [a,b,c]
                       a || b || c

                       [[a,b,c]]
                       a && b && c

                       [[a,b],[c],[d],[e]] or [[a,b],c,d,e]
                       (a && b) || c || d || e
        - tostring (optional): return as string

        """
        ors = []
        if len(constraints) == 1:
            if isinstance(constraints[0], OgcExpression):
                flt = self.setConstraint(constraints[0])
            else:
                self._root.append(And(operations=constraints[0]).toXML())
                flt = self._root
            if tostring:
                return util.element_to_string(flt, xml_declaration=False)
            else:
                return flt

        for c in constraints:
            if isinstance(c, OgcExpression):
                ors.append(c)
            elif isinstance(c, list) or isinstance(c, tuple):
                if len(c) == 1:
                    ors.append(c[0])
                elif len(c) >= 2:
                    ands = []
                    for sub in c:
                        if isinstance(sub, OgcExpression):
                            ands.append(sub)
                    ors.append(And(operations=ands))

        self._root.append(Or(operations=ors).toXML())

        if tostring:
            return util.element_to_string(self._root, xml_declaration=False)

        return self._root


class FilterCapabilities(object):
    """Abstraction for Filter_Capabilities 2.0"""
    def __init__(self, elem):

        if elem is None:
            self.spatial_operands = []
            self.spatial_operators = []
            self.temporal_operators = []
            self.temporal_operands = []
            self.scalar_comparison_operators = []
            self.conformance = {}
            return

        # Spatial_Capabilities
        self.spatial_operands = [f.attrib.get('name') for f in elem.findall(util.nspath_eval(
            'fes:Spatial_Capabilities/fes:GeometryOperands/fes:GeometryOperand', namespaces))]
        self.spatial_operators = []
        for f in elem.findall(util.nspath_eval(
                'fes:Spatial_Capabilities/fes:SpatialOperators/fes:SpatialOperator', namespaces)):
            self.spatial_operators.append(f.attrib['name'])

        # Temporal_Capabilities
        self.temporal_operands = [f.attrib.get('name') for f in elem.findall(util.nspath_eval(
            'fes:Temporal_Capabilities/fes:TemporalOperands/fes:TemporalOperand', namespaces))]
        self.temporal_operators = []
        for f in elem.findall(util.nspath_eval(
                'fes:Temporal_Capabilities/fes:TemporalOperators/fes:TemporalOperator', namespaces)):
            self.temporal_operators.append(f.attrib['name'])

        # Scalar_Capabilities
        self.scalar_comparison_operators = [f.text for f in elem.findall(util.nspath_eval(
            'fes:Scalar_Capabilities/fes:ComparisonOperators/fes:ComparisonOperator', namespaces))]

        # Conformance
        self.conformance = {}
        for f in elem.findall(util.nspath_eval('fes:Conformance/fes:Constraint', namespaces)):
            self.conformance[f.attrib.get('name')] = f.find(util.nspath_eval('ows110:DefaultValue', namespaces)).text


def setsortby(parent, propertyname, order='ASC'):
    """

    constructs a SortBy element

    Parameters
    ----------

    - parent: parent etree.Element object
    - propertyname: the ValueReference
    - order: the SortOrder (default is 'ASC')

    """

    tmp = etree.SubElement(parent, util.nspath_eval('fes:SortBy', namespaces))
    tmp2 = etree.SubElement(tmp, util.nspath_eval('fes:SortProperty', namespaces))
    etree.SubElement(tmp2, util.nspath_eval('fes:ValueReference', namespaces)).text = propertyname
    etree.SubElement(tmp2, util.nspath_eval('fes:SortOrder', namespaces)).text = order


class SortProperty(object):
    def __init__(self, propertyname, order='ASC'):
        self.propertyname = propertyname
        self.order = order.upper()
        if self.order not in ['DESC', 'ASC']:
            raise ValueError("SortOrder can only be 'ASC' or 'DESC'")

    def toXML(self):
        node0 = etree.Element(util.nspath_eval("fes:SortProperty", namespaces))
        etree.SubElement(node0, util.nspath_eval('fes:ValueReference', namespaces)).text = self.propertyname
        etree.SubElement(node0, util.nspath_eval('fes:SortOrder', namespaces)).text = self.order
        return node0


class SortBy(object):
    def __init__(self, properties):
        self.properties = properties

    def toXML(self):
        node0 = etree.Element(util.nspath_eval("fes:SortBy", namespaces))
        for prop in self.properties:
            node0.append(prop.toXML())
        return node0


class OgcExpression(object):
    def __init__(self):
        pass


class BinaryComparisonOpType(OgcExpression):
    """ Super class of all the property operation classes"""
    def __init__(self, propertyoperator, propertyname, literal, matchcase=True):
        self.propertyoperator = propertyoperator
        self.propertyname = propertyname
        self.literal = literal
        self.matchcase = matchcase

    def toXML(self):
        node0 = etree.Element(util.nspath_eval(self.propertyoperator, namespaces))
        if not self.matchcase:
            node0.set('matchCase', 'false')
        etree.SubElement(node0, util.nspath_eval('fes:ValueReference', namespaces)).text = self.propertyname
        etree.SubElement(node0, util.nspath_eval('fes:Literal', namespaces)).text = self.literal
        return node0


class PropertyIsEqualTo(BinaryComparisonOpType):
    """ PropertyIsEqualTo class"""
    def __init__(self, propertyname, literal, matchcase=True):
        BinaryComparisonOpType.__init__(self, 'fes:PropertyIsEqualTo', propertyname, literal, matchcase)


class PropertyIsNotEqualTo(BinaryComparisonOpType):
    """ PropertyIsNotEqualTo class """
    def __init__(self, propertyname, literal, matchcase=True):
        BinaryComparisonOpType.__init__(self, 'fes:PropertyIsNotEqualTo', propertyname, literal, matchcase)


class PropertyIsLessThan(BinaryComparisonOpType):
    """PropertyIsLessThan class"""
    def __init__(self, propertyname, literal, matchcase=True):
        BinaryComparisonOpType.__init__(self, 'fes:PropertyIsLessThan', propertyname, literal, matchcase)


class PropertyIsGreaterThan(BinaryComparisonOpType):
    """PropertyIsGreaterThan class"""
    def __init__(self, propertyname, literal, matchcase=True):
        BinaryComparisonOpType.__init__(self, 'fes:PropertyIsGreaterThan', propertyname, literal, matchcase)


class PropertyIsLessThanOrEqualTo(BinaryComparisonOpType):
    """PropertyIsLessThanOrEqualTo class"""
    def __init__(self, propertyname, literal, matchcase=True):
        BinaryComparisonOpType.__init__(self, 'fes:PropertyIsLessThanOrEqualTo', propertyname, literal, matchcase)


class PropertyIsGreaterThanOrEqualTo(BinaryComparisonOpType):
    """PropertyIsGreaterThanOrEqualTo class"""
    def __init__(self, propertyname, literal, matchcase=True):
        BinaryComparisonOpType.__init__(self, 'fes:PropertyIsGreaterThanOrEqualTo', propertyname, literal, matchcase)


class PropertyIsLike(OgcExpression):
    """PropertyIsLike class"""
    def __init__(self, propertyname, literal, escapeChar='\\', singleChar='_', wildCard='%', matchCase=True):
        self.propertyname = propertyname
        self.literal = literal
        self.escapeChar = escapeChar
        self.singleChar = singleChar
        self.wildCard = wildCard
        self.matchCase = matchCase

    def toXML(self):
        node0 = etree.Element(util.nspath_eval('fes:PropertyIsLike', namespaces))
        node0.set('wildCard', self.wildCard)
        node0.set('singleChar', self.singleChar)
        node0.set('escapeChar', self.escapeChar)
        if not self.matchCase:
            node0.set('matchCase', 'false')
        etree.SubElement(node0, util.nspath_eval('fes:ValueReference', namespaces)).text = self.propertyname
        etree.SubElement(node0, util.nspath_eval('fes:Literal', namespaces)).text = self.literal
        return node0


class PropertyIsNull(OgcExpression):
    """PropertyIsNull class"""
    def __init__(self, propertyname):
        self.propertyname = propertyname

    def toXML(self):
        node0 = etree.Element(util.nspath_eval('fes:PropertyIsNull', namespaces))
        etree.SubElement(node0, util.nspath_eval('fes:ValueReference', namespaces)).text = self.propertyname
        return node0


class PropertyIsBetween(OgcExpression):
    """PropertyIsBetween class"""
    def __init__(self, propertyname, lower, upper):
        self.propertyname = propertyname
        self.lower = lower
        self.upper = upper

    def toXML(self):
        node0 = etree.Element(util.nspath_eval('fes:PropertyIsBetween', namespaces))
        etree.SubElement(node0, util.nspath_eval('fes:ValueReference', namespaces)).text = self.propertyname
        node1 = etree.SubElement(node0, util.nspath_eval('fes:LowerBoundary', namespaces))
        etree.SubElement(node1, util.nspath_eval('fes:Literal', namespaces)).text = '%s' % self.lower
        node2 = etree.SubElement(node0, util.nspath_eval('fes:UpperBoundary', namespaces))
        etree.SubElement(node2, util.nspath_eval('fes:Literal', namespaces)).text = '%s' % self.upper
        return node0


class BBox(OgcExpression):
    """Construct a BBox, two pairs of coordinates (west-south and east-north)"""
    def __init__(self, bbox, crs=None):
        self.bbox = bbox
        self.crs = crs

    def toXML(self):
        tmp = etree.Element(util.nspath_eval('fes:BBOX', namespaces))
        etree.SubElement(tmp, util.nspath_eval('fes:ValueReference', namespaces)).text = 'ows:BoundingBox'
        tmp2 = etree.SubElement(tmp, util.nspath_eval('gml:Envelope', namespaces))
        if self.crs is not None:
            tmp2.set('srsName', self.crs)
        etree.SubElement(tmp2, util.nspath_eval('gml:lowerCorner', namespaces)).text = '{} {}'.format(
            self.bbox[0], self.bbox[1])
        etree.SubElement(tmp2, util.nspath_eval('gml:upperCorner', namespaces)).text = '{} {}'.format(
            self.bbox[2], self.bbox[3])
        return tmp


class Filter(OgcExpression):
    def __init__(self, filter):
        self.filter = filter

    def toXML(self):
        node = etree.Element(util.nspath_eval("fes:Filter", namespaces))
        node.append(self.filter.toXML())
        return node


class TopologicalOpType(OgcExpression, metaclass=ABCMeta):
    """Abstract base class for topological operators."""
    @property
    @abstractmethod
    def operation(self):
        """This is a mechanism to ensure this class is subclassed by an actual operation."""
        pass

    def __init__(self, propertyname, geometry):
        self.propertyname = propertyname
        self.geometry = geometry

    def toXML(self):
        node = etree.Element(util.nspath_eval(f"fes:{self.operation}", namespaces))
        etree.SubElement(node, util.nspath_eval("fes:ValueReference", namespaces)).text = self.propertyname
        node.append(self.geometry.toXML())

        return node


class Intersects(TopologicalOpType):
    operation = "Intersects"


class Contains(TopologicalOpType):
    operation = "Contains"


class Disjoint(TopologicalOpType):
    operation = "Disjoint"


class Within(TopologicalOpType):
    operation = "Within"


class Touches(TopologicalOpType):
    operation = "Touches"


class Overlaps(TopologicalOpType):
    operation = "Overlaps"


class Equals(TopologicalOpType):
    operation = "Equals"


# BINARY
class BinaryLogicOpType(OgcExpression):
    """ Binary Operators: And / Or """
    def __init__(self, binary_operator, operations):
        self.binary_operator = binary_operator
        try:
            assert len(operations) >= 2
            self.operations = operations
        except Exception:
            raise ValueError("Binary operations (And / Or) require a minimum of two operations to operate against")

    def toXML(self):
        node0 = etree.Element(util.nspath_eval(self.binary_operator, namespaces))
        for op in self.operations:
            node0.append(op.toXML())
        return node0


class And(BinaryLogicOpType):
    def __init__(self, operations):
        super(And, self).__init__('fes:And', operations)


class Or(BinaryLogicOpType):
    def __init__(self, operations):
        super(Or, self).__init__('fes:Or', operations)


# UNARY
class UnaryLogicOpType(OgcExpression):
    """ Unary Operator: Not """
    def __init__(self, unary_operator, operations):
        self.unary_operator = unary_operator
        self.operations = operations

    def toXML(self):
        node0 = etree.Element(util.nspath_eval(self.unary_operator, namespaces))
        for op in self.operations:
            node0.append(op.toXML())
        return node0


class Not(UnaryLogicOpType):
    def __init__(self, operations):
        super(Not, self).__init__('fes:Not', operations)
