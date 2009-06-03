#!/usr/bin/python
# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2008 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@hotmail.com>
#
# Contact email: tomkralidis@hotmail.com
# =============================================================================

from lxml import etree
import urlparse, httplib, StringIO

"""
Utility functions
"""

def nspath(path, ns=None):
    """

    Prefix the given path with the given namespace identifier.
    
    Parameters
    ----------

    - path: ElementTree API Compatible path expression
    - ns: the XML namespace URI.

    """

    if ns is None or path is None:
        return -1

    components = []
    for component in path.split('/'):
        if component != '*':
            component = '{%s}%s' % (ns, component)
        components.append(component)
    return '/'.join(components)

def testXMLValue(val, attrib=False):
    """

    Test that the XML value exists, return val.text, else return None

    Parameters
    ----------

    - val: the value to be tested

    """

    if val is not None:
        if attrib == True:
            return val
        else:
            return val.text
    else:
        return None


def http_post(url=None, request=None, lang='en-US'):
    """

    Invoke an HTTP POST request 

    Parameters
    ----------

    - url: the URL of the server
    - request: the request message
    - lang: the language

    """

    if url is not None:
        u = urlparse.urlsplit(url)
        h = httplib.HTTP(u.netloc)
        h.putrequest('POST', u.path)
        h.putheader('User-Agent', 'OWSLib (http://trac.gispython.org/lab/wiki/OwsLib)')
        h.putheader('Content-type', 'text/xml')
        h.putheader('Content-length', '%d' % len(request))
        h.putheader('Accept', 'text/xml')
        h.putheader('Accept-Language', lang)
        h.putheader('Accept-Encoding', 'gzip,deflate')
        h.putheader('Host', u.netloc)
        h.endheaders()
        h.send(request)
        reply, msg, hdrs = h.getreply()

        return h.getfile().read()

def xml2string(xml):
    """

    Return a string of XML object

    Parameters
    ----------

    - xml: xml string

    """
    return '<?xml version="1.0" encoding="ISO-8859-1" standalone="no"?>\n' + xml

def xmlvalid(xml, xsd):
    """

    Test whether an XML document is valid

    Parameters
    ----------

    - xml: XML content
    - xsd: pointer to XML Schema (local file path or URL)

    """

    xsd1 = etree.parse(xsd)
    xsd2 = etree.XMLSchema(xsd1)

    doc = etree.parse(StringIO.StringIO(xml))
    return xsd2.validate(doc)
