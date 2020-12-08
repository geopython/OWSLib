# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2008 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

import os
import sys
from collections import OrderedDict
from dateutil import parser
from datetime import datetime, timedelta
import pytz
from owslib.etree import etree, ParseError
from owslib.namespaces import Namespaces
from urllib.parse import urlsplit, urlencode, urlparse, parse_qs, urlunparse, parse_qsl
import copy

from io import StringIO, BytesIO

import re
from copy import deepcopy
import warnings
import requests
import codecs

"""
Utility functions and classes
"""


class ServiceException(Exception):
    # TODO: this should go in ows common module when refactored.
    pass


# http://stackoverflow.com/questions/6256183/combine-two-dictionaries-of-dictionaries-python
def dict_union(d1, d2):
    return dict((x, (dict_union(d1.get(x, {}), d2[x]) if isinstance(d2.get(x), dict) else d2.get(x, d1.get(x))))
                for x in set(list(d1.keys()) + list(d2.keys())))


# Infinite DateTimes for Python.  Used in SWE 2.0 and other OGC specs as "INF" and "-INF"
class InfiniteDateTime(object):
    def __lt__(self, other):
        return False

    def __gt__(self, other):
        return True

    def timetuple(self):
        return tuple()


class NegativeInfiniteDateTime(object):
    def __lt__(self, other):
        return True

    def __gt__(self, other):
        return False

    def timetuple(self):
        return tuple()


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def format_string(prop_string):
    """
        Formats a property string to remove spaces and go from CamelCase to pep8
        from: http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-camel-case
    """
    if prop_string is None:
        return ''
    st_r = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', prop_string)
    st_r = st_r.replace(' ', '')
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', st_r).lower()


def xml_to_dict(root, prefix=None, depth=1, diction=None):
    """
        Recursively iterates through an xml element to convert each element in the tree to a (key,val).
        Where key is the element tag and val is the inner-text of the element.
        Note that this recursively go through the tree until the depth specified.

        Parameters
        ===========
        :root - root xml element, starting point of iteration
        :prefix - a string to prepend to the resulting key (optional)
        :depth - the number of depths to process in the tree (optional)
        :diction - the dictionary to insert the (tag,text) pairs into (optional)

        Return
        =======
        Dictionary of (key,value); where key is the element tag stripped of namespace and cleaned up to be pep8 and
        value is the inner-text of the element. Note that duplicate elements will be replaced by the last element of the
        same tag in the tree.
    """
    ret = diction if diction is not None else dict()
    for child in root:
        val = testXMLValue(child)
        # skip values that are empty or None
        if val is None or val == '':
            if depth > 1:
                ret = xml_to_dict(child, prefix=prefix, depth=(depth - 1), diction=ret)
            continue

        key = format_string(child.tag.split('}')[-1])

        if prefix is not None:
            key = prefix + key

        ret[key] = val
        if depth > 1:
            ret = xml_to_dict(child, prefix=prefix, depth=(depth - 1), diction=ret)

    return ret


class ResponseWrapper(object):
    """
    Return object type from openURL.

    Provides a thin shim around requests response object to maintain code compatibility.
    """
    def __init__(self, response):
        self._response = response

    def info(self):
        return self._response.headers

    def read(self):
        return self._response.content

    def geturl(self):
        return self._response.url.replace('&&', '&')

    # @TODO: __getattribute__ for poking at response


