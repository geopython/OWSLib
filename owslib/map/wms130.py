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
from .util import openURL, testXMLValue, extract_xml_list, xmltag_split, nspath
from .fgdc import Metadata
from .iso import MD_Metadata
from .wms import ServiceException


WMS_NAMESPACE = 'http://www.opengis.net/wms'


def strip_ns(tag):
    return tag[tag.index('}') + 1:]


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
        se = self._capabilities.find(nspath('ServiceException', WMS_NAMESPACE))
        if se is not None:
            err_message = str(se.text).strip()
            raise ServiceException(err_message, xml)

        # build metadata objects
        self._buildMetadata(parse_remote_metadata)

    def _buildMetadata(self, parse_remote_metadata=False):
        ''' set up capabilities metadata objects '''
        # serviceIdentification metadata
        serviceelem = self._capabilities.find(nspath('Service', WMS_NAMESPACE))
        self.identification = ServiceIdentification(serviceelem, self.version)

        # serviceProvider metadata
        self.provider = ServiceProvider(serviceelem)

        # serviceOperations metadata
        self.operations = []
        for elem in self._capabilities.find(nspath('Capability/Request', WMS_NAMESPACE))[:]:
        # had this for a reason. what was it?
        # for elem in self._capabilities.find('/'.join([ns(t) for t in ['Capability', 'Request']]))[:]:
            self.operations.append(OperationMetadata(elem))

        # serviceContents metadata: our assumption is that services use a top-level
        # layer as a metadata organizer, nothing more.
        self.contents = {}
        caps = self._capabilities.find(nspath('Capability', WMS_NAMESPACE))

        # recursively gather content metadata for all layer elements.
        # To the WebMapService.contents store only metadata of named layers.
        def gather_layers(parent_elem, parent_metadata):
            for index, elem in enumerate(parent_elem.findall(nspath('Layer', WMS_NAMESPACE))):
                cm = ContentMetadata(elem, parent=parent_metadata, index=index + 1,
                                     parse_remote_metadata=parse_remote_metadata)
                if cm.id:
                    if cm.id in self.contents:
                        warnings.warn('Content metadata for layer "%s" already exists. Using child layer' % cm.id)
                    self.contents[cm.id] = cm
                gather_layers(elem, cm)
        gather_layers(caps, None)

        # exceptions
        self.exceptions = [f.text for f
                           in self._capabilities.findall(nspath('Capability/Exception/Format',
                                                         WMS_NAMESPACE))]

    def items(self):
        '''supports dict-like items() access'''
        items = []
        for item in self.contents:
            items.append((item, self.contents[item]))
        return items

    def getcapabilities(self):
        pass

    def getmap(self, layers=None, styles=None, srs=None, bbox=None,
               format=None, size=None, time=None, transparent=False,
               bgcolor='#FFFFFF',
               exceptions='XML',
               method='Get',
               **kwargs
               ):
        """Request and return an image from the WMS as a file-like object.

        Parameters
        ----------
        layers : list
            List of content layer names.
        styles : list
            Optional list of named styles, must be the same length as the
            layers list.
        srs : string
            A spatial reference system identifier.
        bbox : tuple
            (left, bottom, right, top) in srs units.


            CRS:84: (long, lat)
            EPSG:4326: (lat, long)
        format : string
            Output image format such as 'image/jpeg'.
        size : tuple
            (width, height) in pixels.
        transparent : bool
            Optional. Transparent background if True.
        bgcolor : string
            Optional. Image background color.
        method : string
            Optional. HTTP DCP method name: Get or Post.
        **kwargs : extra arguments
            anything else e.g. vendor specific parameters

        Example
        -------
            >>> wms = WebMapService('http://webservices.nationalatlas.gov/wms/1million',
                                    version='1.3.0')
            >>> img = wms.getmap(layers=['airports1m'],\
                                 styles=['default'],\
                                 srs='EPSG:4326',\
                                 bbox=(-176.646, 17.7016, -64.8017, 71.2854),\
                                 size=(300, 300),\
                                 format='image/jpeg',\
                                 transparent=True)
            >>> out = open('example.jpg.jpg', 'wb')
            >>> out.write(img.read())
            >>> out.close()

        """
        def _build_bbox():
            """this is not a complete list for the axis switch
            but the "between 4000 and 5000" option is incorrect as is
            just handling mercator
            """
            if str(srs).lower() in ['epsg:4326', 'epsg:4269', 'epsg:4267']:
                return (bbox[1], bbox[0], bbox[3], bbox[2])
            return bbox

        try:
            base_url = next((m.get('url') for m in self.getOperationByName('GetMap').methods if
                            m.get('type').lower() == method.lower()))
        except StopIteration:
            base_url = self.url
        request = {'version': self.version, 'request': 'GetMap'}

        # check layers and styles
        assert len(layers) > 0
        request['layers'] = ','.join(layers)
        if styles:
            assert len(styles) == len(layers)
            request['styles'] = ','.join(styles)
        else:
            request['styles'] = ''

        # size
        request['width'] = str(size[0])
        request['height'] = str(size[1])

        # remap srs to crs for the actual request
        bbox = _build_bbox()
        request['crs'] = str(srs)
        request['bbox'] = ','.join([repr(x) for x in bbox])
        request['format'] = str(format)
        request['transparent'] = str(transparent).upper()
        request['bgcolor'] = '0x' + bgcolor[1:7]
        request['exceptions'] = str(exceptions)

        if time is not None:
            request['time'] = str(time)

        if kwargs:
            for kw in kwargs:
                request[kw] = kwargs[kw]

        data = urlencode(request)

        u = openURL(base_url, data, method, username=self.username, password=self.password)

        # check for service exceptions, and return
        # fyi: in openURL, if the path goes through the content-type 
        # check w/out http header set and it instantiates a new rereadable
        # url, it loses the additional url obj methods (so just the stringio) and
        # the original u.info() fails with an attributeerror
        if u.headers['Content-Type'] in ['application/vnd.ogc.se_xml', 'text/xml']:
            se_xml = u.read()
            se_tree = etree.fromstring(se_xml)
            err_message = unicode(next(iter(se_tree.xpath('//*[local-name()="ServiceException"]/text()')), '')).strip()
            raise ServiceException(err_message, se_xml)
        return u

    def getServiceXML(self):
        xml = None
        if self._capabilities is not None:
            xml = etree.tostring(self._capabilities)
        return xml

    def getfeatureinfo(self):
        raise NotImplementedError

    def getOperationByName(self, name):
        """Return a named content item."""
        for item in self.operations:
            if item.name == name:
                return item
        raise KeyError("No operation named %s" % name)


