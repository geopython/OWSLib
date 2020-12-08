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
API For Web Map Service version 1.3.0.
"""

from urllib.parse import urlencode

import warnings
from math import sqrt
from owslib.etree import etree
from owslib.util import (openURL, ServiceException, testXMLValue,
                         extract_xml_list, xmltag_split, OrderedDict, nspath,
                         nspath_eval, bind_url, Authentication)
from owslib.fgdc import Metadata
from owslib.iso import MD_Metadata
from owslib.crs import Crs
from owslib.namespaces import Namespaces
from owslib.map.common import WMSCapabilitiesReader, AbstractContentMetadata

from owslib.util import log

n = Namespaces()
WMS_NAMESPACE = n.get_namespace("wms")
OGC_NAMESPACE = n.get_namespace('ogc')
INCH_TO_M = 0.0254  # Standard inch to meter conversion
OGC_PIXEL_SIZE = 0.00028  # The OGC standard pixel size is 0.28 mm, here it's in meter
OGC_DPI = INCH_TO_M / OGC_PIXEL_SIZE
# The sqrt(2) is because the scale is on the diagonal and the resolution on the side
SCALEDENOM_TO_RESOLUTION = 1 / OGC_DPI * INCH_TO_M * sqrt(2)


class WebMapService_1_3_0(object):

    def __getitem__(self, name):
        ''' check contents dictionary to allow dict
        like access to service layers
        '''
        if name in self.__getattribute__('contents'):
            return self.__getattribute__('contents')[name]
        else:
            raise KeyError("No content named %s" % name)

    def __init__(self, url, version='1.3.0', xml=None, username=None,
                 password=None, parse_remote_metadata=False, timeout=30,
                 headers=None, auth=None):
        """initialize"""
        if auth:
            if username:
                auth.username = username
            if password:
                auth.password = password
        self.url = url
        self.version = version
        self.timeout = timeout
        self.headers = headers
        self._capabilities = None
        self.auth = auth or Authentication(username, password)

        # Authentication handled by Reader
        reader = WMSCapabilitiesReader(
            self.version, url=self.url, headers=headers, auth=self.auth)
        if xml:  # read from stored xml
            self._capabilities = reader.readString(xml)
        else:  # read from server
            self._capabilities = reader.read(self.url, timeout=self.timeout)

        self.request = reader.request

        # avoid building capabilities metadata if the
        # response is a ServiceExceptionReport
        se = self._capabilities.find('ServiceException')
        if se is not None:
            err_message = str(se.text).strip()
            raise ServiceException(err_message)

        # build metadata objects
        self._buildMetadata(parse_remote_metadata)

    def _buildMetadata(self, parse_remote_metadata=False):
        '''set up capabilities metadata objects:'''

        self.updateSequence = self._capabilities.attrib.get('updateSequence')

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
        self.contents = OrderedDict()
        caps = self._capabilities.find(nspath('Capability', WMS_NAMESPACE))

        # recursively gather content metadata for all layer elements.
        # To the WebMapService.contents store only metadata of named layers.
        def gather_layers(parent_elem, parent_metadata):
            layers = []
            for index, elem in enumerate(parent_elem.findall(nspath('Layer', WMS_NAMESPACE))):
                cm = ContentMetadata(elem, parent=parent_metadata, index=index + 1,
                                     parse_remote_metadata=parse_remote_metadata)
                if cm.id:
                    if cm.id in self.contents:
                        warnings.warn('Content metadata for layer "%s" already exists. Using child layer' % cm.id)
                    layers.append(cm)
                    self.contents[cm.id] = cm
                cm.children = gather_layers(elem, cm)
            return layers
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

    def getOperationByName(self, name):
        """Return a named content item."""
        for item in self.operations:
            if item.name == name:
                return item
        raise KeyError("No operation named %s" % name)

    def __build_getmap_request(self, layers=None, styles=None, srs=None, bbox=None,
                               format=None, size=None, time=None, dimensions={},
                               elevation=None, transparent=False,
                               bgcolor=None, exceptions=None, **kwargs):

        request = {'service': 'WMS', 'version': self.version, 'request': 'GetMap'}

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
        if srs.upper() == 'EPSG:0':
            # if it's esri's unknown spatial ref code, bail
            raise Exception('Undefined spatial reference (%s).' % srs)

        sref = Crs(srs)
        if sref.axisorder == 'yx':
            # remap the given bbox
            bbox = (bbox[1], bbox[0], bbox[3], bbox[2])

        # remapping the srs to crs for the request
        request['crs'] = str(srs)
        request['bbox'] = ','.join([repr(x) for x in bbox])
        request['format'] = str(format)
        request['transparent'] = str(transparent).upper()
        request['bgcolor'] = '0x' + bgcolor[1:7]
        request['exceptions'] = str(exceptions)

        if time is not None:
            request['time'] = str(time)

        if elevation is not None:
            request['elevation'] = str(elevation)

        # any other specified dimension, prefixed with "dim_"
        for k, v in list(dimensions.items()):
            request['dim_' + k] = str(v)

        if kwargs:
            for kw in kwargs:
                request[kw] = kwargs[kw]
        return request

    def getmap(self, layers=None,
               styles=None,
               srs=None,
               bbox=None,
               format=None,
               size=None,
               time=None,
               elevation=None,
               dimensions={},
               transparent=False,
               bgcolor='#FFFFFF',
               exceptions='XML',
               method='Get',
               timeout=None,
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
            Note: this is an invalid query parameter key for 1.3.0 but is being
                  retained for standardization with 1.1.1.
            Note: throws exception if the spatial ref is ESRI's "no reference"
                  code (EPSG:0)
        bbox : tuple
            (left, bottom, right, top) in srs units (note, this order does not
                change depending on axis order of the crs).

            CRS:84: (long, lat)
            EPSG:4326: (lat, long)
        format : string
            Output image format such as 'image/jpeg'.
        size : tuple
            (width, height) in pixels.

        time : string or list or range
            Optional. Time value of the specified layer as ISO-8601 (per value)
        elevation : string or list or range
            Optional. Elevation value of the specified layer.
        dimensions: dict (dimension : string or list or range)
            Optional. Any other Dimension option, as specified in the GetCapabilities

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
            wms = WebMapService('http://webservices.nationalatlas.gov/wms/1million',\
                                    version='1.3.0')
            img = wms.getmap(layers=['airports1m'],\
                                 styles=['default'],\
                                 srs='EPSG:4326',\
                                 bbox=(-176.646, 17.7016, -64.8017, 71.2854),\
                                 size=(300, 300),\
                                 format='image/jpeg',\
                                 transparent=True)
            out = open('example.jpg.jpg', 'wb')
            out.write(img.read())
            out.close()

        """

        try:
            base_url = next((m.get('url') for m in
                            self.getOperationByName('GetMap').methods if
                            m.get('type').lower() == method.lower()))
        except StopIteration:
            base_url = self.url

        request = self.__build_getmap_request(
            layers=layers,
            styles=styles,
            srs=srs,
            bbox=bbox,
            dimensions=dimensions,
            elevation=elevation,
            format=format,
            size=size,
            time=time,
            transparent=transparent,
            bgcolor=bgcolor,
            exceptions=exceptions,
            **kwargs)

        data = urlencode(request)

        self.request = bind_url(base_url) + data

        u = openURL(base_url, data, method, timeout=timeout or self.timeout, auth=self.auth)

        # need to handle casing in the header keys
        headers = {}
        for k, v in list(u.info().items()):
            headers[k.lower()] = v

        # handle the potential charset def
        if headers.get('content-type', '').split(';')[0] in ['application/vnd.ogc.se_xml', 'text/xml']:
            se_xml = u.read()
            se_tree = etree.fromstring(se_xml)
            err_message = str(se_tree.find(nspath('ServiceException', OGC_NAMESPACE)).text).strip()
            raise ServiceException(err_message)
        return u

    def getfeatureinfo(self, layers=None,
                       styles=None,
                       srs=None,
                       bbox=None,
                       format=None,
                       size=None,
                       time=None,
                       elevation=None,
                       dimensions={},
                       transparent=False,
                       bgcolor='#FFFFFF',
                       exceptions='XML',
                       query_layers=None,
                       xy=None,
                       info_format=None,
                       feature_count=20,
                       method='Get',
                       timeout=None,
                       **kwargs
                       ):
        try:
            base_url = next((m.get('url') for m in self.getOperationByName('GetFeatureInfo').methods
                            if m.get('type').lower() == method.lower()))
        except StopIteration:
            base_url = self.url

        # GetMap-Request
        request = self.__build_getmap_request(
            layers=layers,
            styles=styles,
            srs=srs,
            bbox=bbox,
            dimensions=dimensions,
            elevation=elevation,
            format=format,
            size=size,
            time=time,
            transparent=transparent,
            bgcolor=bgcolor,
            exceptions=exceptions,
            **kwargs)

        # extend to GetFeatureInfo-Request
        request['request'] = 'GetFeatureInfo'

        if not query_layers:
            __str_query_layers = ','.join(layers)
        else:
            __str_query_layers = ','.join(query_layers)

        request['query_layers'] = __str_query_layers
        request['i'] = str(xy[0])
        request['j'] = str(xy[1])
        request['info_format'] = info_format
        request['feature_count'] = str(feature_count)

        data = urlencode(request)

        self.request = bind_url(base_url) + data

        u = openURL(base_url, data, method, timeout=timeout or self.timeout, auth=self.auth)

        # check for service exceptions, and return
        if u.info()['Content-Type'] == 'XML':
            se_xml = u.read()
            se_tree = etree.fromstring(se_xml)
            err_message = str(se_tree.find('ServiceException').text).strip()
            raise ServiceException(err_message)
        return u


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
        self.url = None
        online_resource = self._root.find(nspath('OnlineResource', WMS_NAMESPACE))
        if online_resource is not None:
            self.url = online_resource.attrib.get('{http://www.w3.org/1999/xlink}href', '')
        # contact metadata
        contact = self._root.find(nspath('ContactInformation', WMS_NAMESPACE))
        # sometimes there is a contact block that is empty, so make
        # sure there are children to parse
        if contact is not None and contact[:] != []:
            self.contact = ContactMetadata(contact)
        else:
            self.contact = None