def openURL(url_base, data=None, method='Get', cookies=None, username=None, password=None, timeout=30, headers=None,
            verify=True, cert=None, auth=None):
    """
    Function to open URLs.

    Uses requests library but with additional checks for OGC service exceptions and url formatting.
    Also handles cookies and simple user password authentication.

    :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
    :param verify: (optional) whether the SSL cert will be verified. A CA_BUNDLE path can also be provided.
                   Defaults to ``True``.
    :param cert: (optional) A file with a client side certificate for SSL authentication
                 to send with the :class:`Request`.
    :param auth: Instance of owslib.util.Authentication
    """

    headers = headers if headers is not None else {}
    rkwargs = {}

    rkwargs['timeout'] = timeout

    if auth:
        if username:
            auth.username = username
        if password:
            auth.password = password
        if cert:
            auth.cert = cert
        verify = verify and auth.verify
    else:
        auth = Authentication(username, password, cert, verify)
    if auth.username and auth.password:
        rkwargs['auth'] = (auth.username, auth.password)
    rkwargs['cert'] = auth.cert
    rkwargs['verify'] = verify

    # FIXUP for WFS in particular, remove xml style namespace
    # @TODO does this belong here?
    method = method.split("}")[-1]

    if method.lower() == 'post':
        try:
            etree.fromstring(data)
            headers['Content-Type'] = 'text/xml'
        except (ParseError, UnicodeEncodeError):
            pass

        rkwargs['data'] = data

    elif method.lower() == 'get':
        rkwargs['params'] = data

    else:
        raise ValueError("Unknown method ('%s'), expected 'get' or 'post'" % method)

    if cookies is not None:
        rkwargs['cookies'] = cookies

    req = requests.request(method.upper(), url_base, headers=headers, **rkwargs)

    if req.status_code in [400, 401]:
        raise ServiceException(req.text)

    if req.status_code in [404, 500, 502, 503, 504]:    # add more if needed
        req.raise_for_status()

    # check for service exceptions without the http header set
    if 'Content-Type' in req.headers and \
            req.headers['Content-Type'] in ['text/xml', 'application/xml', 'application/vnd.ogc.se_xml']:
        # just in case 400 headers were not set, going to have to read the xml to see if it's an exception report.
        se_tree = etree.fromstring(req.content)

        # to handle the variety of namespaces and terms across services
        # and versions, especially for "legacy" responses like WMS 1.3.0
        possible_errors = [
            '{http://www.opengis.net/ows}Exception',
            '{http://www.opengis.net/ows/1.1}Exception',
            '{http://www.opengis.net/ogc}ServiceException',
            'ServiceException'
        ]

        for possible_error in possible_errors:
            serviceException = se_tree.find(possible_error)
            if serviceException is not None:
                # and we need to deal with some message nesting
                raise ServiceException('\n'.join([t.strip() for t in serviceException.itertext() if t.strip()]))

    return ResponseWrapper(req)


# default namespace for nspath is OWS common
OWS_NAMESPACE = 'http://www.opengis.net/ows/1.1'


def nspath(path, ns=OWS_NAMESPACE):

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


def nspath_eval(xpath, namespaces):
    ''' Return an etree friendly xpath '''
    out = []
    for chunks in xpath.split('/'):
        namespace, element = chunks.split(':')
        out.append('{%s}%s' % (namespaces[namespace], element))
    return '/'.join(out)


def cleanup_namespaces(element):
    """ Remove unused namespaces from an element """
    if etree.__name__ == 'lxml.etree':
        etree.cleanup_namespaces(element)
        return element
    else:
        return etree.fromstring(etree.tostring(element))


def add_namespaces(root, ns_keys):
    if isinstance(ns_keys, str):
        ns_keys = [ns_keys]

    namespaces = Namespaces()

    ns_keys = [(x, namespaces.get_namespace(x)) for x in ns_keys]

    if etree.__name__ != 'lxml.etree':
        # We can just add more namespaces when not using lxml.
        # We can't re-add an existing namespaces.  Get a list of current
        # namespaces in use
        existing_namespaces = set()
        for elem in root.iter():
            if elem.tag[0] == "{":
                uri, tag = elem.tag[1:].split("}")
                existing_namespaces.add(namespaces.get_namespace_from_url(uri))
        for key, link in ns_keys:
            if link is not None and key not in existing_namespaces:
                root.set("xmlns:%s" % key, link)
        return root
    else:
        # lxml does not support setting xmlns attributes
        # Update the elements nsmap with new namespaces
        new_map = root.nsmap
        for key, link in ns_keys:
            if link is not None:
                new_map[key] = link
        # Recreate the root element with updated nsmap
        new_root = etree.Element(root.tag, nsmap=new_map)
        # Carry over attributes
        for a, v in list(root.items()):
            new_root.set(a, v)
        # Carry over children
        for child in root:
            new_root.append(deepcopy(child))
        return new_root


