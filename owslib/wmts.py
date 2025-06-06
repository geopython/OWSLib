# -*- coding: UTF-8 -*-
# =============================================================================
# Copyright (C) 2012 Brad Hards <bradh@frogmouth.net>
#
# Based on wms.py, which has the following copyright statement:
# Copyright (c) 2004, 2006 Sean C. Gillies
# Copyright (c) 2005 Nuxeo SARL <http://nuxeo.com>
#
# Authors : Sean Gillies <sgillies@frii.com>
#           Julien Anguenot <ja@nuxeo.com>
#
# Contact email: sgillies@frii.com
# =============================================================================

"""

Abstract
--------
The wmts module of the OWSlib package provides client-side functionality
for fetching tiles from an OGC Web Map Tile Service (WMTS)


Disclaimer
----------
PLEASE NOTE: the owslib wmts module should be considered in early-beta
state: it has been tested against only one WMTS server (NASA EODSIS).
More extensive testing is needed and feedback (to bradh@frogmouth.net)
would be appreciated.

"""

from random import randint
import warnings
from urllib.parse import (urlencode, urlparse, urlunparse, parse_qs,
                          ParseResult)
from .etree import etree
from .util import clean_ows_url, testXMLValue, getXMLInteger, Authentication, openURL, getXMLTree, nspath
from .fgdc import Metadata
from .iso import MD_Metadata
from .ows import ServiceProvider, ServiceIdentification, OperationsMetadata


_OWS_NS = '{http://www.opengis.net/ows/1.1}'
_WMTS_NS = '{http://www.opengis.net/wmts/1.0}'
_XLINK_NS = '{http://www.w3.org/1999/xlink}'

# OpenGIS Web Map Tile Service (WMTS) Implementation Standard
# Version 1.0.0, document 07-057r7

_ABSTRACT_TAG = _OWS_NS + 'Abstract'
_BOUNDING_BOX_TAG = _OWS_NS + 'BoundingBox'
_IDENTIFIER_TAG = _OWS_NS + 'Identifier'
_LOWER_CORNER_TAG = _OWS_NS + 'LowerCorner'
_OPERATIONS_METADATA_TAG = _OWS_NS + 'OperationsMetadata'
_SERVICE_IDENTIFICATION_TAG = _OWS_NS + 'ServiceIdentification'
_SERVICE_PROVIDER_TAG = _OWS_NS + 'ServiceProvider'
_SUPPORTED_CRS_TAG = _OWS_NS + 'SupportedCRS'
_TITLE_TAG = _OWS_NS + 'Title'
_UPPER_CORNER_TAG = _OWS_NS + 'UpperCorner'
_WGS84_BOUNDING_BOX_TAG = _OWS_NS + 'WGS84BoundingBox'

_CONTENTS_TAG = _WMTS_NS + 'Contents'
_FORMAT_TAG = _WMTS_NS + 'Format'
_INFO_FORMAT_TAG = _WMTS_NS + 'InfoFormat'
_LAYER_TAG = _WMTS_NS + 'Layer'
_LAYER_REF_TAG = _WMTS_NS + 'LayerRef'
_MATRIX_HEIGHT_TAG = _WMTS_NS + 'MatrixHeight'
_MATRIX_WIDTH_TAG = _WMTS_NS + 'MatrixWidth'
_MAX_TILE_COL_TAG = _WMTS_NS + 'MaxTileCol'
_MAX_TILE_ROW_TAG = _WMTS_NS + 'MaxTileRow'
_MIN_TILE_COL_TAG = _WMTS_NS + 'MinTileCol'
_MIN_TILE_ROW_TAG = _WMTS_NS + 'MinTileRow'
_RESOURCE_URL_TAG = _WMTS_NS + 'ResourceURL'
_SCALE_DENOMINATOR_TAG = _WMTS_NS + 'ScaleDenominator'
_SERVICE_METADATA_URL_TAG = _WMTS_NS + 'ServiceMetadataURL'

# Table 7, page 20-21, Parts of Style data structure
_STYLE_TAG = _WMTS_NS + 'Style'
_STYLE_LEGEND_URL = _WMTS_NS + 'LegendURL'

# Table 9, page 22-23, Parts of Dimensions data structure
_DIMENSION_TAG = _WMTS_NS + 'Dimension'
_UOM_TAG = _OWS_NS + 'UOM'
_DIMENSION_UNIT_SYMBOL_TAG = _WMTS_NS + 'UnitSymbol'
_DIMENSION_DEFAULT_TAG = _WMTS_NS + 'Default'
_DIMENSION_CURRENT_TAG = _WMTS_NS + 'Current'
_DIMENSION_VALUE_TAG = _WMTS_NS + 'Value'

