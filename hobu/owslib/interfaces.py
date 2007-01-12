# Do not import zope.interfaces

class IWebMapService:
    """Abstraction for an OGC Web Map Service (WMS).

    Properties
    ----------
    url : string
        Online resource URL.
    version : string
        WMS protocol version.
    capabilities : object
        Describes the capabilities metadata of the WMS.
    """

    def getcapabilities():
        """Make a request to the WMS, returns an XML document wrapped in a 
        Python file object."""

    def getmap(**kw):
        """Make a request to the WMS, returns an image wrapped in a Python
        file object."""

    def getfeatureinfo(**kw):
        """Make a request to the WMS, returns data."""


class IWebFeatureService:
    """Abstraction for an OGC Web Feature Service (WFS).

    Properties
    ----------
    url : string
        Online resource URL.
    version : string
        WFS protocol version.
    capabilities : object
        Describes the capabilities metadata of the WFS.
    """

    def getcapabilities():
        """Make a request to the WFS, returns an XML document wrapped in a 
        Python file object."""

    def getfeature(**kw):
        """Make a request to the WFS, returns an image wrapped in a Python
        file object."""

    def describefeaturetype(**kw):
        """Make a request to the WFS, returns data."""


class IServiceIdentificationMetadata:
    """OO-interface to WMS metadata.

    Properties
    ----------
    service : string
        "WMS", "WFS".
    version : string
        Version of service protocol.
    title : string
        Human-targeted title of service.
    abstract : string
        Text describing the service.
    keywords : list
        List of strings.
    rights : list
        Explanation of rights associated with service.
    """
    
class IServiceProviderMetadata:
    """OO-interface to WMS metadata.

    Properties
    ----------
    provider : string
        Organization name.
    url : string
        URL for provider web site.
    contact : string
        How to contact the service provider.
    """

class IServiceOperationsMetadata:
    """OO-interface to WMS metadata.

    Properties
    ----------
    operations : list
        List of operation descriptors.
    exceptions : list
        List of exception formats.
    """
    
class IOperationMetadata:
    """OO-interface to WMS metadata.

    Properties
    ----------
    name : string
        "GetCapabilities", for example.
    formatOptions : list
        List of content types.
    methods : dict
        Array of method descriptors, keyed to HTTP verbs.
    """

class IContactMetadata:
    """OO-interface to OWS metadata.

    Properties
    ----------
    name : string
    organization : string
    address : string
    city : string
    region : string
    postcode : string
    country : string
    email : string
    """

class IMethodMetadata:
    """OO-interface to WMS metadata.

    Properties
    ----------
    url : string
        Method URL.
    
    TODO: constraint
    """

class IServiceContentsMetadata:
    """OO-interface to WMS metadata.

    Properties
    ----------
    contents : list
        List of content descriptors.
    """

class IContentMetadata:
    """OO-interface to WMS metadata.

    Properties
    ----------
    id : string
        Unique identifier.
    title : string
        Human-targeted title.
    boundingBox : 5-tuple
        Four bounding values and a coordinate reference system identifier.
    boundingBoxWGS84 : 4-tuple
        Four bounding values in WGS coordinates.
    crsOptions : list
        List of available coordinate/spatial reference systems.
    styles : list
        List of style dicts.
    """

class IServiceMetadata(IServiceIdentificationMetadata, IServiceProvideMetadata,
                       IServiceOperationsMetadata, IServiceContentsMetadata):
    """OWS Metadata.
    """


