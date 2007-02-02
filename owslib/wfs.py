# =============================================================================
# OWSLib. Copyright (C) 2005 Sean C. Gillies
#
# Contact email: sgillies@frii.com
#
# $Id: wfs.py 503 2006-02-01 17:09:12Z dokai $
# =============================================================================

import cgi
from cStringIO import StringIO
from urllib import urlencode
from urllib2 import urlopen

from etree import etree

WFS_NAMESPACE = 'http://www.opengis.net/wfs'
OGC_NAMESPACE = 'http://www.opengis.net/ogc'

def nspath(path, ns=WFS_NAMESPACE):
    """
    Prefix the given path with the given namespace identifier.
    
    Parameters
    ----------
    path : string
        ElementTree API Compatible path expression

    ns : string
        The XML namespace. Defaults to WFS namespace.
    """
    components = []
    for component in path.split("/"):
        if component != '*':
            component = "{%s}%s" % (ns, component)
        components.append(component)
    return "/".join(components)


class ServiceException(Exception):
    pass


class WebFeatureService(object):
    """Abstraction for OGC Web Feature Service (WFS).

    Implements IWebFeatureService.
    """
    
    def __init__(self, url, version='1.0.0', xml=None):
        """Initialize."""
        self.url = url
        self.version = version
        self._capabilities = None
        if xml:
            reader = WFSCapabilitiesReader(self.version)
            self._capabilities = ServiceMetadata(reader.readString(xml))
        
    def _getcapproperty(self):
        if not self._capabilities:
            reader = WFSCapabilitiesReader(self.version)
            self._capabilities = ServiceMetadata(reader.read(self.url))
        return self._capabilities
    capabilities = property(_getcapproperty, None)
            
    def getcapabilities(self):
        """Request and return capabilities document from the WFS as a 
        file-like object."""
        reader = WFSCapabilitiesReader(self.version)
        return urlopen(reader.capabilities_url(self.url))
    
    def getfeature(self, typename=None, filter=None, bbox=None, featureid=None,
                   featureversion=None, propertyname=['*'], maxfeatures=None,
                   method='{http://www.opengis.net/wfs}Get'):
        """Request and return feature data as a file-like object.
        
        Parameters
        ----------
        typename : list
            List of typenames (string)
        filter : string 
            XML-encoded OGC filter expression.
        bbox : tuple
            (left, bottom, right, top) in the feature type's coordinates.
        featureid : list
            List of unique feature ids (string)
        featureversion : string
            Default is most recent feature version.
        propertyname : list
            List of feature property names. '*' matches all.
        maxfeatures : int
            Maximum number of features to be returned.
        method : string
            Qualified name of the HTTP DCP method to use.

        There are 3 different modes of use

        1) typename and bbox (simple spatial query)
        2) typename and filter (more expressive)
        3) featureid (direct access to known features)
        """
        md = self.capabilities
        base_url = md.getOperationByName('{http://www.opengis.net/wfs}GetFeature').methods[method]['url']
        request = {'service': 'WFS', 'version': self.version, 'request': 'GetFeature'}
        
        # check featureid
        if featureid:
            request['featureid'] = ','.join(featureid)
        elif bbox and typename:
            request['bbox'] = ','.join([str(x) for x in bbox])
        elif filter and typename:
            request['filter'] = str(filter)
        assert len(typename) > 0
        request['typename'] = ','.join(typename)
        
        request['propertyname'] = ','.join(propertyname)
        if featureversion: request['featureversion'] = str(featureversion)
        if maxfeatures: request['maxfeatures'] = str(maxfeatures)
        
        data = urlencode(request)
        if method == 'Post':
            u = urlopen(base_url, data=data)
        else:
            u = urlopen(base_url + data)
        
        # check for service exceptions, rewrap, and return
        # We're going to assume that anything with a content-length > 32k
        # is data. We'll check anything smaller.
        if int(u.info()['Content-Length']) < 32000:
            data = u.read()
            tree = etree.fromstring(data)
            if tree.tag == "{%s}ServiceExceptionReport" % OGC_NAMESPACE:
                se = tree.find(nspath('ServiceException', OGC_NAMESPACE))
                raise ServiceException, str(se.text).strip()
            else:
                return StringIO(data)
        else:
            return u