_THEME_TAG = _WMTS_NS + 'Theme'
_THEMES_TAG = _WMTS_NS + 'Themes'
_TILE_HEIGHT_TAG = _WMTS_NS + 'TileHeight'
_TILE_MATRIX_SET_LINK_TAG = _WMTS_NS + 'TileMatrixSetLink'
_TILE_MATRIX_SET_TAG = _WMTS_NS + 'TileMatrixSet'
_TILE_MATRIX_SET_LIMITS_TAG = _WMTS_NS + 'TileMatrixSetLimits'
_TILE_MATRIX_LIMITS_TAG = _WMTS_NS + 'TileMatrixLimits'
_TILE_MATRIX_TAG = _WMTS_NS + 'TileMatrix'
_TILE_WIDTH_TAG = _WMTS_NS + 'TileWidth'
_TOP_LEFT_CORNER_TAG = _WMTS_NS + 'TopLeftCorner'
_KEYWORDS_TAG = _OWS_NS + 'Keywords'
_KEYWORD_TAG = _OWS_NS + 'Keyword'
_HREF_TAG = _XLINK_NS + 'href'


class ServiceException(Exception):
    """WMTS ServiceException

    Attributes:
        message -- short error message
        xml  -- full xml error message from server
    """

    def __init__(self, message, xml):
        self.message = message
        self.xml = xml

    def __str__(self):
        return repr(self.message)


class CapabilitiesError(Exception):
    pass


