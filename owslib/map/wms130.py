# -*- coding: iso-8859-15 -*-
# =============================================================================
# Copyright (c) 2004, 2006 Sean C. Gillies
# Copyright (c) 2005 Nuxeo SARL <http://nuxeo.com>
#
# Authors : Sean Gillies <sgillies@frii.com>
#           Julien Anguenot <ja@nuxeo.com>
#
# Contact email: sgillies@frii.com
# =============================================================================

"""
API for Web Map Service (WMS) methods and metadata.

Support for version 1.3.0 of the WMS protocol.
"""

from __future__ import (absolute_import, division, print_function)

import cgi
import urllib2
from urllib import urlencode
import warnings
from .etree import etree
from .util import openURL, testXMLValue, extract_xml_list, xmltag_split
from owslib.fgdc import Metadata
from owslib.iso import MD_Metadata
from owslib.wms import ServiceException


def ns(tag):
    return '{http://www.opengis.net/wms}' + tag


class WebMapService_1_3_0(object):
    """Abstraction for OGC Web Map Service (WMS)

    Implements IWebMapService
    """

    def __getitem__(self, name):
        ''' check contents dictionary to allow dict like access to service layers'''
        if name in self.__getattribute__('contents').keys():
            return self.__getattribute__('contents')[name]
        else:
            raise KeyError("No content named %s" % name)

    def __init__(self, url, xml=None,
                username=None, password=None, parse_remote_metadata=False):
        """Initialize."""
        self.url = url
        self.username = username
        self.password = password
        self.version = '1.3.0'
        self._capabilities = None

        # Authentication handled by Reader
        reader = WMSCapabilitiesReader(
                self.version, url=self.url, un=self.username, pw=self.password
                )
        if xml:  # read from stored xml
            self._capabilities = reader.readString(xml)
        else:  # read from server
            self._capabilities = reader.read(self.url)

        # avoid building capabilities metadata if the response is a ServiceExceptionReport
        se = self._capabilities.find('ServiceException')
        if se is not None:
            err_message = str(se.text).strip()
            raise ServiceException(err_message, xml)

        # build metadata objects
        self._buildMetadata(parse_remote_metadata)

    def _buildMetadata(self, parse_remote_metadata=False):
        ''' set up capabilities metadata objects '''
        # serviceIdentification metadata
        serviceelem = self._capabilities.find(ns('Service'))
        self.identification = ServiceIdentification(serviceelem, self.version)

        # serviceProvider metadata
        self.provider = ServiceProvider(serviceelem)

        # serviceOperations metadata
        self.operations = []
        for elem in self._capabilities.find('/'.join([ns(t) for t in ['Capability', 'Request']]))[:]:
            self.operations.append(OperationMetadata(elem))

        # serviceContents metadata: our assumption is that services use a top-level
        # layer as a metadata organizer, nothing more.
        self.contents = {}
        caps = self._capabilities.find(ns('Capability'))

        # recursively gather content metadata for all layer elements.
        # To the WebMapService.contents store only metadata of named layers.
        def gather_layers(parent_elem, parent_metadata):
            for index, elem in enumerate(parent_elem.findall(ns('Layer'))):
                cm = ContentMetadata(elem, parent=parent_metadata, index=index+1, parse_remote_metadata=parse_remote_metadata)
                if cm.id:
                    if cm.id in self.contents:
                        warnings.warn('Content metadata for layer "%s" already exists. Using child layer' % cm.id)
                    self.contents[cm.id] = cm
                gather_layers(elem, cm)
        gather_layers(caps, None)

        # exceptions
        self.exceptions = [f.text for f \
                in self._capabilities.findall('/'.join([ns(t) for t in ['Capability', 'Exception', 'Format']]))]


class ServiceIdentification(object):
    ''' Implements IServiceIdentificationMetadata '''

    def __init__(self, infoset, version):
        self._root = infoset
        self.type = testXMLValue(self._root.find(ns('Name')))
        self.version = version
        self.title = testXMLValue(self._root.find(ns('Title')))
        self.abstract = testXMLValue(self._root.find(ns('Abstract')))
        self.keywords = extract_xml_list(self._root.findall('/'.join([ns(t) for t in ['KeywordList', 'Keyword']])))
        self.accessconstraints = testXMLValue(self._root.find(ns('AccessConstraints')))
        self.fees = testXMLValue(self._root.find(ns('Fees')))