class ContentMetadata(AbstractContentMetadata):

    def __init__(self, elem, parent=None, children=None, index=0, parse_remote_metadata=False,
                 timeout=30, auth=None):
        super(ContentMetadata, self).__init__(auth)

        if xmltag_split(elem.tag) != 'Layer':
            raise ValueError('%s should be a Layer' % (elem,))

        self.parent = parent
        if parent:
            self.index = "%s.%d" % (parent.index, index)
        else:
            self.index = str(index)

        self._children = children

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

        # TODO: what is the preferred response to esri's handling of custom projections
        # in the spatial ref definitions? see
        # http://resources.arcgis.com/en/help/main/10.1/index.html#//00sq000000m1000000
        # and an example (20150812)
        # http://maps.ngdc.noaa.gov/arcgis/services/firedetects/MapServer/WMSServer?request=GetCapabilities&service=WMS

        # bboxes
        b = elem.find(nspath('EX_GeographicBoundingBox', WMS_NAMESPACE))
        self.boundingBoxWGS84 = None
        if b is not None:
            minx = b.find(nspath('westBoundLongitude', WMS_NAMESPACE))
            miny = b.find(nspath('southBoundLatitude', WMS_NAMESPACE))
            maxx = b.find(nspath('eastBoundLongitude', WMS_NAMESPACE))
            maxy = b.find(nspath('northBoundLatitude', WMS_NAMESPACE))
            box = tuple(map(float, [minx.text if minx is not None else None,
                            miny.text if miny is not None else None,
                            maxx.text if maxx is not None else None,
                            maxy.text if maxy is not None else None]))

            self.boundingBoxWGS84 = tuple(box)
        elif self.parent:
            if hasattr(self.parent, 'boundingBoxWGS84'):
                self.boundingBoxWGS84 = self.parent.boundingBoxWGS84

        # make a bbox list (of tuples)
        crs_list = []
        for bb in elem.findall(nspath('BoundingBox', WMS_NAMESPACE)):
            srs_str = bb.attrib.get('CRS', None)
            srs = Crs(srs_str)

            box = tuple(map(float, [bb.attrib['minx'],
                        bb.attrib['miny'],
                        bb.attrib['maxx'],
                        bb.attrib['maxy']]
            ))
            minx, miny, maxx, maxy = box[0], box[1], box[2], box[3]

            # handle the ordering so that it always
            # returns (minx, miny, maxx, maxy)
            if srs and srs.axisorder == 'yx':
                # reverse things
                minx, miny, maxx, maxy = box[1], box[0], box[3], box[2]

            crs_list.append((
                minx, miny, maxx, maxy,
                srs_str,
            ))
        self.crs_list = crs_list
        # and maintain the original boundingBox attribute (first in list)
        # or the wgs84 bbox (to handle cases of incomplete parentage)
        self.boundingBox = crs_list[0] if crs_list else self.boundingBoxWGS84

        # ScaleHint
        self.scaleHint = None
        self.min_scale_denominator = elem.find(nspath('MinScaleDenominator', WMS_NAMESPACE))
        min_scale_hint = 0 if self.min_scale_denominator is None else \
            float(self.min_scale_denominator.text) * SCALEDENOM_TO_RESOLUTION
        self.max_scale_denominator = elem.find(nspath('MaxScaleDenominator', WMS_NAMESPACE))
        max_scale_hint = 0 if self.max_scale_denominator is None else \
            float(self.max_scale_denominator.text) * SCALEDENOM_TO_RESOLUTION
        if self.min_scale_denominator is not None or self.max_scale_denominator is not None:
            self.scaleHint = {'min': min_scale_hint, 'max': max_scale_hint}

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
                self.attribution['logo_url'] = logo.find(
                    nspath('OnlineResource', WMS_NAMESPACE)).attrib['{http://www.w3.org/1999/xlink}href']

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
            for srslist in [x.text for x in elem.findall(nspath('CRS', WMS_NAMESPACE))]:
                if srslist:
                    for srs in srslist.split():
                        self.crsOptions.append(srs)

        # Get rid of duplicate entries
        self.crsOptions = list(set(self.crsOptions))

        # Set self.crsOptions to None if the layer (and parents) had no SRS options
        if len(self.crsOptions) == 0:
            # raise ValueError('%s no SRS available!?' % (elem,))
            # Comment by D Lowe.
            # Do not raise ValueError as it is possible that a layer is purely a parent layer and
            # does not have SRS specified. Instead set crsOptions to None
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
            if name is None and title is None:
                raise ValueError('%s missing name and title' % (s,))
            if name is None or title is None:
                warnings.warn('%s missing name or title' % (s,))
            title_ = title.text if title is not None else name.text
            name_ = name.text if name is not None else title.text
            style = {'title': title_}
            # legend url
            legend = s.find(nspath('LegendURL/OnlineResource', WMS_NAMESPACE))
            if legend is not None:
                style['legend'] = legend.attrib['{http://www.w3.org/1999/xlink}href']

            lgd = s.find(nspath('LegendURL', WMS_NAMESPACE))
            if lgd is not None:
                if 'width' in list(lgd.attrib.keys()):
                    style['legend_width'] = lgd.attrib.get('width')
                if 'height' in list(lgd.attrib.keys()):
                    style['legend_height'] = lgd.attrib.get('height')

                lgd_format = lgd.find(nspath('Format', WMS_NAMESPACE))
                if lgd_format is not None:
                    style['legend_format'] = lgd_format.text.strip()
            self.styles[name_] = style

        # keywords
        self.keywords = [f.text for f in elem.findall(nspath('KeywordList/Keyword', WMS_NAMESPACE))]

        # extents replaced by dimensions of name
        # comment by Soren Scott
        # <Dimension name="elevation" units="meters" default="500" multipleValues="1"
        #    nearestValue="0" current="true" unitSymbol="m">500, 490, 480</Dimension>
        # it can be repeated with the same name so ? this assumes a single one to match 1.1.1

        self.timepositions = None
        self.defaulttimeposition = None
        time_dimension = None

        for dim in elem.findall(nspath('Dimension', WMS_NAMESPACE)):
            dim_name = dim.attrib.get('name')
            if dim_name is not None and dim_name.lower() == 'time':
                time_dimension = dim
        if time_dimension is not None:
            self.timepositions = time_dimension.text.split(',') if time_dimension.text else None
            self.defaulttimeposition = time_dimension.attrib.get('default', None)

        # Elevations - available vertical levels
        self.elevations = None
        elev_dimension = None
        for dim in elem.findall(nspath('Dimension', WMS_NAMESPACE)):
            if dim.attrib.get('name') == 'elevation':
                elev_dimension = dim
        if elev_dimension is not None:
            self.elevations = [e.strip() for e in elev_dimension.text.split(',')] if elev_dimension.text else None

        # and now capture the dimensions as more generic things (and custom things)
        self.dimensions = {}
        for dim in elem.findall(nspath('Dimension', WMS_NAMESPACE)):
            dim_name = dim.attrib.get('name')
            dim_data = {}
            for k, v in list(dim.attrib.items()):
                if k != 'name':
                    dim_data[k] = v
            # single values and ranges are not differentiated here
            dim_data['values'] = dim.text.strip().split(',') if dim.text.strip() else None
            self.dimensions[dim_name] = dim_data

        # MetadataURLs
        self.metadataUrls = []
        for m in elem.findall(nspath('MetadataURL', WMS_NAMESPACE)):
            metadataUrl = {
                'type': testXMLValue(m.attrib['type'], attrib=True),
                'format': testXMLValue(m.find(nspath('Format', WMS_NAMESPACE))),
                'url': testXMLValue(m.find(
                    nspath('OnlineResource', WMS_NAMESPACE)).attrib['{http://www.w3.org/1999/xlink}href'], attrib=True)
            }
            self.metadataUrls.append(metadataUrl)

        if parse_remote_metadata:
            self.parse_remote_metadata(timeout)

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

    def parse_remote_metadata(self, timeout=30):
        """Parse remote metadata for MetadataURL and add it as metadataUrl['metadata']"""
        for metadataUrl in self.metadataUrls:
            if metadataUrl['url'] is not None \
                    and metadataUrl['format'].lower() in ['application/xml', 'text/xml']:  # download URL
                try:
                    content = openURL(
                        metadataUrl['url'], timeout=timeout, auth=self.auth)
                    doc = etree.fromstring(content.read())

                    mdelem = doc.find('.//metadata')
                    if mdelem is not None:
                        metadataUrl['metadata'] = Metadata(mdelem)
                        continue

                    mdelem = doc.find('.//' + nspath_eval('gmd:MD_Metadata', n.get_namespaces(['gmd']))) \
                        or doc.find('.//' + nspath_eval('gmi:MI_Metadata', n.get_namespaces(['gmi'])))
                    if mdelem is not None:
                        metadataUrl['metadata'] = MD_Metadata(mdelem)
                        continue
                except Exception:
                    metadataUrl['metadata'] = None

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, value):
        if self._children is None:
            self._children = value
        else:
            self._children.extend(value)

    def __str__(self):
        return 'Layer Name: %s Title: %s' % (self.name, self.title)


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
