# -*- coding: ISO-8859-15 -*-

'''
API For Web Map Service version 1.3.0
'''

from __future__ import (absolute_import, division, print_function)

import cgi
try:                    # Python 3
    from urllib.parse import urlencode
except ImportError:     # Python 2
    from urllib import urlencode

import warnings

import six
from owslib.etree import etree
from owslib.util import openURL, ServiceException, testXMLValue, extract_xml_list, xmltag_split, OrderedDict
from owslib.util import nspath
from owslib.fgdc import Metadata
from owslib.iso import MD_Metadata
from owslib.crs import Crs
from owslib.namespaces import Namespaces
from owslib.map.wms_cap import WMSCapabilitiesReader

from owslib.util import log

n = Namespaces()
WMS_NAMESPACE = n.get_namespace("wms")
# OGC_NAMESPACE = n.get_namespace("ogc")


class WebMapService_1_3_0():

    def __init__(self, url, version='1.3.0', xml=None, username=None,
                 password=None, parse_remote_metadata=False, timeout=30):
        """initialize"""
        self.url = url
        self.username = username
        self.password = password
        self.version = version
        self.timeout = timeout
        self._capabilities = None

        # Authentication handled by Reader
        reader = WMSCapabilitiesReader(self.version, url=self.url,
                                       un=self.username, pw=self.password)
        if xml:  # read from stored xml
            self._capabilities = reader.readString(xml)
        else:  # read from server
            self._capabilities = reader.read(self.url, timeout=self.timeout)

        # avoid building capabilities metadata if the
        # response is a ServiceExceptionReport
        se = self._capabilities.find('ServiceException')
        if se is not None:
            err_message = str(se.text).strip()
            raise ServiceException(err_message, xml)

    def _buildMetadata(self, parse_remote_metadata=False):
        '''set up capabilities metadata objects: '''

        # serviceIdentification metadata
        serviceelem = self._capabilities.find(nspath('Service',
                                              ns=WMS_NAMESPACE))
        self.identification = ServiceIdentification(serviceelem, self.version)

        # serviceProvider metadata
        self.provider = ServiceProvider(serviceelem)

        # serviceOperations metadata
        self.operations = []
        for elem in self._capabilities.find(nspath('Capability/Request',
                                            ns=WMS_NAMESPACE))[:]:
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


class ContentMetadata(object):
    def __init__(self, elem, parent=None, index=0, parse_remote_metadata=False, timeout=30):
        if xmltag_split(elem.tag) != 'Layer':
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
        b = elem.find(nspath('BoundingBox', WMS_NAMESPACE))
        self.boundingBox = None
        if b is not None:
            try:
                # sometimes the SRS attribute is (wrongly) not provided
                srs = b.attrib['CRS']
            except KeyError:
                srs = None

            box = map(float, [b.attrib['minx'],
                              b.attrib['miny'],
                              b.attrib['maxx'],
                              b.attrib['maxy']]
                      )
            self.boundingBox = (
                box[0],
                box[1],
                box[2],
                box[3],
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


class OperationMetadata(object):
    def __init__(self, elem):
        """."""
        self.name = xmltag_split(elem.tag)
        # formatOptions
        self.formatOptions = [f.text for f in elem.findall(nspath('Format', WMS_NAMESPACE))]
        self.methods = []
        for verb in elem.findall(nspath('DCPType/HTTP/*', WMS_NAMESPACE)):
            url = verb.find(nspath('OnlineResource', WMS_NAMESPACE)).attrib['{http://www.w3.org/1999/xlink}href']
            self.methods.append({'type': xmltag_split(verb.tag), 'url': url})


class ContactMetadata(object):
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
            if street is not None:
                self.address = street.text

            city = address.find(nspath('City', WMS_NAMESPACE))
            if city is not None:
                self.city = city.text

            region = address.find(nspath('StateOrProvince', WMS_NAMESPACE))
            if region is not None:
                self.region = region.text

            postcode = address.find(nspath('PostCode', WMS_NAMESPACE))
            if postcode is not None:
                self.postcode = postcode.text

            country = address.find(nspath('Country', WMS_NAMESPACE))
            if country is not None:
                self.country = country.text

        organization = elem.find(nspath('ContactPersonPrimary/ContactOrganization', WMS_NAMESPACE))
        if organization is not None:
            self.organization = organization.text
        else:
            self.organization = None

        position = elem.find(nspath('ContactPosition', WMS_NAMESPACE))
        if position is not None:
            self.position = position.text
        else:
            self.position = None
