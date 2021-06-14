from dataclasses import dataclass
from typing import Sequence
from owslib.etree import etree
from owslib import util
from owslib.namespaces import Namespaces

# default variables
def get_namespaces():
    n = Namespaces()
    ns = n.get_namespaces(["gml", "ogc", "xsd"])
    ns[None] = n.get_namespace("ogc")
    return ns


namespaces = get_namespaces()

prefix = lambda x: util.nspath_eval(x, namespaces)


@dataclass
class AbstractGMLType():
    id: str


@dataclass
class AbstractGeometryType(AbstractGMLType):
    srsName: str = None
    srsDimension: int = None
    # axisLabels: str = None
    # uomLabels: str = None

    description: str = None
    descriptionReference: str = None
    identifier: str = None
    name: str = None


@dataclass
class _PointBase:
    pos: Sequence[float]


@dataclass
class Point(AbstractGeometryType, _PointBase):
    """GML Point object."""

    def toXML(self):
        """Return `lxml.etree.Element` object."""
        node = etree.Element(prefix("gml:Point"))
        for key in ["id", "srsName"]:
            if getattr(self, key, None) is not None:
                node.set(prefix(f"gml:{key}"), getattr(self, key))

        for key in ["description", "descriptionReference", "identifier", "name"]:
            content = getattr(self, key)
            if content is not None:
                etree.SubElement(node, prefix(f"gml:{key}")).text = content

        coords = etree.SubElement(node, prefix("gml:pos"))
        coords.text = " ".join([str(c) for c in self.pos])
        for key in ["srsDimension"]:
            if getattr(self, key, None) is not None:
                node.set(prefix(f"gml:{key}"), getattr(self, key))

        return node
