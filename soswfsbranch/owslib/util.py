# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2008 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@hotmail.com>
#
# Contact email: tomkralidis@hotmail.com
# =============================================================================

"""
Utility functions
"""

#default namespace
OWS_NAMESPACE = 'http://www.opengis.net/ows/1.1'

def nspath(path, ns=OWS_NAMESPACE):
    """
    Prefix the given path with the given namespace identifier.
    
    Parameters
    ----------
    path : string
        ElementTree API Compatible path expression

    ns : string
        The XML namespace.
    """

    if ns is None or path is None:
        return -1

    components = []
    for component in path.split("/"):
        if component != '*':
            component = "{%s}%s" % (ns, component)
        components.append(component)
    return "/".join(components)

def testXMLValue(val, attrib=False):
    """
    Test that the XML value exists, return val.text, else return None

    Parameters
    ----------
    val: the value to be tested
    """
    if val is not None:
        if attrib == True:
            return val
        else:
            return val.text
    else:
        return None