def getXMLInteger(elem, tag):
    """
    Return the text within the named tag as an integer.

    Raises an exception if the tag cannot be found or if its textual
    value cannot be converted to an integer.

    Parameters
    ----------

    - elem: the element to search within
    - tag: the name of the tag to look for

    """
    e = elem.find(tag)
    if e is None:
        raise ValueError('Missing %s in %s' % (tag, elem))
    return int(e.text.strip())


def testXMLValue(val, attrib=False):
    """

    Test that the XML value exists, return val.text, else return None

    Parameters
    ----------

    - val: the value to be tested

    """

    if val is not None:
        if attrib:
            return val.strip()
        elif val.text:
            return val.text.strip()
        else:
            return None
    else:
        return None


def testXMLAttribute(element, attribute):
    """

    Test that the XML element and attribute exist, return attribute's value, else return None

    Parameters
    ----------

    - element: the element containing the attribute
    - attribute: the attribute name

    """
    if element is not None:
        return element.get(attribute)

    return None


def http_post(url=None, request=None, lang='en-US', timeout=10, username=None, password=None, auth=None):
    """

    Invoke an HTTP POST request

    Parameters
    ----------

    - url: the URL of the server
    - request: the request message
    - lang: the language
    - timeout: timeout in seconds

    """

    if url is None:
        raise ValueError("URL required")

    u = urlsplit(url)

    headers = {
        'User-Agent': 'OWSLib (https://geopython.github.io/OWSLib)',
        'Content-type': 'text/xml',
        'Accept': 'text/xml',
        'Accept-Language': lang,
        'Accept-Encoding': 'gzip,deflate',
        'Host': u.netloc,
    }

    rkwargs = {}

    if auth:
        if username:
            auth.username = username
        if password:
            auth.password = password
    else:
        auth = Authentication(username, password)
    if auth.username is not None and auth.password is not None:
        rkwargs['auth'] = (auth.username, auth.password)
    rkwargs['verify'] = auth.verify
    rkwargs['cert'] = auth.cert

    up = requests.post(url, request, headers=headers, **rkwargs)
    return up.content


def http_get(*args, **kwargs):
    # Copy input kwargs so the dict can be modified
    rkwargs = copy.deepcopy(kwargs)

    # Use Authentication instance if provided, else create one
    auth = rkwargs.pop('auth', None)
    if auth is not None:
        if isinstance(auth, (tuple, list)):
            auth = Authentication(*auth)
    else:
        auth = Authentication()

    # Populate values with other arguments supplied
    if 'username' in rkwargs:
        auth.username = rkwargs.pop('username')
    if 'password' in rkwargs:
        auth.password = rkwargs.pop('password')
    if 'cert' in rkwargs:
        auth.cert = rkwargs.pop('cert')
    if 'verify' in rkwargs:
        auth.verify = rkwargs.pop('verify')

    # Build keyword args for call to requests.get()
    if auth.username and auth.password:
        rkwargs.setdefault('auth', (auth.username, auth.password))
    else:
        rkwargs.setdefault('auth', None)
    rkwargs.setdefault('cert', rkwargs.get('cert'))
    rkwargs.setdefault('verify', rkwargs.get('verify', True))
    return requests.get(*args, **rkwargs)


def element_to_string(element, encoding=None, xml_declaration=False):
    """
    Returns a string from a XML object

    Parameters
    ----------
    - element: etree Element
    - encoding (optional): encoding in string form. 'utf-8', 'ISO-8859-1', etc.
    - xml_declaration (optional): whether to include xml declaration

    """

    output = None

    if encoding is None:
        encoding = "ISO-8859-1"

    if etree.__name__ == 'lxml.etree':
        if xml_declaration:
            if encoding in ['unicode', 'utf-8']:
                output = '<?xml version="1.0" encoding="utf-8" standalone="no"?>\n{}'.format(
                    etree.tostring(element, encoding='unicode'))
            else:
                output = etree.tostring(element, encoding=encoding, xml_declaration=True)
        else:
            output = etree.tostring(element)
    else:
        if xml_declaration:
            output = '<?xml version="1.0" encoding="{}" standalone="no"?>\n{}'.format(
                encoding, etree.tostring(element, encoding=encoding))
        else:
            output = etree.tostring(element)

    return output