class ServiceMetadata(object):
    """Abstraction for WFS metadata.
    
    Implements IServiceMetadata.
    """

    def __init__(self, infoset):
        """Initialize from an element tree."""
        self._root = infoset.getRoot()
        # properties
        self.service = self._root.find(nspath('Service/Name')).text
        self.title = self._root.find(nspath('Service/Title')).text
        self.abstract = self._root.find(nspath('Service/Abstract')).text
        self.link = self._root.find(nspath('Service/OnlineResource')).text
        
        # operations []
        self.operations = []
        for elem in self._root.findall(nspath('Capability/Request/*')):
            self.operations.append(OperationMetadata(elem))

        # contents: our assumption is that services use a top-level layer
        # as a metadata organizer, nothing more.
        self.contents = []
        top = self._root.find(nspath('FeatureTypeList'))
        for elem in self._root.findall(nspath('FeatureTypeList/FeatureType')):
            self.contents.append(ContentMetadata(elem, top))
        
        # keywords
        self.keywords = []

        self.provider = ContactMetadata(self._root.find('Service/ContactInformation'))

    def getContentByName(self, name):
        """Return a named content item."""
        for item in self.contents:
            if item.name == name:
                return item
        raise KeyError, "No content named %s" % name

    def getOperationByName(self, name):
        """Return a named content item."""
        for item in self.operations:
            if item.name == name:
                return item
        raise KeyError, "No operation named %s" % name


class ContentMetadata:
    """Abstraction for WMS metadata.
    
    Implements IMetadata.
    """

    def __init__(self, elem, parent):
        """."""
        self.name = elem.find(nspath('Name')).text
        self.title = elem.find(nspath('Title')).text
        # bboxes
        self.boundingBox = None
        b = elem.find(nspath('BoundingBox'))
        if b is not None:
            self.boundingBox = (float(b.attrib['minx']),float(b.attrib['miny']),
                    float(b.attrib['maxx']), float(b.attrib['maxy']),
                    b.attrib['SRS'])
        self.boundingBoxWGS84 = None
        b = elem.find(nspath('LatLongBoundingBox'))
        if b is not None:
            self.boundingBoxWGS84 = (
                    float(b.attrib['minx']),float(b.attrib['miny']),
                    float(b.attrib['maxx']), float(b.attrib['maxy']),
                    )
        # crs options
        self.crsOptions = [srs.text for srs in elem.findall(nspath('SRS'))]

        # verbs
        self.verbOptions = [op.tag for op \
            in parent.findall(nspath('Operations/*'))]
        self.verbOptions + [op.tag for op \
            in elem.findall(nspath('Operations/*')) \
            if op.tag not in self.verbOptions]
        

class OperationMetadata:
    """Abstraction for WMS metadata.
    
    Implements IMetadata.
    """
    def __init__(self, elem):
        """."""
        self.name = elem.tag
        # formatOptions
        self.formatOptions = [f.tag for f in elem.findall(nspath('ResultFormat/*'))]
        methods = []
        for verb in elem.findall(nspath('DCPType/HTTP/*')):
            url = verb.attrib['onlineResource']
            methods.append((verb.tag, {'url': url}))
        self.methods = dict(methods)


class ContactMetadata:
    """Abstraction for contact details advertised in GetCapabilities.
    """
    # TODO: refactor with class from wms

    def __init__(self, elem):
        self.name = None
        self.email = None

        if elem:
            self.name = elem.find('ContactPersonPrimary/ContactPerson').text
            self.organization = elem.find('ContactPersonPrimary/ContactOrganization').text
            address = elem.find('ContactAddress')
            if address is not None:
                try:    
                    self.address = address.find('Address').text
                    self.city = address.find('City').text
                    self.region = address.find('StateOrProvince').text
                    self.postcode = address.find('Postcode').text
                    self.country = address.find('Country').text
                except: pass
            self.email = elem.find('ContactElectronicMailAddress').text 


