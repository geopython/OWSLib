# =============================================================================
# OWSLib. Copyright (C) 2005 Sean C. Gillies
#
# Contact email: sgillies@frii.com
#
# $Id: wfs.py 503 2006-02-01 17:09:12Z dokai $
# =============================================================================

# owslib imports:
from owslib import util
from owslib.fgdc import Metadata
from owslib.iso import MD_Metadata
from owslib.ows import Constraint, ServiceIdentification, ServiceProvider, OperationsMetadata
from owslib.etree import etree
from owslib.util import nspath, testXMLValue, openURL, Authentication
from owslib.crs import Crs
from owslib.feature import WebFeatureService_
from owslib.feature.common import (
    WFSCapabilitiesReader,
    AbstractContentMetadata,
)
from owslib.namespaces import Namespaces

# other imports
from io import BytesIO
from urllib.parse import urlencode

import logging
from owslib.util import log

n = Namespaces()
WFS_NAMESPACE = n.get_namespace("wfs20")
OWS_NAMESPACE = n.get_namespace("ows110")
OGC_NAMESPACE = n.get_namespace("ogc")
GML_NAMESPACE = n.get_namespace("gml")
FES_NAMESPACE = n.get_namespace("fes")


class ServiceException(Exception):
    pass


class WebFeatureService_2_0_0(WebFeatureService_):
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
        @return: initialized WebFeatureService_2_0_0 object
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
            auth = Authentication()
        super(WebFeatureService_2_0_0, self).__init__(auth)
        log.debug("building WFS %s" % url)
        self.url = url
        self.version = version
        self.timeout = timeout
        self.headers = headers
        self._capabilities = None
        reader = WFSCapabilitiesReader(self.version, headers=self.headers, auth=self.auth)
        if xml:
            self._capabilities = reader.readString(xml)
        else:
            self._capabilities = reader.read(self.url, self.timeout)
        self._buildMetadata(parse_remote_metadata)

    def _buildMetadata(self, parse_remote_metadata=False):
        """set up capabilities metadata objects: """

        self.updateSequence = self._capabilities.attrib.get("updateSequence")

        # serviceIdentification metadata
        serviceidentelem = self._capabilities.find(nspath("ServiceIdentification"))
        if serviceidentelem is not None:
            self.identification = ServiceIdentification(serviceidentelem)
        # need to add to keywords list from featuretypelist information:
        featuretypelistelem = self._capabilities.find(
            nspath("FeatureTypeList", ns=WFS_NAMESPACE)
        )
        if featuretypelistelem is not None:
            featuretypeelems = featuretypelistelem.findall(
                nspath("FeatureType", ns=WFS_NAMESPACE)
            )
            if serviceidentelem is not None:
                for f in featuretypeelems:
                    kwds = f.findall(nspath("Keywords/Keyword", ns=OWS_NAMESPACE))
                    if kwds is not None:
                        for kwd in kwds[:]:
                            if kwd.text not in self.identification.keywords:
                                self.identification.keywords.append(kwd.text)

        # TODO: update serviceProvider metadata, miss it out for now
        serviceproviderelem = self._capabilities.find(nspath("ServiceProvider"))
        if serviceproviderelem is not None:
            self.provider = ServiceProvider(serviceproviderelem)

        # serviceOperations metadata
        self.operations = []

        for elem in self._capabilities.find(nspath("OperationsMetadata"))[:]:
            if elem.tag != nspath("ExtendedCapabilities"):
                self.operations.append(OperationsMetadata(elem))
        self.constraints = {}
        for elem in self._capabilities.findall(
            nspath("OperationsMetadata/Constraint", ns=WFS_NAMESPACE)
        ):
            self.constraints[elem.attrib["name"]] = Constraint(
                elem, self.owscommon.namespace
            )
        self.parameters = {}
        for elem in self._capabilities.findall(
            nspath("OperationsMetadata/Parameter", ns=WFS_NAMESPACE)
        ):
            self.parameters[elem.attrib["name"]] = Parameter(
                elem, self.owscommon.namespace
            )

        # serviceContents metadata: our assumption is that services use a top-level
        # layer as a metadata organizer, nothing more.

        self.contents = {}
        featuretypelist = self._capabilities.find(
            nspath("FeatureTypeList", ns=WFS_NAMESPACE)
        )
        features = self._capabilities.findall(
            nspath("FeatureTypeList/FeatureType", ns=WFS_NAMESPACE)
        )
        for feature in features:
            cm = ContentMetadata(
                feature, featuretypelist, parse_remote_metadata, auth=self.auth
            )
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
        storedQueryID=None,
        storedQueryParams=None,
        method="Get",
        outputFormat=None,
        startindex=None,
        sortby=None,
    ):
        """Request and return feature data as a file-like object.

        #TODO: NOTE: have changed property name from ['*'] to None - check the use of this in WFS 2.0

        Parameters
        ----------
        typename : list
            List of typenames (string)
        filter : string
            XML-encoded OGC filter expression.
        bbox : tuple
            (left, bottom, right, top) in the feature type's coordinates == (minx, miny, maxx, maxy)
        featureid : list
            List of unique feature ids (string)
        featureversion : string
            Default is most recent feature version.
        propertyname : list
            List of feature property names. For Get request, '*' matches all.
            For Post request, leave blank (None) to get all properties.
        maxfeatures : int
            Maximum number of features to be returned.
        storedQueryID : string
            A name identifying a prepared set available in WFS-service
        storedQueryParams : dict
            Variable amount of extra information sent to server related to
            storedQueryID to further define the requested data
            {'parameter_name': parameter_value}
        method : string
            Qualified name of the HTTP DCP method to use.
        outputFormat: string (optional)
            Requested response format of the request.
        startindex: int (optional)
            Start position to return feature set (paging in combination with maxfeatures)
        sortby: list (optional)
            List of property names whose values should be used to order
            (upon presentation) the set of feature instances that
            satify the query.

        There are 5 different modes of use

        1) typename and bbox (simple spatial query)
        2) typename and filter (==query) (more expressive)
        3) featureid (direct access to known features)
        4) storedQueryID and optional storedQueryParams
        5) filter only via Post method

        Raises:
            ServiceException: If there is an error during the request

        Returns:
            BytesIO -- Data returned from the service as a file-like object
        """
        storedQueryParams = storedQueryParams or {}
        url = data = None
        if typename and type(typename) == type(""):  # noqa: E721
            typename = [typename]
        if method.upper() == "GET":
            (url) = self.getGETGetFeatureRequest(
                typename,
                filter,
                bbox,
                featureid,
                featureversion,
                propertyname,
                maxfeatures,
                storedQueryID,
                storedQueryParams,
                outputFormat,
                "Get",
                startindex,
                sortby,
            )
            log.debug("GetFeature WFS GET url %s" % url)
        else:
            url, data = self.getPOSTGetFeatureRequest(
                typename,
                filter,
                bbox,
                featureid,
                featureversion,
                propertyname,
                maxfeatures,
                storedQueryID,
                storedQueryParams,
                outputFormat,
                "Post",
                startindex,
                sortby)

        u = openURL(url, data, method, timeout=self.timeout, headers=self.headers, auth=self.auth)

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
                if tree.tag == "{%s}ServiceExceptionReport" % OGC_NAMESPACE:
                    se = tree.find(nspath("ServiceException", OGC_NAMESPACE))
                    raise ServiceException(str(se.text).strip())
                else:
                    return BytesIO(data)
        else:
            if have_read:
                return BytesIO(data)
            return u

    def getpropertyvalue(
        self,
        query=None,
        storedquery_id=None,
        valuereference=None,
        typename=None,
        method=nspath("Get"),
        **kwargs
    ):
        """ the WFS GetPropertyValue method"""
        try:
            base_url = next(
                (
                    m.get("url")
                    for m in self.getOperationByName("GetPropertyValue").methods
                    if m.get("type").lower() == method.lower()
                )
            )
        except StopIteration:
            base_url = self.url
        request = {
            "service": "WFS",
            "version": self.version,
            "request": "GetPropertyValue",
        }
        if query:
            request["query"] = str(query)
        if valuereference:
            request["valueReference"] = str(valuereference)
        if storedquery_id:
            request["storedQuery_id"] = str(storedquery_id)
        if typename:
            request["typename"] = str(typename)
        if kwargs:
            for kw in list(kwargs.keys()):
                request[kw] = str(kwargs[kw])
        encoded_request = urlencode(request)
        u = openURL(base_url + encoded_request, timeout=self.timeout, headers=self.headers, auth=self.auth)
        return u.read()

    def _getStoredQueries(self):
        """ gets descriptions of the stored queries available on the server """
        sqs = []
        # This method makes two calls to the WFS - one ListStoredQueries, and one DescribeStoredQueries.
        # The information is then aggregated in 'StoredQuery' objects
        method = nspath("Get")

        # first make the ListStoredQueries response and save the results in a dictionary
        # if form {storedqueryid:(title, returnfeaturetype)}
        try:
            base_url = next(
                (
                    m.get("url")
                    for m in self.getOperationByName("ListStoredQueries").methods
                    if m.get("type").lower() == method.lower()
                )
            )
        except StopIteration:
            base_url = self.url

        request = {
            "service": "WFS",
            "version": self.version,
            "request": "ListStoredQueries",
        }
        encoded_request = urlencode(request)
        u = openURL(
            base_url, data=encoded_request, timeout=self.timeout, headers=self.headers, auth=self.auth
        )
        tree = etree.fromstring(u.read())
        tempdict = {}
        for sqelem in tree[:]:
            title = rft = id = None
            id = sqelem.get("id")
            for elem in sqelem[:]:
                if elem.tag == nspath("Title", WFS_NAMESPACE):
                    title = elem.text
                elif elem.tag == nspath("ReturnFeatureType", WFS_NAMESPACE):
                    rft = elem.text
            tempdict[id] = (title, rft)  # store in temporary dictionary

        # then make the DescribeStoredQueries request and get the rest of the information about the stored queries
        try:
            base_url = next(
                (
                    m.get("url")
                    for m in self.getOperationByName("DescribeStoredQueries").methods
                    if m.get("type").lower() == method.lower()
                )
            )
        except StopIteration:
            base_url = self.url
        request = {
            "service": "WFS",
            "version": self.version,
            "request": "DescribeStoredQueries",
        }
        encoded_request = urlencode(request)
        u = openURL(
            base_url, data=encoded_request, timeout=self.timeout, headers=self.headers, auth=self.auth
        )
        tree = etree.fromstring(u.read())
        tempdict2 = {}
        for sqelem in tree[:]:
            params = []  # list to store parameters for the stored query description
            id = sqelem.get("id")
            for elem in sqelem[:]:
                abstract = ""
                if elem.tag == nspath("Abstract", WFS_NAMESPACE):
                    abstract = elem.text
                elif elem.tag == nspath("Parameter", WFS_NAMESPACE):
                    newparam = Parameter(elem.get("name"), elem.get("type"))
                    params.append(newparam)
            tempdict2[id] = (abstract, params)  # store in another temporary dictionary

        # now group the results into StoredQuery objects:
        for key in list(tempdict.keys()):
            sqs.append(
                StoredQuery(
                    key,
                    tempdict[key][0],
                    tempdict[key][1],
                    tempdict2[key][0],
                    tempdict2[key][1],
                )
            )
        return sqs

    storedqueries = property(_getStoredQueries, None)

    def getOperationByName(self, name):
        """Return a named content item."""
        for item in self.operations:
            if item.name == name:
                return item
        raise KeyError("No operation named %s" % name)