def xml2string(xml):
    """

    Return a string of XML object

    Parameters
    ----------

    - xml: xml string

    """
    warnings.warn("DEPRECIATION WARNING!  You should now use the 'element_to_string' method \
                   The 'xml2string' method will be removed in a future version of OWSLib.")
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
    except Exception:
        return tag


def getNamespace(element):
    ''' Utility method to extract the namespace from an XML element tag encoded as {namespace}localname. '''
    if element.tag[0] == '{':
        return element.tag[1:].split("}")[0]
    else:
        return ""


def build_get_url(base_url, params, overwrite=False):
    ''' Utility function to build a full HTTP GET URL from the service base URL and a dictionary of HTTP parameters.

    TODO: handle parameters case-insensitive?

    @param overwrite: boolean flag to allow overwrite of parameters of the base_url (default: False)
    '''

    qs_base = []
    if base_url.find('?') != -1:
        qs_base = parse_qsl(base_url.split('?')[1])

    qs_params = []
    for key, value in list(params.items()):
        qs_params.append((key, value))

    qs = qs_add = []
    if overwrite is True:
        # all params and additional base
        qs = qs_params
        qs_add = qs_base
    else:
        # all base and additional params
        qs = qs_base
        qs_add = qs_params

    pars = [x[0] for x in qs]

    for key, value in qs_add:
        if key not in pars:
            qs.append((key, value))

    urlqs = urlencode(tuple(qs))
    return base_url.split('?')[0] + '?' + urlqs


def dump(obj, prefix=''):
    '''Utility function to print to standard output a generic object with all its attributes.'''

    print(("{} {}.{} : {}".format(prefix, obj.__module__, obj.__class__.__name__, obj.__dict__)))


def getTypedValue(data_type, value):
    '''Utility function to cast a string value to the appropriate XSD type. '''

    # If the default value is empty
    if value is None:
        return

    if data_type == 'boolean':
        return True if value.lower() == 'true' else False
    elif data_type == 'integer':
        return int(value)
    elif data_type == 'float':
        return float(value)
    elif data_type == 'string':
        return str(value)
    else:
        return value  # no type casting


def extract_time(element):
    ''' return a datetime object based on a gml text string

ex:
<gml:beginPosition>2006-07-27T21:10:00Z</gml:beginPosition>
<gml:endPosition indeterminatePosition="now"/>

If there happens to be a strange element with both attributes and text,
use the text.
ex: <gml:beginPosition indeterminatePosition="now">2006-07-27T21:10:00Z</gml:beginPosition>
Would be 2006-07-27T21:10:00Z, not 'now'

'''
    if element is None:
        return None

    try:
        dt = parser.parse(element.text)
    except Exception:
        att = testXMLValue(element.attrib.get('indeterminatePosition'), True)
        if att and att == 'now':
            dt = datetime.utcnow()
            dt.replace(tzinfo=pytz.utc)
        else:
            dt = None
    return dt


def extract_xml_list(elements):
    """
Some people don't have seperate tags for their keywords and seperate them with
a newline. This will extract out all of the keywords correctly.
"""
    keywords = (re.split(r'[\n\r]+', f.text) for f in elements if f.text)
    flattened = (item.strip() for sublist in keywords for item in sublist)
    remove_blank = [_f for _f in flattened if _f]
    return remove_blank


def strip_bom(raw_text):
    """ return the raw (assumed) xml response without the BOM
    """
    boms = [
        # utf-8
        codecs.BOM_UTF8,
        # utf-16
        codecs.BOM,
        codecs.BOM_BE,
        codecs.BOM_LE,
        codecs.BOM_UTF16,
        codecs.BOM_UTF16_LE,
        codecs.BOM_UTF16_BE,
        # utf-32
        codecs.BOM_UTF32,
        codecs.BOM_UTF32_LE,
        codecs.BOM_UTF32_BE
    ]

    if isinstance(raw_text, bytes):
        for bom in boms:
            if raw_text.startswith(bom):
                return raw_text[len(bom):]
    return raw_text