class WFSCapabilitiesInfoset(object):
    """High-level container for WFS Capabilities based on lxml.etree
    """

    def __init__(self, infoset):
        """Initialize"""
        self._infoset = infoset

    #
    # XML Node accessors
    # 
    
    def getRoot(self):
        """
        Returns the root node of the capabilities document.
        """
        return self._infoset

    def getServiceNode(self):
        """
        Returns the <Service> node of the capabilities document.
        """
        return self.getRoot().find(nspath('Service'))

    def getCapabilitiesNode(self):
        """
        Returns the <Capability> node of the capabilities document.
        """
        return self.getRoot().find(nspath('Capability'))

    def getFeatureTypeNode(self):
        """
        Returns the <FeatureTypeList> node of the capabilities document.
        """
        return self.getRoot().find(nspath('FeatureTypeList'))

    def getFilterNode(self):
        """
        Returns the <Filter_Capabilities> node of the capabilities document.
        """
        return self.getRoot().find(nspath('Filter_Capabilities'))

    #
    # Info accessors
    #

    def getServiceInfo(self):
        """
        Returns the WFS Service information packed in a dictionary.
        """
        service = self.getServiceNode()
        info = {}
        for tag in ('Name', 'Title', 'Abstract', 'Keyword', 'OnlineResource',
                    'Fees', 'AccessConstraints'):
            info[tag.lower()] = service.findtext(nspath(tag))
        return info

    def getCapabilityInfo(self):
        """
        Returns the WFS Capability information packed in a dictionary.
        """
        # Simplify the resource URLs, favoring GET over POST.
        # Assume GML2.
        capabilities = self.getCapabilitiesNode()
        info = {}
        
        for key, path_id in [('capabilities', 'GetCapabilities'),
                             ('description', 'DescribeFeatureType'),
                             ('features', 'GetFeature')]:
            get_path = nspath('Request/%s/DCPType/HTTP/Get' % path_id)
            post_path = nspath('Request/%s/DCPType/HTTP/Post' % path_id)
            
            node = capabilities.find(get_path) or capabilities.find(post_path)
            info[key] = node.get('onlineResource', None)
        return info

    def getFeatureTypeInfo(self):
        """
        Returns the WFS Feature type information as a list of dictionaries.
        """
        # Assume XMLSchema is used as the schema description language.
        info = []
        for featuretype in self.getFeatureTypeNode().getiterator(nspath('FeatureType')):
            entry = {}
            # Loop over simple text nodes
            for tag in ('Name', 'Title', 'Abstract', 'SRS'):
                entry[tag.lower()] = featuretype.findtext(nspath(tag))

            # LatLongBoundingBox
            entry['latlongboundingbox'] = []
            for latlong in featuretype.findall(nspath('LatLongBoundingBox')):
                entry['latlongboundingbox'].append('%s,%s,%s,%s' % (latlong.get('minx'),
                                                                    latlong.get('miny'),
                                                                    latlong.get('maxx'),
                                                                    latlong.get('maxy')))
            
            # MetadataURL
            entry['metadataurl'] = []
            for metadataurl in featuretype.findall(nspath('MetadataURL')):
                entry['metadataurl'].append(metadataurl.text)

            info.append(entry)
        return info


class WFSCapabilitiesReader(object):
    """Read and parse capabilities document into a lxml.etree infoset
    """

    def __init__(self, version='1.0'):
        """Initialize"""
        self.version = version
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

    def read(self, url):
        """Get and parse a WFS capabilities document, returning an
        instance of WFSCapabilitiesInfoset

        Parameters
        ----------
        url : string
            The URL to the WFS capabilities document.
        """
        request = self.capabilities_url(url)
        u = urlopen(request)
        return WFSCapabilitiesInfoset(etree.fromstring(u.read()))

    def readString(self, st):
        """Parse a WFS capabilities document, returning an
        instance of WFSCapabilitiesInfoset

        string should be an XML capabilities document
        """
        if not isinstance(st, str):
            raise ValueError("String must be of type string, not %s" % type(st))
        return WFSCapabilitiesInfoset(etree.fromstring(st))
    
