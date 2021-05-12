from urllib.parse import quote, urlencode
from owslib.util import Authentication, openURL

class ProcessCoverages(object):
    """Sends the encoded WCPS query to WCS server by using "ProcessCoverage" operation
    """

    def __init__(self, version=None, cookies=None, auth=None, headers=None):
    
        self.version = version
        self._infoset = None
        self.cookies = cookies
        self.headers = headers
        self.auth = auth or Authentication()
        
     #get/kvp encoding implementation
    def getKVPUrl(self, service_url, query):
        """Return a process coverage url encoded in get/kvp
        @type service_url: string
        @param service_url: base url of WCS service
        @rtype: string
        @return: processCoverage URL
        """
        url = []
        url.append(('service', 'WCS'))
        url.append(('request', 'ProcessCoverages'))
        url.append(('version', '2.0'))
        url.append(('query', ""))
        
        urlqs = urlencode(tuple(url))
        
        return service_url.split('?')[0] + '?' + urlqs + query


    def process(self, service_url, query):
        """Get and process a WCPS query result, returning the
        result in encode() format

        @type service_url: string
        @param service_url: The base url, to which is appended the service,
        version, and request parameters
        @param query: WCPS that needs to be processed
        @rtype: response content
        @return: encoded coverage
        """
        query = quote(query) # encoding the query parameter
        request = ProcessCoverages.getKVPUrl(self, service_url=service_url, query=query)
        u = openURL(request, timeout=self.timeout, cookies=self.cookies, auth=self.auth, headers=self.headers)
        return u.read()