def clean_ows_url(url):
    """
    clean an OWS URL of basic service elements

    source: https://stackoverflow.com/a/11640565
    """

    if url is None or not url.startswith('http'):
        return url

    filtered_kvp = {}
    basic_service_elements = ('service', 'version', 'request')

    parsed = urlparse(url)
    qd = parse_qs(parsed.query, keep_blank_values=True)

    for key, value in list(qd.items()):
        if key.lower() not in basic_service_elements:
            filtered_kvp[key] = value

    newurl = urlunparse([
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        urlencode(filtered_kvp, doseq=True),
        parsed.fragment
    ])

    return newurl


def bind_url(url):
    """binds an HTTP GET query string endpiont"""
    if url.find('?') == -1:  # like http://host/wms
        binder = '?'

    # if like http://host/wms?foo=bar& or http://host/wms?foo=bar
    if url.find('=') != -1:
        if url.find('&', -1) != -1:  # like http://host/wms?foo=bar&
            binder = ''
        else:  # like http://host/wms?foo=bar
            binder = '&'

    # if like http://host/wms?foo
    if url.find('?') != -1:
        if url.find('?', -1) != -1:  # like http://host/wms?
            binder = ''
        elif url.find('&', -1) == -1:  # like http://host/wms?foo=bar
            binder = '&'
    return '%s%s' % (url, binder)


import logging
# Null logging handler
NullHandler = logging.NullHandler

log = logging.getLogger('owslib')
log.addHandler(NullHandler())


def which_etree():
    """decipher which etree library is being used by OWSLib"""

    which_etree = None

    if 'lxml' in etree.__file__:
        which_etree = 'lxml.etree'
    elif 'xml/etree' in etree.__file__:
        which_etree = 'xml.etree'
    elif 'elementree' in etree.__file__:
        which_etree = 'elementtree.ElementTree'

    return which_etree


def findall(root, xpath, attribute_name=None, attribute_value=None):
    """Find elements recursively from given root element based on
    xpath and possibly given attribute

    :param root: Element root element where to start search
    :param xpath: xpath defintion, like {http://foo/bar/namespace}ElementName
    :param attribute_name: name of possible attribute of given element
    :param attribute_value: value of the attribute
    :return: list of elements or None
    """

    found_elements = []

    if attribute_name is not None and attribute_value is not None:
        xpath = '%s[@%s="%s"]' % (xpath, attribute_name, attribute_value)
    found_elements = root.findall('.//' + xpath)

    if found_elements == []:
        found_elements = None
    return found_elements


def datetime_from_iso(iso):
    """returns a datetime object from dates in the format 2001-07-01T00:00:00Z or 2001-07-01T00:00:00.000Z """
    try:
        iso_datetime = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        iso_datetime = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S.%fZ")
    return iso_datetime


def datetime_from_ansi(ansi):
    """Converts an ansiDate (expressed as a number = the nuber of days since the datum origin of ansi)
    to a python datetime object.
    """

    datumOrigin = datetime(1600, 12, 31, 0, 0, 0)

    return datumOrigin + timedelta(ansi)


def is_number(s):
    """simple helper to test if value is number as requests with numbers don't
    need quote marks
    """
    try:
        float(s)
        return True
    except ValueError:
        return False


def makeString(value):
    # using repr unconditionally breaks things in some circumstances if a
    # value is already a string
    if type(value) is not str:
        sval = repr(value)
    else:
        sval = value
    return sval


