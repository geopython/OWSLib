###########################################################################
# Module containing generic utility functions used by wps.py,
# which could also be useful to other modules.
###########################################################################

import cgi
from etree import etree
from urllib import urlencode

def build_get_url(base_url, params):
    """
    Utility function to build a full HTTP GET URL from the service base URL and a dictionary of HTTP parameters.
    """
    
    qs = []
    if base_url.find('?') != -1:
        qs = cgi.parse_qsl(base_url.split('?')[1])

    pars = [x[0] for x in qs]

    for key,value in params.iteritems():
        if key not in pars:
            qs.append( (key,value) )

    urlqs = urlencode(tuple(qs))
    return base_url.split('?')[0] + '?' + urlqs

def dump(obj, prefix=''):
    print "%s %s : %s" % (prefix, obj.__class__, obj.__dict__)
    
def getTypedValue(type, value):
    """
    Utility function to cast a string value to the appropriate XSD type
    """
    if type=='boolean':
       return bool(value)
    elif type=='integer':
       return int(value)
    elif type=='float':
        return float(value)
    elif type=='string':
        return str(value)
    else:
        return value # no type casting
    
def parseText(element):
    """
    Utility function to return the text of an XML element, or None if the element is not found.
    """    
    if element is not None:
        return element.text
    else:
        return None