class ServiceProvider(object):
    ''' Implements IServiceProviderMetatdata '''
    def __init__(self, infoset):
        self._root = infoset
        name = self._root.find('/'.join([ns(t) for t in ['ContactInformation', 'ContactPersonPrimary', 'ContactOrganization']]))
        if name is not None:
            self.name = name.text
        else:
            self.name = None
        self.url = self._root.find(ns('OnlineResource')).attrib.get('{http://www.w3.org/1999/xlink}href', '')
        # contact metadata
        contact = self._root.find(ns('ContactInformation'))
        # sometimes there is a contact block that is empty, so make
        # sure there are children to parse
        if contact is not None and contact[:] != []:
            self.contact = ContactMetadata(contact)
        else:
            self.contact = None

    def getContentByName(self, name):
        """Return a named content item."""
        for item in self.contents:
            if item.name == name:
                return item
        raise KeyError("No content named %s" % name)

    def getOperationByName(self, name):
        """Return a named content item."""
        for item in self.operations:
            if item.name == name:
                return item
        raise KeyError("No operation named %s" % name)


class ContentMetadata:
    """
    Abstraction for WMS layer metadata.

    Implements IContentMetadata.
    """
    def __init__(self, elem, parent=None, index=0, parse_remote_metadata=False, timeout=30):
        if elem.tag != 'Layer':
            raise ValueError('%s should be a Layer' % (elem,))

        self.parent = parent
        if parent:
            self.index = "%s.%d" % (parent.index, index)
        else:
            self.index = str(index)

        self.id = self.name = testXMLValue(elem.find(ns('Name')))

        # layer attributes
        self.queryable = int(elem.attrib.get('queryable', 0))
        self.cascaded = int(elem.attrib.get('cascaded', 0))
        self.opaque = int(elem.attrib.get('opaque', 0))
        self.noSubsets = int(elem.attrib.get('noSubsets', 0))
        self.fixedWidth = int(elem.attrib.get('fixedWidth', 0))
        self.fixedHeight = int(elem.attrib.get('fixedHeight', 0))

        # title is mandatory property
        self.title = None
        title = testXMLValue(elem.find(ns('Title')))
        if title is not None:
            self.title = title.strip()

        self.abstract = testXMLValue(elem.find(ns('Abstract')))

        # bboxes
        b = elem.find(ns('BoundingBox'))
        self.boundingBox = None
        if b is not None:
            try:
                # sometimes the SRS attribute is (wrongly) not provided
                sr = b.attrib['SRS']
            except KeyError:
                srs = None
            self.boundingBox = (
                float(b.attrib['minx']),
                float(b.attrib['miny']),
                float(b.attrib['maxx']),
                float(b.attrib['maxy']),
                srs,
                )
        elif self.parent:
            if hasattr(self.parent, 'boundingBox'):
                self.boundingBox = self.parent.boundingBox

        # ScaleHint
        sh = elem.find(ns('ScaleHint'))
        self.scaleHint = None
        if sh is not None:
            if 'min' in sh.attrib and 'max' in sh.attrib:
                self.scaleHint = {'min': sh.attrib['min'], 'max': sh.attrib['max']}

        attribution = elem.find(ns('Attribution'))
        if attribution is not None:
            self.attribution = dict()
            title = attribution.find(ns('Title'))
            url = attribution.find(ns('OnlineResource'))
            logo = attribution.find(ns('LogoURL'))
            if title is not None:
                self.attribution['title'] = title.text
            if url is not None:
                self.attribution['url'] = url.attrib['{http://www.w3.org/1999/xlink}href']
            if logo is not None:
                self.attribution['logo_size'] = (int(logo.attrib['width']), int(logo.attrib['height']))
                self.attribution['logo_url'] = logo.find(ns('OnlineResource')).attrib['{http://www.w3.org/1999/xlink}href']

        b = elem.find(ns('LatLonBoundingBox'))
        if b is not None:
            self.boundingBoxWGS84 = (
                float(b.attrib['minx']),
                float(b.attrib['miny']),
                float(b.attrib['maxx']),
                float(b.attrib['maxy']),
            )
        elif self.parent:
            self.boundingBoxWGS84 = self.parent.boundingBoxWGS84
        else:
            self.boundingBoxWGS84 = None

        # SRS options
        self.crsOptions = []

        # Copy any parent SRS options (they are inheritable properties)
        if self.parent:
            self.crsOptions = list(self.parent.crsOptions)

        # Look for SRS option attached to this layer
        if elem.find(ns('SRS')) is not None:
            # some servers found in the wild use a single SRS
            # tag containing a whitespace separated list of SRIDs
            # instead of several SRS tags. hence the inner loop
            for srslist in map(lambda x: x.text, elem.findall(ns('SRS'))):
                if srslist:
                    for srs in srslist.split():
                        self.crsOptions.append(srs)

        # Get rid of duplicate entries
        self.crsOptions = list(set(self.crsOptions))

        # Set self.crsOptions to None if the layer (and parents) had no SRS options
        if len(self.crsOptions) == 0:
            # raise ValueError('%s no SRS available!?' % (elem,))
            # Comment by D Lowe.
            # Do not raise ValueError as it is possible that a layer is purely a parent layer and does not have SRS specified. Instead set crsOptions to None
            # Comment by Jachym:
            # Do not set it to None, but to [], which will make the code
            # work further. Fixed by anthonybaxter
            self.crsOptions = []

        # Styles
        self.styles = {}

        # Copy any parent styles (they are inheritable properties)
        if self.parent:
            self.styles = self.parent.styles.copy()

        # Get the styles for this layer (items with the same name are replaced)
        for s in elem.findall(ns('Style')):
            name = s.find(ns('Name'))
            title = s.find(ns('Title'))
            if name is None or title is None:
                raise ValueError('%s missing name or title' % (s,))
            style = {'title': title.text}
            # legend url
            legend = s.find('/'.join([ns(t) for t in ['LegendURL', 'OnlineResource']]))
            if legend is not None:
                style['legend'] = legend.attrib['{http://www.w3.org/1999/xlink}href']
            self.styles[name.text] = style

        # keywords
        self.keywords = [f.text for f in elem.findall('/'.join([ns(t) for t in ['KeywordList', 'Keyword']]))]

        # timepositions - times for which data is available.
        self.timepositions = None
        self.defaulttimeposition = None
        for extent in elem.findall(ns('Extent')):
            if extent.attrib.get("name").lower() == 'time':
                if extent.text:
                    self.timepositions = extent.text.split(',')
                    self.defaulttimeposition = extent.attrib.get("default")
                    break

        # Elevations - available vertical levels
        self.elevations = None
        for extent in elem.findall(ns('Extent')):
            if extent.attrib.get("name").lower() == 'elevation':
                if extent.text:
                    self.elevations = extent.text.split(',')
                    break

        # MetadataURLs
        self.metadataUrls = []
        for m in elem.findall(ns('MetadataURL')):
            metadataUrl = {
                'type': testXMLValue(m.attrib['type'], attrib=True),
                'format': testXMLValue(m.find(ns('Format'))),
                'url': testXMLValue(m.find(ns('OnlineResource')).attrib['{http://www.w3.org/1999/xlink}href'], attrib=True)
            }

            if metadataUrl['url'] is not None and parse_remote_metadata:  # download URL
                try:
                    content = urllib2.urlopen(metadataUrl['url'], timeout=timeout)
                    doc = etree.parse(content)
                    if metadataUrl['type'] is not None:
                        if metadataUrl['type'] == 'FGDC':
                            metadataUrl['metadata'] = Metadata(doc)
                        if metadataUrl['type'] == 'TC211':
                            metadataUrl['metadata'] = MD_Metadata(doc)
                except Exception:
                    metadataUrl['metadata'] = None

            self.metadataUrls.append(metadataUrl)

        # DataURLs
        self.dataUrls = []
        for m in elem.findall(ns('DataURL')):
            dataUrl = {
                'format': m.find(ns('Format')).text.strip(),
                'url': m.find(ns('OnlineResource')).attrib['{http://www.w3.org/1999/xlink}href']
            }
            self.dataUrls.append(dataUrl)

        self.layers = []
        for child in elem.findall(ns('Layer')):
            self.layers.append(ContentMetadata(child, self))

    def __str__(self):
        return 'Layer Name: %s Title: %s' % (self.name, self.title)