def param_list_to_url_string(param_list, param_name):
    """Converts list of tuples for certain WCS GetCoverage keyword arguments
    (subsets, resolutions, sizes) to a url-encoded string
    """
    string = ''
    for param in param_list:
        if len(param) > 2:
            if not is_number(param[1]):
                string += "&" + urlencode({param_name: param[0] + '("' + makeString(param[1]) + '","' + makeString(param[2]) + '")'})  # noqa
            else:
                string += "&" + urlencode({param_name: param[0] + "(" + makeString(param[1]) + "," + makeString(param[2]) + ")"})  # noqa
        else:
            if not is_number(param[1]):
                string += "&" + urlencode({param_name: param[0] + '("' + makeString(param[1]) + '")'})  # noqa
            else:
                string += "&" + urlencode({param_name: param[0] + "(" + makeString(param[1]) + ")"})  # noqa
    return string


def is_vector_grid(grid_elem):
    pass


class Authentication(object):

    _USERNAME = None
    _PASSWORD = None
    _CERT = None
    _VERIFY = None

    def __init__(self, username=None, password=None,
                 cert=None, verify=True, shared=False):
        '''
        :param str username=None: Username for basic authentication, None for
            unauthenticated access (or if using cert/verify)
        :param str password=None: Password for basic authentication, None for
            unauthenticated access (or if using cert/verify)
        :param cert=None: Either a str (path to a combined certificate/key) or
            tuple/list of paths (certificate, key). If supplied, the target
            files must exist.
        :param verify=True: Either a bool (verify SSL certificates, use system
            CA bundle) or str (path to a specific CA bundle). If a str, the
            target file must exist.
        :param bool shared=False: Set to True to make the values be class-level
            attributes (shared among instances where shared=True) instead of
            instance-level (shared=False, default)
        '''
        self.shared = shared
        self.username = username
        self.password = password
        self.cert = cert
        self.verify = verify

    @property
    def username(self):
        if self.shared:
            return self._USERNAME
        return self._username

    @username.setter
    def username(self, value):
        if value is None:
            pass
        elif not isinstance(value, str):
            raise TypeError('Value for "username" must be a str')
        if self.shared:
            self.__class__._USERNAME = value
        else:
            self._username = value

    @property
    def password(self):
        if self.shared:
            return self._PASSWORD
        return self._password

    @password.setter
    def password(self, value):
        if value is None:
            pass
        elif not isinstance(value, str):
            raise TypeError('Value for "password" must be a str')
        if self.shared:
            self.__class__._PASSWORD = value
        else:
            self._password = value

    @property
    def cert(self):
        if self.shared:
            return self._CERT
        return self._cert

    @cert.setter
    def cert(self, certificate, key=None):
        error = 'Value for "cert" must be a str path to a file or list/tuple of str paths'
        value = None
        if certificate is None:
            value = certificate
        elif isinstance(certificate, (list, tuple)):
            for _ in certificate:
                if not isinstance(_, str):
                    raise TypeError(error)
                os.stat(_)  # Raises OSError/FileNotFoundError if missing
            # Both paths supplied as same argument
            value = tuple(certificate)
        elif isinstance(certificate, str):
            os.stat(certificate)  # Raises OSError/FileNotFoundError if missing
            if isinstance(key, str):
                # Separate files for certificate and key
                value = (certificate, key)
            else:
                # Assume combined file of both certificate and key
                value = certificate
        else:
            raise TypeError(error)
        if self.shared:
            self.__class__._CERT = value
        else:
            self._cert = value

    @property
    def verify(self):
        if self.shared:
            return self._VERIFY
        return self._verify

    @verify.setter
    def verify(self, value):
        if value is None:
            pass  # Passthrough when clearing the value
        elif not isinstance(value, (bool, str)):
            raise TypeError(
                'Value for "verify" must a bool or str path to a file')
        elif isinstance(value, str):
            os.stat(value)  # Raises OSError/FileNotFoundError if missing
        if self.shared:
            self.__class__._VERIFY = value
        else:
            self._verify = value

    @property
    def urlopen_kwargs(self):
        return {
            'username': self.username,
            'password': self.password,
            'cert': self.cert,
            'verify': self.verify
        }

    def __repr__(self, *args, **kwargs):
        return '<{} shared={} username={} password={} cert={} verify={}>'.format(
            self.__class__.__name__, self.shared, self.username, self.password, self.cert, self.verify)