class StoredQuery(object):
    """' Class to describe a storedquery """

    def __init__(self, id, title, returntype, abstract, parameters):
        self.id = id
        self.title = title
        self.returnfeaturetype = returntype
        self.abstract = abstract
        self.parameters = parameters


class Parameter(object):
    def __init__(self, name, type):
        self.name = name
        self.type = type


class ContentMetadata(AbstractContentMetadata):
    """Abstraction for WFS metadata.

    Implements IMetadata.
    """

    def __init__(
        self, elem, parent, parse_remote_metadata=False, timeout=30, headers=None, auth=None
    ):
        """."""
        super(ContentMetadata, self).__init__(headers=headers, auth=auth)
        self.id = elem.find(nspath("Name", ns=WFS_NAMESPACE)).text
        self.title = elem.find(nspath("Title", ns=WFS_NAMESPACE)).text
        abstract = elem.find(nspath("Abstract", ns=WFS_NAMESPACE))
        if abstract is not None:
            self.abstract = abstract.text
        else:
            self.abstract = None
        self.keywords = [
            f.text for f in elem.findall(nspath("Keywords", ns=WFS_NAMESPACE))
        ]

        # bboxes
        self.boundingBoxWGS84 = None
        b = elem.find(nspath("WGS84BoundingBox", ns=OWS_NAMESPACE))
        if b is not None:
            try:
                lc = b.find(nspath("LowerCorner", ns=OWS_NAMESPACE))
                uc = b.find(nspath("UpperCorner", ns=OWS_NAMESPACE))
                ll = [float(s) for s in lc.text.split()]
                ur = [float(s) for s in uc.text.split()]
                self.boundingBoxWGS84 = (ll[0], ll[1], ur[0], ur[1])

                # there is no such think as bounding box
                # make copy of the WGS84BoundingBox
                self.boundingBox = (
                    self.boundingBoxWGS84[0],
                    self.boundingBoxWGS84[1],
                    self.boundingBoxWGS84[2],
                    self.boundingBoxWGS84[3],
                    Crs("epsg:4326"),
                )
            except AttributeError:
                self.boundingBoxWGS84 = None
        # crs options
        self.crsOptions = [
            Crs(srs.text) for srs in elem.findall(nspath("OtherCRS", ns=WFS_NAMESPACE))
        ]
        defaultCrs = elem.findall(nspath("DefaultCRS", ns=WFS_NAMESPACE))
        if len(defaultCrs) > 0:
            self.crsOptions.insert(0, Crs(defaultCrs[0].text))

        # verbs
        self.verbOptions = [
            op.tag for op in parent.findall(nspath("Operations/*", ns=WFS_NAMESPACE))
        ]
        self.verbOptions + [
            op.tag
            for op in elem.findall(nspath("Operations/*", ns=WFS_NAMESPACE))
            if op.tag not in self.verbOptions
        ]

        # others not used but needed for iContentMetadata harmonisation
        self.styles = None
        self.timepositions = None
        self.defaulttimeposition = None

        # MetadataURLs
        self.metadataUrls = []
        for m in elem.findall(nspath("MetadataURL", ns=WFS_NAMESPACE)):
            metadataUrl = {
                "url": testXMLValue(
                    m.attrib["{http://www.w3.org/1999/xlink}href"], attrib=True
                )
            }
            self.metadataUrls.append(metadataUrl)

        if parse_remote_metadata:
            self.parse_remote_metadata(timeout)

    def parse_remote_metadata(self, timeout=30):
        """Parse remote metadata for MetadataURL and add it as metadataUrl['metadata']"""
        for metadataUrl in self.metadataUrls:
            if metadataUrl["url"] is not None:
                try:
                    content = openURL(metadataUrl["url"], timeout=timeout, headers=self.headers, auth=self.auth)
                    doc = etree.fromstring(content.read())

                    mdelem = doc.find(".//metadata")
                    if mdelem is not None:
                        metadataUrl["metadata"] = Metadata(mdelem)
                        continue

                    mdelem = doc.find(
                        ".//" + util.nspath_eval("gmd:MD_Metadata", n.get_namespaces(["gmd"]))
                    ) or doc.find(
                        ".//" + util.nspath_eval("gmi:MI_Metadata", n.get_namespaces(["gmi"]))
                    )
                    if mdelem is not None:
                        metadataUrl["metadata"] = MD_Metadata(mdelem)
                        continue
                except Exception:
                    metadataUrl["metadata"] = None