class WebMapTileService(object):
    """Abstraction for OGC Web Map Tile Service (WMTS).

    Implements IWebMapService.
    """

    def __getitem__(self, name):
        '''Check contents dictionary to allow dict like access to
        service layers'''
        if name in self.__getattribute__('contents'):
            return self.__getattribute__('contents')[name]
        else:
            raise KeyError("No content named %s" % name)

    def __init__(self, url, version='1.0.0', xml=None, username=None, password=None,
                 parse_remote_metadata=False, vendor_kwargs=None, headers=None, auth=None, cookies=None,
                 timeout=30):
        """Initialize.

        Parameters
        ----------
        url : string
            Base URL for the WMTS service.
        version : string
            Optional WMTS version. Defaults to '1.0.0'.
        xml : string
            Optional XML content to use as the content for the initial
            GetCapabilities request. Typically only used for testing.
        username : string
            Optional user name for authentication.
        password : string
            Optional password for authentication.
        parse_remote_metadata: string
            Currently unused.
        vendor_kwargs : dict
            Optional vendor-specific parameters to be included in all
            requests.
        auth : owslib.util.Authentication
            Instance of Authentication class to hold username/password/cert/verify
        timeout : int
            number of seconds for GetTile request

        """
        self.url = clean_ows_url(url)
        if auth:
            if username:
                auth.username = username
            if password:
                auth.password = password
        self.version = version
        self.vendor_kwargs = vendor_kwargs
        self._capabilities = None
        self.headers = headers
        self.cookies = cookies
        self.auth = auth or Authentication(username, password)
        self.timeout = timeout or 30

        # Authentication handled by Reader
        reader = WMTSCapabilitiesReader(
            self.version, url=self.url, headers=self.headers, auth=self.auth, cookies=self.cookies)
        if xml is not None:  # read from stored xml
            self._capabilities = reader.readString(xml)
        else:  # read from server
            self._capabilities = reader.read(self.url, self.vendor_kwargs)

        # Avoid building capabilities metadata if the response is a
        # ServiceExceptionReport.
        # TODO: check if this needs a namespace
        se = self._capabilities.find('ServiceException')
        if se is not None:
            err_message = str(se.text).strip()
            raise ServiceException(err_message, xml)

        # build metadata objects
        self._buildMetadata(parse_remote_metadata)

    def _getcapproperty(self):
        # TODO: deprecated function. See ticket #453.
        if not self._capabilities:
            reader = WMTSCapabilitiesReader(
                self.version, url=self.url, headers=self.headers, auth=self.auth)
            # xml = reader.read(self.url, self.vendor_kwargs)
            # self._capabilities = ServiceMetadata(xml)
            self._capabilities = reader.read(self.url, self.vendor_kwargs)
        return self._capabilities

    def _buildMetadata(self, parse_remote_metadata=False):
        ''' set up capabilities metadata objects '''

        self.updateSequence = self._capabilities.attrib.get('updateSequence')

        # serviceIdentification metadata
        serviceident = self._capabilities.find(_SERVICE_IDENTIFICATION_TAG)
        if serviceident is not None:
            self.identification = ServiceIdentification(serviceident)

        # serviceProvider metadata
        serviceprov = self._capabilities.find(_SERVICE_PROVIDER_TAG)
        if serviceprov is not None:
            self.provider = ServiceProvider(serviceprov)

        # serviceOperations metadata
        self.operations = []
        serviceop = self._capabilities.find(_OPERATIONS_METADATA_TAG)
        #  REST only WMTS does not have any Operations
        if serviceop is not None:
            for elem in serviceop[:]:
                if elem.tag != nspath('ExtendedCapabilities'):
                    self.operations.append(OperationsMetadata(elem))

        # serviceContents metadata: our assumption is that services use
        # a top-level layer as a metadata organizer, nothing more.
        self.contents = {}
        caps = self._capabilities.find(_CONTENTS_TAG)

        def gather_layers(parent_elem, parent_metadata):
            for index, elem in enumerate(parent_elem.findall(_LAYER_TAG)):
                cm = ContentMetadata(
                    elem, parent=parent_metadata, index=index + 1,
                    parse_remote_metadata=parse_remote_metadata)
                if cm.id:
                    if cm.id in self.contents:
                        msg = ('Content metadata for layer "%s" '
                               'already exists' % cm.id)
                        warnings.warn(msg, RuntimeWarning)
                    self.contents[cm.id] = cm
                gather_layers(elem, cm)
        gather_layers(caps, None)

        self.tilematrixsets = {}
        for elem in caps.findall(_TILE_MATRIX_SET_TAG):
            tms = TileMatrixSet(elem)
            if tms.identifier:
                if tms.identifier in self.tilematrixsets:
                    msg = ('TileMatrixSet with identifier "%s" '
                           'already exists' % tms.identifier)
                    warnings.warn(msg, RuntimeWarning)
                self.tilematrixsets[tms.identifier] = tms

        self.themes = {}
        for elem in self._capabilities.findall(_THEMES_TAG + '/' + _THEME_TAG):
            theme = Theme(elem)
            if theme.identifier:
                if theme.identifier in self.themes:
                    msg = ('Theme with identifier "%s" already exists'
                           % theme.identifier)
                    warnings.warn(msg, RuntimeWarning)
                self.themes[theme.identifier] = theme

        serviceMetadataURL = self._capabilities.find(_SERVICE_METADATA_URL_TAG)
        if serviceMetadataURL is not None:
            self.serviceMetadataURL = serviceMetadataURL.attrib[_HREF_TAG]
        else:
            self.serviceMetadataURL = None

    def items(self):
        '''supports dict-like items() access'''
        items = []
        for item in self.contents:
            items.append((item, self.contents[item]))
        return items

    def buildTileRequest(self, layer=None, style=None, format=None,
                         tilematrixset=None, tilematrix=None, row=None,
                         column=None, **kwargs):
        """Return the URL-encoded parameters for a GetTile request.

        Parameters
        ----------
        layer : string
            Content layer name.
        style : string
            Optional style name. Defaults to the first style defined for
            the relevant layer in the GetCapabilities response.
        format : string
            Optional output image format,  such as 'image/jpeg'.
            Defaults to the first format defined for the relevant layer
            in the GetCapabilities response.
        tilematrixset : string
            Optional name of tile matrix set to use.
            Defaults to the first tile matrix set defined for the
            relevant layer in the GetCapabilities response.
        tilematrix : string
            Name of the tile matrix to use.
        row : integer
            Row index of tile to request.
        column : integer
            Column index of tile to request.
        **kwargs : extra arguments
            anything else e.g. vendor specific parameters
        """

        if (layer is None):
            raise ValueError("layer is mandatory (cannot be None)")
        if style is None:
            style = list(self[layer].styles.keys())[0]
        if format is None:
            format = self[layer].formats[0]
        if tilematrixset is None:
            tilematrixset = sorted(self[layer].tilematrixsetlinks.keys())[0]
        if tilematrix is None:
            msg = 'tilematrix (zoom level) is mandatory (cannot be None)'
            raise ValueError(msg)
        if row is None:
            raise ValueError("row is mandatory (cannot be None)")
        if column is None:
            raise ValueError("column is mandatory (cannot be None)")

        request = list()
        request.append(('SERVICE', 'WMTS'))
        request.append(('REQUEST', 'GetTile'))
        request.append(('VERSION', '1.0.0'))
        request.append(('LAYER', layer))
        request.append(('STYLE', style))
        request.append(('TILEMATRIXSET', tilematrixset))
        request.append(('TILEMATRIX', tilematrix))
        request.append(('TILEROW', str(row)))
        request.append(('TILECOL', str(column)))
        request.append(('FORMAT', format))

        for key, value in list(kwargs.items()):
            request.append((key, value))

        data = urlencode(request, True)
        return data

    def buildTileResource(self, layer=None, style=None, format=None,
                          tilematrixset=None, tilematrix=None, row=None,
                          column=None, **kwargs):

        # check the validity of the parameters and set reasonable defaults
        if layer is None:
            raise ValueError("layer is mandatory (cannot be None)")
        if style is None:
            style = list(self[layer].styles.keys())[0]
        if tilematrixset is None:
            tilematrixset = sorted(self[layer].tilematrixsetlinks.keys())[0]
        if tilematrix is None:
            msg = 'tilematrix (zoom level) is mandatory (cannot be None)'
            raise ValueError(msg)
        if row is None:
            raise ValueError("row is mandatory (cannot be None)")
        if column is None:
            raise ValueError("column is mandatory (cannot be None)")

        tileresourceurls = []
        for resourceURL in self[layer].resourceURLs:
            if resourceURL['resourceType'] == 'tile':
                tileresourceurls.append(resourceURL)
        numres = len(tileresourceurls)
        if numres > 0:
            # choose random ResourceURL if more than one available
            resindex = randint(0, numres - 1)
            resurl = tileresourceurls[resindex]['template']
            return resurl.format(
                TileMatrixSet=tilematrixset,
                TileMatrix=tilematrix,
                TileRow=str(row),
                TileCol=str(column),
                Style=style,
                **kwargs
            )

        return None

    @property
    def restonly(self):

        # if OperationsMetadata is missing completely --> use REST
        if len(self.operations) == 0:
            return True

        # check if KVP or RESTful are available
        restenc = False
        kvpenc = False
        for operation in self.operations:
            if operation.name == 'GetTile':
                for method in operation.methods:
                    if 'kvp' in str(method['constraints']).lower():
                        kvpenc = True
                    if 'rest' in str(method['constraints']).lower():
                        restenc = True

        # if KVP is available --> use KVP
        if kvpenc:
            return False

        # if the operation has no constraint --> use KVP
        if not kvpenc and not restenc:
            return False

        return restenc

    def gettile(self, base_url=None, layer=None, style=None, format=None,
                tilematrixset=None, tilematrix=None, row=None, column=None,
                **kwargs):
        """Return a tile from the WMTS.

        Returns the tile image as a file-like object.

        Parameters
        ----------
        base_url : string
            Optional URL for request submission. Defaults to the URL of
            the GetTile operation as declared in the GetCapabilities
            response.
        layer : string
            Content layer name.
        style : string
            Optional style name. Defaults to the first style defined for
            the relevant layer in the GetCapabilities response.
        format : string
            Optional output image format,  such as 'image/jpeg'.
            Defaults to the first format defined for the relevant layer
            in the GetCapabilities response.
        tilematrixset : string
            Optional name of tile matrix set to use.
            Defaults to the first tile matrix set defined for the
            relevant layer in the GetCapabilities response.
        tilematrix : string
            Name of the tile matrix to use.
        row : integer
            Row index of tile to request.
        column : integer
            Column index of tile to request.
        **kwargs : extra arguments
            anything else e.g. vendor specific parameters
        """
        vendor_kwargs = self.vendor_kwargs or {}
        vendor_kwargs.update(kwargs)

        # REST only WMTS
        if self.restonly:
            resurl = self.buildTileResource(
                layer, style, format, tilematrixset, tilematrix,
                row, column, **vendor_kwargs)
            u = openURL(resurl, headers=self.headers, cookies=self.cookies, auth=self.auth, timeout=self.timeout)
            return u

        # KVP implemetation
        data = self.buildTileRequest(layer, style, format, tilematrixset,
                                     tilematrix, row, column, **vendor_kwargs)

        if base_url is None:
            base_url = self.url
            try:
                methods = self.getOperationByName('GetTile').methods
                get_verbs = [x for x in methods
                             if x.get('type').lower() == 'get']
                if len(get_verbs) > 1:
                    # Filter by constraints
                    base_url = next(
                        x for x in filter(
                            list,
                            ([pv.get('url')
                                for const in pv.get('constraints')
                                if 'kvp' in [x.lower() for x in const.values]]
                             for pv in get_verbs if pv.get('constraints'))))[0]
                elif len(get_verbs) == 1:
                    base_url = get_verbs[0].get('url')
            except StopIteration:
                pass
        u = openURL(base_url, data, headers=self.headers, cookies=self.cookies, auth=self.auth, timeout=self.timeout)

        # check for service exceptions, and return
        if u.info()['Content-Type'] == 'application/vnd.ogc.se_xml':
            se_xml = u.read()
            se_tree = etree.fromstring(se_xml)
            err_message = str(se_tree.find('ServiceException').text)
            raise ServiceException(err_message.strip(), se_xml)
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


