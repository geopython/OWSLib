# -*- coding: utf-8 -*-
# =============================================================================
# Copyright (c) 2011 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

from io import BytesIO
from urllib.parse import urlencode
from owslib.util import (
    testXMLValue,
    nspath_eval,
    ServiceException,
    Authentication,
    # openURL,
)
from owslib.etree import etree
from owslib.fgdc import Metadata
from owslib.iso import MD_Metadata
from owslib.ows import (
    OwsCommon,
    ServiceIdentification,
    ServiceProvider,
    Constraint,
    Parameter,
    OperationsMetadata,
    BoundingBox
)
from owslib.fes import FilterCapabilities
from owslib.crs import Crs
from owslib.feature import WebFeatureService_
from owslib.feature.common import (
    WFSCapabilitiesReader,
    AbstractContentMetadata,
)
from owslib.namespaces import Namespaces
from owslib.util import log, openURL


def get_namespaces():
    n = Namespaces()
    return n.get_namespaces(["gmd", "gml", "gmi", "ogc", "ows", "wfs"])


namespaces = get_namespaces()


class WebFeatureService_1_1_0(WebFeatureService_):
    """Abstraction for OGC Web Feature Service (WFS).

    Implements IWebFeatureService.
    """

    def __new__(
        self,
        url,
        version,
        xml,
        parse_remote_metadata=False,
        timeout=30,
        headers=None,
        username=None,
        password=None,
        auth=None,
    ):
        """ overridden __new__ method

        @type url: string
        @param url: url of WFS capabilities document
        @type xml: string
        @param xml: elementtree object
        @type parse_remote_metadata: boolean
        @param parse_remote_metadata: whether to fully process MetadataURL elements
        @param headers: HTTP headers to send with requests
        @param timeout: time (in seconds) after which requests should timeout
        @param username: service authentication username
        @param password: service authentication password
        @param auth: instance of owslib.util.Authentication
        @return: initialized WebFeatureService_1_1_0 object
        """
        obj = object.__new__(self)
        obj.__init__(
            url,
            version,
            xml,
            parse_remote_metadata,
            timeout,
            headers=headers,
            username=username,
            password=password,
            auth=auth,
        )
        return obj

    def __getitem__(self, name):
        """ check contents dictionary to allow dict like access to service layers"""
        if name in list(self.__getattribute__("contents").keys()):
            return self.__getattribute__("contents")[name]
        else:
            raise KeyError("No content named %s" % name)

    def __init__(
        self,
        url,
        version,
        xml=None,
        parse_remote_metadata=False,
        timeout=30,
        headers=None,
        username=None,
        password=None,
        auth=None,
    ):
        """Initialize."""
        if auth:
            if username:
                auth.username = username
            if password:
                auth.password = password
        else:
            auth = Authentication(username, password)
        super(WebFeatureService_1_1_0, self).__init__(auth)
        self.url = url
        self.version = version
        self.headers = headers
        self.timeout = timeout
        self._capabilities = None
        self.owscommon = OwsCommon("1.0.0")
        reader = WFSCapabilitiesReader(self.version, headers=self.headers, auth=self.auth)
        if xml:
            self._capabilities = reader.readString(xml)
        else:
            self._capabilities = reader.read(self.url, self.timeout)
        self._buildMetadata(parse_remote_metadata)

    def _buildMetadata(self, parse_remote_metadata=False):
        """set up capabilities metadata objects: """

        self.updateSequence = self._capabilities.attrib.get("updateSequence")

        # ServiceIdentification
        val = self._capabilities.find(
            nspath_eval("ows:ServiceIdentification", namespaces)
        )
        if val is not None:
            self.identification = ServiceIdentification(val, self.owscommon.namespace)
        # ServiceProvider
        val = self._capabilities.find(
            nspath_eval("ows:ServiceProvider", namespaces)
        )
        if val is not None:
            self.provider = ServiceProvider(val, self.owscommon.namespace)
        # ServiceOperations metadata
        self.operations = []
        for elem in self._capabilities.findall(
            nspath_eval("ows:OperationsMetadata/ows:Operation", namespaces)
        ):
            self.operations.append(OperationsMetadata(elem, self.owscommon.namespace))
        self.constraints = {}
        for elem in self._capabilities.findall(
            nspath_eval("ows:OperationsMetadata/ows:Constraint", namespaces)
        ):
            self.constraints[elem.attrib["name"]] = Constraint(
                elem, self.owscommon.namespace
            )
        self.parameters = {}
        for elem in self._capabilities.findall(
            nspath_eval("ows:OperationsMetadata/ows:Parameter", namespaces)
        ):
            self.parameters[elem.attrib["name"]] = Parameter(
                elem, self.owscommon.namespace
            )

        # FilterCapabilities
        val = self._capabilities.find(
            nspath_eval("ogc:Filter_Capabilities", namespaces)
        )
        self.filters = FilterCapabilities(val)

        # serviceContents metadata: our assumption is that services use a top-level
        # layer as a metadata organizer, nothing more.

        self.contents = {}
        features = self._capabilities.findall(
            nspath_eval("wfs:FeatureTypeList/wfs:FeatureType", namespaces)
        )
        if features is not None:
            for feature in features:
                cm = ContentMetadata(feature, parse_remote_metadata, headers=self.headers, auth=self.auth)
                self.contents[cm.id] = cm

        # exceptions
        self.exceptions = [
            f.text for f in self._capabilities.findall("Capability/Exception/Format")
        ]

    def getcapabilities(self):
        """Request and return capabilities document from the WFS as a
        file-like object.
        NOTE: this is effectively redundant now"""
        reader = WFSCapabilitiesReader(self.version, auth=self.auth)
        return openURL(
            reader.capabilities_url(self.url), timeout=self.timeout,
            headers=self.headers, auth=self.auth
        )

    def items(self):
        """supports dict-like items() access"""
        items = []
        for item in self.contents:
            items.append((item, self.contents[item]))
        return items

    def getfeature(
        self,
        typename=None,
        filter=None,
        bbox=None,
        featureid=None,
        featureversion=None,
        propertyname=None,
        maxfeatures=None,
        srsname=None,
        outputFormat=None,
        method="Get",
        startindex=None,
        sortby=None,
    ):
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
            List of feature property names. For Get request, '*' matches all.
            For Post request, leave blank (None) to get all properties.
        maxfeatures : int
            Maximum number of features to be returned.
        method : string
            Qualified name of the HTTP DCP method to use.
        srsname: string
            EPSG code to request the data in
        outputFormat: string (optional)
            Requested response format of the request.
        startindex: int (optional)
            Start position to return feature set (paging in combination with maxfeatures)
        sortby: list (optional)
            List of property names whose values should be used to order
            (upon presentation) the set of feature instances that
            satify the query.

        There are 3 different modes of use

        1) typename and bbox (simple spatial query). It is assumed, that
            bbox coordinates are given *always* in the east,north order
        2) typename and filter (more expressive)
        3) featureid (direct access to known features)
        """
        try:
            base_url = next(
                (
                    m.get("url")
                    for m in self.getOperationByName("GetFeature").methods
                    if m.get("type").lower() == method.lower()
                )
            )
        except StopIteration:
            base_url = self.url
        request = {"service": "WFS", "version": self.version, "request": "GetFeature"}

        if method.lower() == "get":
            if not isinstance(typename, list):
                typename = [typename]

            if srsname is not None:
                request["srsname"] = str(srsname)

                # Check, if desired SRS is supported by the service for each
                # typename. Warning will be thrown if that SRS is not allowed."
                for name in typename:
                    _ = self.getSRS(srsname, name)

            # check featureid
            if featureid:
                request["featureid"] = ",".join(featureid)

            # bbox
            elif bbox and typename:
                request["bbox"] = self.getBBOXKVP(bbox, typename)

            # or filter
            elif filter and typename:
                request["filter"] = str(filter)

            assert len(typename) > 0
            request["typename"] = ",".join(typename)

            if propertyname is None:
                propertyname = "*"

            if not isinstance(propertyname, list):
                propertyname = [propertyname]
            request["propertyname"] = ",".join(propertyname)

            if sortby is not None:
                if not isinstance(sortby, list):
                    sortby = [sortby]
                request["sortby"] = ",".join(sortby)

            if featureversion is not None:
                request["featureversion"] = str(featureversion)
            if maxfeatures is not None:
                request["maxfeatures"] = str(maxfeatures)
            if startindex is not None:
                request["startindex"] = str(startindex)
            if outputFormat is not None:
                request["outputFormat"] = outputFormat

            data = urlencode(request)
            log.debug("Making request: %s?%s" % (base_url, data))

        elif method.lower() == "post":
            base_url, data = self.getPOSTGetFeatureRequest(
                typename=typename,
                filter=filter,
                bbox=bbox,
                featureid=featureid,
                featureversion=featureversion,
                propertyname=propertyname,
                maxfeatures=maxfeatures,
                outputFormat=outputFormat,
                method='Post',
                startindex=startindex,
                sortby=sortby,
            )

        u = openURL(base_url, data, method, timeout=self.timeout,
                    headers=self.headers, auth=self.auth)

        # check for service exceptions, rewrap, and return
        # We're going to assume that anything with a content-length > 32k
        # is data. We'll check anything smaller.
        if "Content-Length" in u.info():
            length = int(u.info()["Content-Length"])
            have_read = False
        else:
            data = u.read()
            have_read = True
            length = len(data)

        if length < 32000:
            if not have_read:
                data = u.read()

            try:
                tree = etree.fromstring(data)
            except BaseException:
                # Not XML
                return BytesIO(data)
            else:
                if tree.tag == "{%s}ServiceExceptionReport" % namespaces["ogc"]:
                    se = tree.find(nspath_eval("ServiceException", namespaces["ogc"]))
                    raise ServiceException(str(se.text).strip())
                else:
                    return BytesIO(data)
        else:
            if have_read:
                return BytesIO(data)
            return u

    def getOperationByName(self, name):
        """Return a named content item."""
        for item in self.operations:
            if item.name == name:
                return item
        raise KeyError("No operation named %s" % name)


class ContentMetadata(AbstractContentMetadata):
    """Abstraction for WFS metadata.

    Implements IMetadata.
    """

    def __init__(self, elem, parse_remote_metadata=False, timeout=30, headers=None, auth=None):
        """."""
        super(ContentMetadata, self).__init__(headers=headers, auth=auth)
        self.id = testXMLValue(elem.find(nspath_eval("wfs:Name", namespaces)))
        self.title = testXMLValue(elem.find(nspath_eval("wfs:Title", namespaces)))
        self.abstract = testXMLValue(elem.find(nspath_eval("wfs:Abstract", namespaces)))
        self.keywords = [
            f.text
            for f in elem.findall(nspath_eval("ows:Keywords/ows:Keyword", namespaces))
        ]

        # bbox
        self.boundingBoxWGS84 = None
        b = BoundingBox(
            elem.find(nspath_eval("ows:WGS84BoundingBox", namespaces)),
            namespaces["ows"],
        )
        if b is not None:
            try:
                self.boundingBoxWGS84 = (
                    float(b.minx),
                    float(b.miny),
                    float(b.maxx),
                    float(b.maxy),
                )
            except TypeError:
                self.boundingBoxWGS84 = None
        # crs options
        self.crsOptions = [
            Crs(srs.text)
            for srs in elem.findall(nspath_eval("wfs:OtherSRS", namespaces))
        ]
        dsrs = testXMLValue(elem.find(nspath_eval("wfs:DefaultSRS", namespaces)))
        if dsrs is not None:  # first element is default srs
            self.crsOptions.insert(0, Crs(dsrs))

        # verbs
        self.verbOptions = [
            op.text
            for op in elem.findall(
                nspath_eval("wfs:Operations/wfs:Operation", namespaces)
            )
        ]

        # output formats
        self.outputFormats = [
            op.text
            for op in elem.findall(
                nspath_eval("wfs:OutputFormats/wfs:Format", namespaces)
            )
        ]

        # MetadataURLs
        self.metadataUrls = []
        for m in elem.findall(nspath_eval("wfs:MetadataURL", namespaces)):
            metadataUrl = {
                "type": testXMLValue(m.attrib["type"], attrib=True),
                "format": testXMLValue(m.attrib["format"], attrib=True),
                "url": testXMLValue(m),
            }
            self.metadataUrls.append(metadataUrl)

        if parse_remote_metadata:
            self.parse_remote_metadata(timeout)

        # others not used but needed for iContentMetadata harmonisation
        self.styles = None
        self.timepositions = None
        self.defaulttimeposition = None

    def parse_remote_metadata(self, timeout=30):
        """Parse remote metadata for MetadataURL of format 'text/xml' and add it as metadataUrl['metadata']"""
        for metadataUrl in self.metadataUrls:
            if (
                metadataUrl["url"] is not None and metadataUrl["format"].lower() == "text/xml"
            ):
                try:
                    content = openURL(metadataUrl["url"], timeout=timeout, headers=self.headers, auth=self.auth)
                    doc = etree.fromstring(content.read())

                    if metadataUrl["type"] == "FGDC":
                        mdelem = doc.find(".//metadata")
                        if mdelem is not None:
                            metadataUrl["metadata"] = Metadata(mdelem)
                        else:
                            metadataUrl["metadata"] = None
                    elif metadataUrl["type"] in ["TC211", "19115", "19139"]:
                        mdelem = doc.find(
                            ".//" + nspath_eval("gmd:MD_Metadata", namespaces)
                        ) or doc.find(
                            ".//" + nspath_eval("gmi:MI_Metadata", namespaces)
                        )
                        if mdelem is not None:
                            metadataUrl["metadata"] = MD_Metadata(mdelem)
                        else:
                            metadataUrl["metadata"] = None
                except Exception:
                    metadataUrl["metadata"] = None
