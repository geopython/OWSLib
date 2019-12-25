from urllib.parse import urlencode, parse_qsl

from owslib.etree import etree
from owslib.util import strip_bom, Authentication, openURL


class WMSCapabilitiesReader(object):
    """Read and parse capabilities document into a lxml.etree infoset
    """

    def __init__(self, version='1.1.1', url=None, un=None, pw=None, headers=None, auth=None):
        """Initialize"""
        self.version = version
        self._infoset = None
        self.url = url
        if auth:
            if un:
                auth.username = un
            if pw:
                auth.password = pw
        self.headers = headers
        self.request = None
        self.auth = auth or Authentication(un, pw)

        # if self.username and self.password:
        #     # Provide login information in order to use the WMS server
        #     # Create an OpenerDirector with support for Basic HTTP
        #     # Authentication...
        #     passman = HTTPPasswordMgrWithDefaultRealm()
        #     passman.add_password(None, self.url, self.username, self.password)
        #     auth_handler = HTTPBasicAuthHandler(passman)
        #     opener = build_opener(auth_handler)
        #     self._open = opener.open

    def capabilities_url(self, service_url):
        """Return a capabilities url
        """
        qs = []
        if service_url.find('?') != -1:
            qs = parse_qsl(service_url.split('?')[1])

        params = [x[0] for x in qs]

        if 'service' not in params:
            qs.append(('service', 'WMS'))
        if 'request' not in params:
            qs.append(('request', 'GetCapabilities'))
        if 'version' not in params:
            qs.append(('version', self.version))

        urlqs = urlencode(tuple(qs))
        return service_url.split('?')[0] + '?' + urlqs

    def read(self, service_url, timeout=30):
        """Get and parse a WMS capabilities document, returning an
        elementtree instance

        service_url is the base url, to which is appended the service,
        version, and request parameters
        """
        self.request = self.capabilities_url(service_url)

        # now split it up again to use the generic openURL function...
        spliturl = self.request.split('?')
        u = openURL(spliturl[0], spliturl[1], method='Get',
                    timeout=timeout, headers=self.headers, auth=self.auth)

        raw_text = strip_bom(u.read())
        return etree.fromstring(raw_text)

    def readString(self, st):
        """Parse a WMS capabilities document, returning an elementtree instance.

        string should be an XML capabilities document
        """
        if not isinstance(st, str) and not isinstance(st, bytes):
            raise ValueError("String must be of type string or bytes, not %s" % type(st))
        raw_text = strip_bom(st)
        return etree.fromstring(raw_text)


class AbstractContentMetadata(object):

    def __init__(self, auth=None):
        self.auth = auth or Authentication()

    def get_metadata(self):
        return [m['metadata'] for m in self.metadataUrls if m.get('metadata', None) is not None]