class TileMatrixSet(object):
    '''Holds one TileMatrixSet'''
    def __init__(self, elem):
        if elem.tag != _TILE_MATRIX_SET_TAG:
            raise ValueError('%s should be a TileMatrixSet' % (elem,))
        self.identifier = testXMLValue(elem.find(_IDENTIFIER_TAG)).strip()
        self.crs = testXMLValue(elem.find(_SUPPORTED_CRS_TAG)).strip()
        if self.crs is None or self.identifier is None:
            raise ValueError('%s incomplete TileMatrixSet' % (elem,))
        self.tilematrix = {}
        for tilematrix in elem.findall(_TILE_MATRIX_TAG):
            tm = TileMatrix(tilematrix)
            if tm.identifier:
                if tm.identifier in self.tilematrix:
                    msg = ('TileMatrix with identifier "%s" '
                           'already exists' % tm.identifier)
                    warnings.warn(msg, RuntimeWarning)
                self.tilematrix[tm.identifier] = tm


class TileMatrix(object):
    '''Holds one TileMatrix'''
    def __init__(self, elem):
        if elem.tag != _TILE_MATRIX_TAG:
            raise ValueError('%s should be a TileMatrix' % (elem,))
        self.identifier = testXMLValue(elem.find(_IDENTIFIER_TAG)).strip()
        sd = testXMLValue(elem.find(_SCALE_DENOMINATOR_TAG))
        if sd is None:
            raise ValueError('%s is missing ScaleDenominator' % (elem,))
        self.scaledenominator = float(sd)
        tl = testXMLValue(elem.find(_TOP_LEFT_CORNER_TAG))
        if tl is None:
            raise ValueError('%s is missing TopLeftCorner' % (elem,))
        (lon, lat) = tl.split(" ")
        self.topleftcorner = (float(lon), float(lat))
        width = testXMLValue(elem.find(_TILE_WIDTH_TAG))
        height = testXMLValue(elem.find(_TILE_HEIGHT_TAG))
        if (width is None) or (height is None):
            msg = '%s is missing TileWidth and/or TileHeight' % (elem,)
            raise ValueError(msg)
        self.tilewidth = int(width)
        self.tileheight = int(height)
        mw = testXMLValue(elem.find(_MATRIX_WIDTH_TAG))
        mh = testXMLValue(elem.find(_MATRIX_HEIGHT_TAG))
        if (mw is None) or (mh is None):
            msg = '%s is missing MatrixWidth and/or MatrixHeight' % (elem,)
            raise ValueError(msg)
        self.matrixwidth = int(mw)
        self.matrixheight = int(mh)