class OperationMetadata:
    """Abstraction for WMS OperationMetadata.

    Implements IOperationMetadata.
    """
    def __init__(self, elem):
        """."""
        self.name = xmltag_split(elem.tag)
        # formatOptions
        self.formatOptions = [f.text for f in elem.findall(ns('Format'))]
        self.methods = []
        for verb in elem.findall('/'.join([ns(t) for t in ['DCPType', 'HTTP', '*']])):
            url = verb.find(ns('OnlineResource')).attrib['{http://www.w3.org/1999/xlink}href']
            self.methods.append({'type': xmltag_split(verb.tag), 'url': url})


class ContactMetadata:
    """Abstraction for contact details advertised in GetCapabilities.
    """
    def __init__(self, elem):
        name = elem.find('ContactPersonPrimary/ContactPerson')
        if name is not None:
            self.name = name.text
        else:
            self.name = None
        email = elem.find('ContactElectronicMailAddress')
        if email is not None:
            self.email = email.text
        else:
            self.email = None
        self.address = self.city = self.region = None
        self.postcode = self.country = None

        address = elem.find(ns('ContactAddress'))
        if address is not None:
            street = address.find(ns('Address'))
            if street is not None: self.address = street.text

            city = address.find(ns('City'))
            if city is not None: self.city = city.text

            region = address.find(ns('StateOrProvince'))
            if region is not None: self.region = region.text

            postcode = address.find(ns('PostCode'))
            if postcode is not None: self.postcode = postcode.text

            country = address.find(ns('Country'))
            if country is not None: self.country = country.text

        organization = elem.find('/'.join([ns(t) for t in ['ContactPersonPrimary', 'ContactOrganization']]))
        if organization is not None: self.organization = organization.text
        else: self.organization = None

        position = elem.find(ns('ContactPosition'))
        if position is not None: self.position = position.text
        else: self.position = None


