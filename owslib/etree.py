# =============================================================================
# OWSLib. Copyright (C) 2005 Sean C. Gillies
#
# Contact email: sgillies@frii.com
# =============================================================================

from __future__ import (absolute_import, division, print_function)

# try to find lxml or elementtree
try:
    from lxml import etree
    from lxml.etree import ParseError
    ElementType = etree._Element
except ImportError:
    import xml.etree.ElementTree as etree
    ElementType = etree.Element
    try:
        from xml.etree.ElementTree import ParseError
    except ImportError:
        from xml.parsers.expat import ExpatError as ParseError