class Theme:
    """
    Abstraction for a WMTS theme
    """
    def __init__(self, elem):
        if elem.tag != _THEME_TAG:
            raise ValueError('%s should be a Theme' % (elem,))
        self.identifier = testXMLValue(elem.find(_IDENTIFIER_TAG)).strip()
        title = testXMLValue(elem.find(_TITLE_TAG))
        if title is not None:
            self.title = title.strip()
        else:
            self.title = None
        abstract = testXMLValue(elem.find(_ABSTRACT_TAG))
        if abstract is not None:
            self.abstract = abstract.strip()
        else:
            self.abstract = None

        self.layerRefs = []
        layerRefs = elem.findall(_LAYER_REF_TAG)
        for layerRef in layerRefs:
            if layerRef.text is not None:
                self.layerRefs.append(layerRef.text)


class TileMatrixLimits(object):
    """
    Represents a WMTS TileMatrixLimits element.

    """
    def __init__(self, elem):
        if elem.tag != _TILE_MATRIX_LIMITS_TAG:
            raise ValueError('%s should be a TileMatrixLimits' % elem)

        tm = elem.find(_TILE_MATRIX_TAG)
        if tm is None:
            raise ValueError('Missing TileMatrix in %s' % elem)
        self.tilematrix = tm.text.strip()

        self.mintilerow = getXMLInteger(elem, _MIN_TILE_ROW_TAG)
        self.maxtilerow = getXMLInteger(elem, _MAX_TILE_ROW_TAG)
        self.mintilecol = getXMLInteger(elem, _MIN_TILE_COL_TAG)
        self.maxtilecol = getXMLInteger(elem, _MAX_TILE_COL_TAG)

    def __repr__(self):
        fmt = ('<TileMatrixLimits: {self.tilematrix}'
               ', minRow={self.mintilerow}, maxRow={self.maxtilerow}'
               ', minCol={self.mintilecol}, maxCol={self.maxtilecol}>')
        return fmt.format(self=self)