class WMSCapabilitiesReader:
    """Read and parse capabilities document into a lxml.etree infoset
    """

    def __init__(self, version='1.3.0', url=None, un=None, pw=None):
        """Initialize"""
        self.version = version
        self._infoset = None
        self.url = url
        self.username = un
        self.password = pw

        #if self.username and self.password:
            ## Provide login information in order to use the WMS server
            ## Create an OpenerDirector with support for Basic HTTP 
            ## Authentication...
            #passman = HTTPPasswordMgrWithDefaultRealm()
            #passman.add_password(None, self.url, self.username, self.password)
            #auth_handler = HTTPBasicAuthHandler(passman)
            #opener = build_opener(auth_handler)
            #self._open = opener.open

    def capabilities_url(self, service_url):
        """Return a capabilities url
        """
        qs = []
        if service_url.find('?') != -1:
            qs = cgi.parse_qsl(service_url.split('?')[1])

        params = [x[0] for x in qs]

        if 'service' not in params:
            qs.append(('service', 'WMS'))
        if 'request' not in params:
            qs.append(('request', 'GetCapabilities'))
        if 'version' not in params:
            qs.append(('version', self.version))

        urlqs = urlencode(tuple(qs))
        return service_url.split('?')[0] + '?' + urlqs

    def read(self, service_url):
        """Get and parse a WMS capabilities document, returning an
        elementtree instance

        service_url is the base url, to which is appended the service,
        version, and request parameters
        """
        getcaprequest = self.capabilities_url(service_url)

        #now split it up again to use the generic openURL function...
        spliturl=getcaprequest.split('?')
        u = openURL(spliturl[0], spliturl[1], method='Get', username = self.username, password = self.password)
        return etree.fromstring(u.read())

    def readString(self, st):
        """Parse a WMS capabilities document, returning an elementtree instance

        string should be an XML capabilities document
        """
        if not isinstance(st, str):
            raise ValueError("String must be of type string, not %s" % type(st))
        return etree.fromstring(st)
