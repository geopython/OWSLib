import cgi
from owslib.etree import etree
from owslib.util import openURL

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode



class WFSCapabilitiesReader(object):
    """Read and parse capabilities document into a lxml.etree infoset
    """

    def __init__(self, version='1.0', username=None, password=None):
        """Initialize"""
        self.version = version
        self.username = username
        self.password = password
        self._infoset = None

    def capabilities_url(self, service_url):
        """Return a capabilities url
        """
        qs = []
        if service_url.find('?') != -1:
            qs = cgi.parse_qsl(service_url.split('?')[1])

        params = [x[0] for x in qs]

        if 'service' not in params:
            qs.append(('service', 'WFS'))
        if 'request' not in params:
            qs.append(('request', 'GetCapabilities'))
        if 'version' not in params:
            qs.append(('version', self.version))

        urlqs = urlencode(tuple(qs))
        return service_url.split('?')[0] + '?' + urlqs

    def read(self, url, timeout=30):
        """Get and parse a WFS capabilities document, returning an
        instance of WFSCapabilitiesInfoset

        Parameters
        ----------
        url : string
            The URL to the WFS capabilities document.
        timeout : number
            A timeout value (in seconds) for the request.
        """
        request = self.capabilities_url(url)
        u = openURL(request, timeout=timeout,
                    username=self.username, password=self.password)
        return etree.fromstring(u.read())

    def readString(self, st):
        """Parse a WFS capabilities document, returning an
        instance of WFSCapabilitiesInfoset

        string should be an XML capabilities document
        """
        if not isinstance(st, str) and not isinstance(st, bytes):
            raise ValueError("String must be of type string or bytes, not %s" % type(st))
        return etree.fromstring(st)


class AbstractContentMetadata(object):
    def get_metadata(self):
        return [m['metadata'] for m in self.metadataUrls if m.get('metadata', None) is not None]