class TileMatrixSetLink(object):
    """
    Represents a WMTS TileMatrixSetLink element.

    """
    @staticmethod
    def from_elements(link_elements):
        """
        Return a list of TileMatrixSetLink instances derived from the
        given list of <TileMatrixSetLink> XML elements.

        """
        # NB. The WMTS spec is contradictory re. the multiplicity
        # relationships between Layer and TileMatrixSetLink, and
        # TileMatrixSetLink and tileMatrixSet (URI).
        # Try to figure out which model has been used by the server.
        links = []
        for link_element in link_elements:
            matrix_set_elements = link_element.findall(_TILE_MATRIX_SET_TAG)
            if len(matrix_set_elements) == 0:
                raise ValueError('Missing TileMatrixSet in %s' % link_element)
            elif len(matrix_set_elements) > 1:
                set_limits_elements = link_element.findall(
                    _TILE_MATRIX_SET_LIMITS_TAG)
                if set_limits_elements:
                    raise ValueError('Multiple instances of TileMatrixSet'
                                     ' plus TileMatrixSetLimits in %s' %
                                     link_element)
                for matrix_set_element in matrix_set_elements:
                    uri = matrix_set_element.text.strip()
                    links.append(TileMatrixSetLink(uri))
            else:
                uri = matrix_set_elements[0].text.strip()

                tilematrixlimits = {}
                path = '%s/%s' % (_TILE_MATRIX_SET_LIMITS_TAG,
                                  _TILE_MATRIX_LIMITS_TAG)
                for limits_element in link_element.findall(path):
                    tml = TileMatrixLimits(limits_element)
                    if tml.tilematrix:
                        if tml.tilematrix in tilematrixlimits:
                            msg = ('TileMatrixLimits with tileMatrix "%s" '
                                   'already exists' % tml.tilematrix)
                            warnings.warn(msg, RuntimeWarning)
                        tilematrixlimits[tml.tilematrix] = tml

                links.append(TileMatrixSetLink(uri, tilematrixlimits))
        return links

    def __init__(self, tilematrixset, tilematrixlimits=None):
        self.tilematrixset = tilematrixset

        if tilematrixlimits is None:
            self.tilematrixlimits = {}
        else:
            self.tilematrixlimits = tilematrixlimits

    def __repr__(self):
        fmt = ('<TileMatrixSetLink: {self.tilematrixset}'
               ', tilematrixlimits={{...}}>')
        return fmt.format(self=self)


class BoundingBox(object):
    """
    Represents a BoundingBox element
    """

    def __init__(self, elem) -> None:
        if elem.tag != _BOUNDING_BOX_TAG:
            raise ValueError('%s should be a BoundingBox' % elem)

        lc = elem.find(_LOWER_CORNER_TAG)
        uc = elem.find(_UPPER_CORNER_TAG)

        self.ll = [float(s) for s in lc.text.split()]
        self.ur = [float(s) for s in uc.text.split()]

        self.crs = elem.attrib.get('crs')
        self.extent = (self.ll[0], self.ll[1], self.ur[0], self.ur[1])

    def __repr__(self):
        fmt = ('<BoundingBox'
               ', crs={self.crs}'
               ', extent={self.extent}>')
        return fmt.format(self=self)


