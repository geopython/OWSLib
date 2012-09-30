# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2008 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@hotmail.com>
#
# Contact email: tomkralidis@hotmail.com
# =============================================================================

import re
import sys
from owslib.etree import etree
import pytz
from dateutil import parser
from datetime import datetime
import urlparse, urllib2
from urllib2 import urlopen, HTTPError, Request
from urllib2 import HTTPPasswordMgrWithDefaultRealm
from urllib2 import HTTPBasicAuthHandler
from StringIO import StringIO
import cgi
from urllib import urlencode
from owslib.namespaces import OWSLibNamespaces

ns = OWSLibNamespaces()

"""
Utility functions and classes
"""

class RereadableURL(StringIO,object):
    """ Class that acts like a combination of StringIO and url - has seek method and url headers etc """
    def __init__(self, u):
        #get url headers etc from url
        self.headers = u.headers                
        #get file like seek, read methods from StringIO
        content=u.read()
        super(RereadableURL, self).__init__(content)


class ServiceException(Exception):
    #TODO: this should go in ows common module when refactored.  
    pass

# http://stackoverflow.com/questions/6256183/combine-two-dictionaries-of-dictionaries-python
dict_union = lambda d1,d2: dict((x,(dict_union(d1.get(x,{}),d2[x]) if
  isinstance(d2.get(x),dict) else d2.get(x,d1.get(x)))) for x in
  set(d1.keys()+d2.keys()))

def openURL(url_base, data, method='Get', cookies=None, username=None, password=None):
    ''' function to open urls - wrapper around urllib2.urlopen but with additional checks for OGC service exceptions and url formatting, also handles cookies and simple user password authentication'''
    url_base.strip() 
    lastchar = url_base[-1]
    if lastchar not in ['?', '&']:
        if url_base.find('?') == -1:
            url_base = url_base + '?'
        else:
            url_base = url_base + '&'
            
    if username and password:
        # Provide login information in order to use the WMS server
        # Create an OpenerDirector with support for Basic HTTP 
        # Authentication...
        passman = HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, url_base, username, password)
        auth_handler = HTTPBasicAuthHandler(passman)
        opener = urllib2.build_opener(auth_handler)
        openit = opener.open
    else:
        # NOTE: optionally set debuglevel>0 to debug HTTP connection
        #opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=0))
        #openit = opener.open
        openit = urlopen
   
    try:
        if method == 'Post':
            req = Request(url_base, data)
            # set appropriate header if posting XML
            try:
                xml = etree.fromstring(data)
                req.add_header('Content-Type', "text/xml")
            except:
                pass
        else:
            req=Request(url_base + data)
        if cookies is not None:
            req.add_header('Cookie', cookies)
        u = openit(req)
    except HTTPError, e: #Some servers may set the http header to 400 if returning an OGC service exception or 401 if unauthorised.
        if e.code in [400, 401]:
            raise ServiceException, e.read()
        else:
            raise e
    # check for service exceptions without the http header set
    if u.info()['Content-Type'] in ['text/xml', 'application/xml']:          
        #just in case 400 headers were not set, going to have to read the xml to see if it's an exception report.
        #wrap the url stram in a extended StringIO object so it's re-readable
        u=RereadableURL(u)      
        se_xml= u.read()
        se_tree = etree.fromstring(se_xml)
        serviceException=se_tree.find('{http://www.opengis.net/ows}Exception')
        if serviceException is None:
            serviceException=se_tree.find('ServiceException')
        if serviceException is not None:
            raise ServiceException, \
            str(serviceException.text).strip()
        u.seek(0) #return cursor to start of u      
    return u

#default namespace for nspath is OWS common
OWS_NAMESPACE = 'http://www.opengis.net/ows'
def nspath(path, namespace=OWS_NAMESPACE):
    """

    Prefix the given path with the given namespace identifier.
    
    Parameters
    ----------

    - path: ElementTree API Compatible path expression
    - ns: the XML namespace URI.

    """
    if path is None:
        return -1

    # If no namespace, just return the unchanged path
    if namespace is None:
        return path

    components = []
    for component in path.split('/'):
        if component != '*':
            component = '{%s}%s' % (namespace, component)
        components.append(component)
    return '/'.join(components)