class ServiceIdentification(object):
    ''' Implements IServiceIdentificationMetadata '''

    def __init__(self, infoset, version):
        self._root = infoset
        self.type = testXMLValue(self._root.find(nspath('Name', WMS_NAMESPACE)))
        self.version = version
        self.title = testXMLValue(self._root.find(nspath('Title', WMS_NAMESPACE)))
        self.abstract = testXMLValue(self._root.find(nspath('Abstract', WMS_NAMESPACE)))
        self.keywords = extract_xml_list(self._root.findall(nspath('KeywordList/Keyword', WMS_NAMESPACE)))
        self.accessconstraints = testXMLValue(self._root.find(nspath('AccessConstraints', WMS_NAMESPACE)))
        self.fees = testXMLValue(self._root.find(nspath('Fees', WMS_NAMESPACE)))


class ServiceProvider(object):
    ''' Implements IServiceProviderMetatdata '''
    def __init__(self, infoset):
        self._root = infoset
        name = self._root.find(nspath('ContactInformation/ContactPersonPrimary/ContactOrganization', WMS_NAMESPACE))
        if name is not None:
            self.name = name.text
        else:
            self.name = None
        self.url = self._root.find(nspath('OnlineResource', WMS_NAMESPACE)).attrib.get('{http://www.w3.org/1999/xlink}href', '')
        # contact metadata
        contact = self._root.find(nspath('ContactInformation', WMS_NAMESPACE))

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
        if strip_ns(elem.tag) != 'Layer':
            raise ValueError('%s should be a Layer' % (elem,))

        self.parent = parent
        if parent:
            self.index = "%s.%d" % (parent.index, index)
        else:
            self.index = str(index)

        self.id = self.name = testXMLValue(elem.find(nspath('Name', WMS_NAMESPACE)))

        # layer attributes
        self.queryable = int(elem.attrib.get('queryable', 0))
        self.cascaded = int(elem.attrib.get('cascaded', 0))
        self.opaque = int(elem.attrib.get('opaque', 0))
        self.noSubsets = int(elem.attrib.get('noSubsets', 0))
        self.fixedWidth = int(elem.attrib.get('fixedWidth', 0))
        self.fixedHeight = int(elem.attrib.get('fixedHeight', 0))

        # title is mandatory property
        self.title = None

        title = testXMLValue(elem.find(nspath('Title', WMS_NAMESPACE)))
        if title is not None:
            self.title = title.strip()

        self.abstract = testXMLValue(elem.find(nspath('Abstract', WMS_NAMESPACE)))

        # bboxes
        # TODO: LOOK UP AN ISSUE RE: not bboxES but just the one
        #       and then don't do that
        b = elem.find(nspath('BoundingBox', WMS_NAMESPACE))
        self.boundingBox = None
        if b is not None:
            try:
                # sometimes the SRS attribute is (wrongly) not provided
                # srs = b.attrib['SRS']
                srs = b.attrib['CRS']
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

        # make a bbox list (of tuples)
        crs_list = []
        for bb in elem.findall(nspath('BoundingBox', WMS_NAMESPACE)):
            srs = bb.attrib.get('CRS', None)
            box = map(float, [bb.attrib['minx'],
                              bb.attrib['miny'],
                              bb.attrib['maxx'],
                              bb.attrib['maxy']]
                      )
            crs_list.append((
                box[0],
                box[1],
                box[2],
                box[3],
                srs,
            ))
        self.crs_list = crs_list

        # ScaleHint
        sh = elem.find(nspath('ScaleHint', WMS_NAMESPACE))
        self.scaleHint = None
        if sh is not None:
            if 'min' in sh.attrib and 'max' in sh.attrib:
                self.scaleHint = {'min': sh.attrib['min'], 'max': sh.attrib['max']}

        attribution = elem.find(nspath('Attribution', WMS_NAMESPACE))
        if attribution is not None:
            self.attribution = dict()
            title = attribution.find(nspath('Title', WMS_NAMESPACE))
            url = attribution.find(nspath('OnlineResource', WMS_NAMESPACE))
            logo = attribution.find(nspath('LogoURL', WMS_NAMESPACE))

            if title is not None:
                self.attribution['title'] = title.text
            if url is not None:
                self.attribution['url'] = url.attrib['{http://www.w3.org/1999/xlink}href']
            if logo is not None:
                self.attribution['logo_size'] = (int(logo.attrib['width']), int(logo.attrib['height']))
                self.attribution['logo_url'] = logo.find(nspath('OnlineResource', WMS_NAMESPACE)).attrib['{http://www.w3.org/1999/xlink}href']

        b = elem.find(nspath('EX_GeographicBoundingBox', WMS_NAMESPACE))
        if b is not None:
            westBoundLongitude = b.find(nspath('westBoundLongitude', WMS_NAMESPACE))
            eastBoundLongitude = b.find(nspath('eastBoundLongitude', WMS_NAMESPACE))
            southBoundLatitude = b.find(nspath('southBoundLatitude', WMS_NAMESPACE))
            northBoundLatitude = b.find(nspath('northBoundLatitude', WMS_NAMESPACE))
            self.boundingBoxWGS84 = (
                float(westBoundLongitude.text if westBoundLongitude is not None else ''),
                float(southBoundLatitude.text if southBoundLatitude is not None else ''),
                float(eastBoundLongitude.text if eastBoundLongitude is not None else ''),
                float(northBoundLatitude.text if northBoundLatitude is not None else ''),
            )
        elif self.parent:
            self.boundingBoxWGS84 = self.parent.boundingBoxWGS84
        else:
            self.boundingBoxWGS84 = None

        # TODO: get this from the bbox attributes instead (deal with parents)
        # SRS options
        self.crsOptions = []

        # Copy any parent SRS options (they are inheritable properties)
        if self.parent:
            self.crsOptions = list(self.parent.crsOptions)

        # Look for SRS option attached to this layer
        if elem.find(nspath('CRS', WMS_NAMESPACE)) is not None:
            # some servers found in the wild use a single SRS
            # tag containing a whitespace separated list of SRIDs
            # instead of several SRS tags. hence the inner loop
            for srslist in map(lambda x: x.text, elem.findall(nspath('CRS', WMS_NAMESPACE))):
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
        for s in elem.findall(nspath('Style', WMS_NAMESPACE)):
            name = s.find(nspath('Name', WMS_NAMESPACE))
            title = s.find(nspath('Title', WMS_NAMESPACE))

            if name is None or title is None:
                raise ValueError('%s missing name or title' % (s,))
            style = {'title': title.text}
            # legend url
            legend = s.find(nspath('LegendURL/OnlineResource', WMS_NAMESPACE))
            if legend is not None:
                style['legend'] = legend.attrib['{http://www.w3.org/1999/xlink}href']
            self.styles[name.text] = style

        # keywords
        self.keywords = [f.text for f in elem.findall(nspath('KeywordList/Keyword', WMS_NAMESPACE))]

        # extents replaced by dimensions of name
        # comment by Soren Scott
        # <Dimension name="elevation" units="meters" default="500" multipleValues="1"
        #    nearestValue="0" current="true" unitSymbol="m">500, 490, 480</Dimension>
        # it can be repeated with the same name so ? this assumes a single one to match 1.1.1

        self.timepositions = None
        self.defaulttimeposition = None
        time_xpath = '*[local-name()="Dimension" and @name="time"]'
        time_dimension = next(iter(elem.xpath(time_xpath)), None)
        if time_dimension is not None:
            self.timepositions = time_dimension.text.split(',') if time_dimension.text else None
            self.defaulttimeposition = time_dimension.attrib.get('default', '')

        # Elevations - available vertical levels
        self.elevations = None
        elev_xpath = '*[local-name()="Dimension" and @name="elevation"]'
        elev_dimension = next(iter(elem.xpath(elev_xpath)), None)
        if elev_dimension is not None:
            self.elevations = [e.strip() for e in elev_dimension.text.split(',')] if elev_dimension.text else None

        # MetadataURLs
        self.metadataUrls = []
        for m in elem.findall(nspath('MetadataURL', WMS_NAMESPACE)):
            metadataUrl = {
                'type': testXMLValue(m.attrib['type'], attrib=True),
                'format': testXMLValue(m.find(nspath('Format', WMS_NAMESPACE))),
                'url': testXMLValue(m.find(nspath('OnlineResource', WMS_NAMESPACE)).attrib['{http://www.w3.org/1999/xlink}href'], attrib=True)
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
        for m in elem.findall(nspath('DataURL', WMS_NAMESPACE)):
            dataUrl = {
                'format': m.find(nspath('Format', WMS_NAMESPACE)).text.strip(),
                'url': m.find(nspath('OnlineResource', WMS_NAMESPACE)).attrib['{http://www.w3.org/1999/xlink}href']
            }
            self.dataUrls.append(dataUrl)

        # FeatureListURLs
        self.featureListUrls = []
        for m in elem.findall(nspath('FeatureListURL', WMS_NAMESPACE)):
            featureUrl = {
                'format': m.find(nspath('Format', WMS_NAMESPACE)).text.strip(),
                'url': m.find(nspath('OnlineResource', WMS_NAMESPACE)).attrib['{http://www.w3.org/1999/xlink}href']
            }
            self.featureListUrls.append(featureUrl)

        self.layers = []
        for child in elem.findall(nspath('Layer', WMS_NAMESPACE)):
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
        self.formatOptions = [f.text for f in elem.findall(nspath('Format', WMS_NAMESPACE))]
        self.methods = []
        for verb in elem.findall(nspath('DCPType/HTTP/*', WMS_NAMESPACE)):
            url = verb.find(nspath('OnlineResource', WMS_NAMESPACE)).attrib['{http://www.w3.org/1999/xlink}href']
            self.methods.append({'type': xmltag_split(verb.tag), 'url': url})


class ContactMetadata:
    """Abstraction for contact details advertised in GetCapabilities.
    """
    def __init__(self, elem):
        name = elem.find(nspath('ContactPersonPrimary/ContactPerson', WMS_NAMESPACE))
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

        address = elem.find(nspath('ContactAddress', WMS_NAMESPACE))
        if address is not None:
            street = address.find(nspath('Address', WMS_NAMESPACE))
            if street is not None: self.address = street.text

            city = address.find(nspath('City', WMS_NAMESPACE))
            if city is not None: self.city = city.text

            region = address.find(nspath('StateOrProvince', WMS_NAMESPACE))
            if region is not None: self.region = region.text

            postcode = address.find(nspath('PostCode', WMS_NAMESPACE))
            if postcode is not None: self.postcode = postcode.text

            country = address.find(nspath('Country', WMS_NAMESPACE))
            if country is not None: self.country = country.text

        organization = elem.find(nspath('ContactPersonPrimary/ContactOrganization', WMS_NAMESPACE))
        if organization is not None: self.organization = organization.text
        else: self.organization = None

        position = elem.find(nspath('ContactPosition', WMS_NAMESPACE))
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