class ContentMetadata:
    """
    Abstraction for WMTS layer metadata.

    Implements IContentMetadata.
    """
    def __init__(self, elem, parent=None, index=0, parse_remote_metadata=False):
        if elem.tag != _LAYER_TAG:
            raise ValueError('%s should be a Layer' % (elem,))

        self.parent = parent
        if parent:
            self.index = "%s.%d" % (parent.index, index)
        else:
            self.index = str(index)

        self.id = self.name = testXMLValue(elem.find(_IDENTIFIER_TAG))
        # title is mandatory property
        self.title = None
        title = testXMLValue(elem.find(_TITLE_TAG))
        if title is not None:
            self.title = title.strip()

        self.abstract = testXMLValue(elem.find(_ABSTRACT_TAG))

        # Bounding boxes
        # There may be multiple, using different CRSes
        self.boundingBox = []

        bbs = elem.findall(_BOUNDING_BOX_TAG)
        for b in bbs:
            self.boundingBox.append(BoundingBox(b))

        # WGS84 Bounding box
        b = elem.find(_WGS84_BOUNDING_BOX_TAG)
        if b is not None:
            lc = b.find(_LOWER_CORNER_TAG)
            uc = b.find(_UPPER_CORNER_TAG)
            ll = [float(s) for s in lc.text.split()]
            ur = [float(s) for s in uc.text.split()]
            self.boundingBoxWGS84 = (ll[0], ll[1], ur[0], ur[1])
        # TODO: there is probably some more logic here, and it should
        # probably be shared code

        self._tilematrixsets = [f.text.strip() for f in
                                elem.findall(_TILE_MATRIX_SET_LINK_TAG + '/' + _TILE_MATRIX_SET_TAG)]

        link_elements = elem.findall(_TILE_MATRIX_SET_LINK_TAG)
        tile_matrix_set_links = TileMatrixSetLink.from_elements(link_elements)
        self.tilematrixsetlinks = {}
        for tmsl in tile_matrix_set_links:
            if tmsl.tilematrixset:
                if tmsl.tilematrixset in self.tilematrixsetlinks:
                    msg = ('TileMatrixSetLink with tilematrixset "%s"'
                           ' already exists' % tmsl.tilematrixset)
                    warnings.warn(msg, RuntimeWarning)
                self.tilematrixsetlinks[tmsl.tilematrixset] = tmsl

        self.resourceURLs = []
        for resourceURL in elem.findall(_RESOURCE_URL_TAG):
            resource = {}
            for attrib in ['format', 'resourceType', 'template']:
                resource[attrib] = resourceURL.attrib[attrib]
            self.resourceURLs.append(resource)

        # Styles
        self.styles = {}
        for s in elem.findall(_STYLE_TAG):
            style = {}
            isdefaulttext = s.attrib.get('isDefault')
            style['isDefault'] = (isdefaulttext == "true")
            identifier = s.find(_IDENTIFIER_TAG)  # one and mandatory
            if identifier is None:
                raise ValueError('%s missing identifier' % (s,))

            title = s.find(_TITLE_TAG)
            if title is not None:
                style['title'] = testXMLValue(title)

            abstract = s.find(_ABSTRACT_TAG)
            if abstract is not None:
                style['abstract'] = testXMLValue(abstract)

            legendURL = s.find(_STYLE_LEGEND_URL)
            if legendURL is not None:
                style['legend'] = legendURL.attrib[_HREF_TAG]
                if 'width' in list(legendURL.attrib.keys()):
                    style['width'] = legendURL.attrib.get('width')
                if 'height' in list(legendURL.attrib.keys()):
                    style['height'] = legendURL.attrib.get('height')
                if 'format' in list(legendURL.attrib.keys()):
                    style['format'] = legendURL.attrib.get('format')

            keywords = [f.text for f in s.findall(
                        _KEYWORDS_TAG + '/' + _KEYWORD_TAG)]
            if keywords:  # keywords is a list []
                style['keywords'] = keywords

            self.styles[identifier.text] = style

        self.formats = [f.text for f in elem.findall(_FORMAT_TAG)]

        self.keywords = [f.text for f in elem.findall(
                         _KEYWORDS_TAG + '/' + _KEYWORD_TAG)]
        self.infoformats = [f.text for f in elem.findall(_INFO_FORMAT_TAG)]

        self.dimensions = {}
        for dim in elem.findall(_DIMENSION_TAG):
            dimension = {}

            identifier = dim.find(_IDENTIFIER_TAG)
            if identifier is None:
                # mandatory parameter
                raise ValueError('%s missing identifier' % (dim,))
            if identifier.text in self.dimensions:
                # domain identifier SHALL be unique
                warnings.warn('%s identifier duplicated, taking first occurence' % (dim,))
                continue

            values = [f.text for f in dim.findall(_DIMENSION_VALUE_TAG)]
            if len(values) == 0:
                raise ValueError(
                    '%s list of values can not be empty' % (dim,)
                )
            dimension['values'] = values

            title = dim.find(_TITLE_TAG)
            if title is not None:
                dimension['title'] = title.text

            abstract = dim.find(_ABSTRACT_TAG)
            if abstract is not None:
                dimension['abstract'] = abstract.text

            keywords = [
                f.text for f in dim.findall(_KEYWORDS_TAG + '/' + _KEYWORD_TAG)
            ]
            if keywords:
                dimension['keywords'] = keywords

            uom = dim.find(_UOM_TAG)
            if uom is not None:
                dimension['UOM'] = uom.text

            unit_symbol = dim.find(_DIMENSION_UNIT_SYMBOL_TAG)
            if unit_symbol is not None:
                dimension['unit_symbol'] = unit_symbol.text

            default_value = dim.find(_DIMENSION_DEFAULT_TAG)
            if default_value in ['default', 'current', '', None]:
                # mandatory parameter
                raise ValueError(
                    '%s default value must not be empty or \'default\' or \'current\''
                    % (dim,)
                )
            dimension['default'] = default_value.text

            current = dim.find(_DIMENSION_CURRENT_TAG)
            if current and current.text == 'true':
                dimension['current'] = True
            else:
                dimension['current'] = False

            self.dimensions[identifier.text] = dimension

        self.layers = []
        for child in elem.findall(_LAYER_TAG):
            self.layers.append(ContentMetadata(child, self))

    @property
    def tilematrixsets(self):
        # NB. This attribute has been superseeded by the
        # `tilematrixsetlinks` attribute defined below, but is included
        # for now to provide continuity.
        warnings.warn("The 'tilematrixsets' attribute has been deprecated"
                      " and will be removed in a future version of OWSLib."
                      " Please use 'tilematrixsetlinks' instead.")
        return self._tilematrixsets

    def __str__(self):
        return 'Layer Name: %s Title: %s' % (self.name, self.title)