def nspath_eval(xpath, version=None):
    ''' Return an etree friendly xpath '''
    out = []
    
    if version is not None:
        c_version = ''
        for str in version.split('.'):
            c_version += str
    
    for chunks in xpath.split('/'):
        if chunks.find(':') == -1:
            out.append(chunks)
        else:
            namespace, element = chunks.split(':')
            if version is not None:
                namespace += c_version
            out.append('{%s}%s' % (ns.get_namespace(namespace), element))

    return '/'.join(out)

def testXMLAttribute(element, attribute):
    ele = testXMLValue(element, attrib=True)
    if ele is not None:
        attrib = ele.get(attribute)
        if attrib is not None:
            return attrib.strip()

    return None

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
            try:
                return val.text.strip()
            except:
                return val.text
    else:
        return None


def http_post(url=None, request=None, lang='en-US', timeout=10):
    """

    Invoke an HTTP POST request 

    Parameters
    ----------

    - url: the URL of the server
    - request: the request message
    - lang: the language
    - timeout: timeout in seconds

    """

    if url is not None:
        u = urlparse.urlsplit(url)
        r = urllib2.Request(url, request)
        r.add_header('User-Agent', 'OWSLib (https://geopython.github.com/OWSLib)')
        r.add_header('Content-type', 'text/xml')
        r.add_header('Content-length', '%d' % len(request))
        r.add_header('Accept', 'text/xml')
        r.add_header('Accept-Language', lang)
        r.add_header('Accept-Encoding', 'gzip,deflate')
        r.add_header('Host', u.netloc)

        try:
            up = urllib2.urlopen(r,timeout=timeout);
        except TypeError:
            import socket
            socket.setdefaulttimeout(timeout)
            up = urllib2.urlopen(r)

        ui = up.info()  # headers
        response = up.read()
        up.close()

        # check if response is gzip compressed
        if ui.has_key('Content-Encoding'):
            if ui['Content-Encoding'] == 'gzip':  # uncompress response
                import gzip
                cds = StringIO(response)
                gz = gzip.GzipFile(fileobj=cds)
                response = gz.read()

        return response

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

    doc = etree.parse(StringIO(xml))
    return xsd2.validate(doc)

def xmltag_split(tag):
    ''' Return XML element bare tag name (without prefix) '''
    try:
        return tag.split('}')[1]
    except:
        return tag

def getNamespace(element):
    ''' Utility method to extract the namespace from an XML element tag encoded as {namespace}localname. '''
    if element.tag[0]=='{':
        return element.tag[1:].split("}")[0]
    else:
        return ""

def build_get_url(base_url, params):
    ''' Utility function to build a full HTTP GET URL from the service base URL and a dictionary of HTTP parameters. '''
    
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
    '''Utility function to print to standard output a generic object with all its attributes.'''
    
    print "%s %s : %s" % (prefix, obj.__class__, obj.__dict__)
    
def getTypedValue(type, value):
    ''' Utility function to cast a string value to the appropriate XSD type. '''
    
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

def extract_time(element):
    ''' return a datetime object based on a gml text string 

        ex:
        <gml:beginPosition>2006-07-27T21:10:00Z</gml:beginPosition>
        <gml:endPosition indeterminatePosition="now"/>

        If there happens to be a strange element with both attributes and text,
        use the text.
        ex:  <gml:beginPosition indeterminatePosition="now">2006-07-27T21:10:00Z</gml:beginPosition>
        Would be 2006-07-27T21:10:00Z, not 'now'

    '''
    if element is None:
        return None

    try:            
        dt = parser.parse(element.text)
    except Exception:
        att = testXMLAttribute(element, 'indeterminatePosition')
        if att and att == 'now':
            dt = datetime.utcnow()
            dt.replace(tzinfo=pytz.utc)
        else:
            dt = None
    return dt

def extract_xml_list(elements):
    """
        Some people don't have seperate tags for their keywords and seperate them with
        a newline.  This will extract out all of the  keywords correctly.
    """
    keywords = [re.split(r'[\n\r]+',f.text) for f in elements if f.text]
    flattened = [item.strip() for sublist in keywords for item in sublist]
    remove_blank = filter(None, flattened)
    return remove_blank

def setrootelement(element, nsmap=None):
        if etree.__name__ == 'lxml.etree':  # apply nsmap
            return etree.Element(nspath_eval(element), nsmap=nsmap)
        else:
            e = etree.Element(nspath_eval(element))
            if nsmap is not None:
                for m in nsmap:
                    e.set('xmlns:%s' % m, nsmap[m])
            return e