class WMTSCapabilitiesReader:
    """Read and parse capabilities document into a lxml.etree infoset
    """

    def __init__(self, version='1.0.0', url=None, un=None, pw=None, headers=None, auth=None, cookies=None):
        """Initialize"""
        self.version = version
        self._infoset = None
        self.url = url
        if auth:
            if un:
                auth.username = un
            if pw:
                auth.password = pw
        self.auth = auth or Authentication(un, pw)
        self.headers = headers
        self.cookies = cookies

    def capabilities_url(self, service_url, vendor_kwargs=None):
        """Return a capabilities url
        """
        # Ensure the 'service', 'request', and 'version' parameters,
        # and any vendor-specific parameters are included in the URL.
        pieces = urlparse(service_url)
        args = parse_qs(pieces.query)
        if 'service' not in args:
            args['service'] = 'WMTS'
        if 'request' not in args:
            args['request'] = 'GetCapabilities'
        if 'version' not in args:
            args['version'] = self.version
        if vendor_kwargs:
            args.update(vendor_kwargs)
        query = urlencode(args, doseq=True)
        pieces = ParseResult(pieces.scheme, pieces.netloc,
                             pieces.path, pieces.params,
                             query, pieces.fragment)
        return urlunparse(pieces)

    def read(self, service_url, vendor_kwargs=None):
        """Get and parse a WMTS capabilities document, returning an
        elementtree instance

        service_url is the base url, to which is appended the service,
        version, and request parameters. Optional vendor-specific
        parameters can also be supplied as a dict.
        """
        getcaprequest = self.capabilities_url(service_url, vendor_kwargs)

        # now split it up again to use the generic openURL function...
        spliturl = getcaprequest.split('?')
        u = openURL(spliturl[0], spliturl[1], method='Get', cookies=self.cookies, headers=self.headers, auth=self.auth)
        return getXMLTree(u)

    def readString(self, st):
        """Parse a WMTS capabilities document, returning an elementtree instance

        string should be an XML capabilities document
        """
        if not isinstance(st, str) and not isinstance(st, bytes):
            msg = 'String must be of type string or bytes, not %s' % type(st)
            raise ValueError(msg)
        return etree.fromstring(st)
