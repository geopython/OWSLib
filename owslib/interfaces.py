# Do not import zope.interfaces


class IService:
    """The OGC Web Service interface.
    """

    url = property("""Online resource URL (string)""")
    # XXX: here or in capabilities?
    version = property("""Protocol version (string)""")
    capabilities = property("""Implementation of IServiceMetadata (object)""")


class IWebMapService(IService):
    """Abstraction for an OGC Web Map Service (WMS).
    """

    def getcapabilities():
        """Make a request to the WMS, returns an XML document wrapped in a 
        Python file object."""

    def getmap(**kw):
        """Make a request to the WMS, returns an image wrapped in a Python
        file object."""

    def getfeatureinfo(**kw):
        """Make a request to the WMS, returns data."""


class IWebFeatureService(IService):
    """Abstraction for an OGC Web Feature Service (WFS).
    """

    def getcapabilities():
        """Make a request to the WFS, returns an XML document wrapped in a 
        Python file object."""

    def getfeature(**kw):
        """Make a request to the WFS, returns an image wrapped in a Python
        file object."""

    def describefeaturetype(**kw):
        """Make a request to the WFS, returns data."""


class IWebCoverageService(IService):
    # TODO
    pass


# Follows the 4 aspects of service metadata

class IServiceIdentificationMetadata:
    """OO-interface to service identification metadata.
    """

    service = property("""Service name (string): "WMS", "WFS", or "WCS".""")
    # XXX: here or in service root?
    version = property("""Version of service protocol (string).""")
    title = property("""Human-targeted title of service (string).""")
    abstract = property("""Text describing the service (string).""")
    keywords = property("""Keyword list (list).""")
    rights = property("""Explanation of rights associated with service (string).""")
    

class IServiceProviderMetadata:
    """OO-interface to service provider metadata.
    """

    provider = property("""Provider's name (string).""")
    url = property("""URL for provider's web site (string).""")
    contact = property("""How to contact the service provider (string).""")


class IServiceOperationsMetadata:
    """OO-interface to service operations metadata.
    """

    operations = property("""List of operation descriptors (list). These must implement IOperationMetadata (below).""")
    exceptions = property("""List of exception formats (list).""")


class IServiceContentsMetadata:
    """OO-interface to service contents metadata.
    """

    contents = property("""List of content descriptors (list). These must implement IServiceContent (below).""")


# IServiceMetadata aggregates the 4 aspects above

class IServiceMetadata(
    IServiceIdentificationMetadata, IServiceProviderMetadata,
    IServiceOperationsMetadata, IServiceContentsMetadata
    ):
    """OWS Metadata.
    """


# Second level metadata interfaces

class IOperationMetadata:
    """OO-interface to operation metadata.
    """

    name = property("""Operation name (string): GetCapabilities", for example.""")
    formatOptions = property("""List of content types (list).""")
    methods = property("""Mapping of method descriptors, keyed to HTTP verbs. Items must implement IMethodMetadata (below).""")


class IMethodMetadata:
    """OO-interface to method metadata.
    """

    url = property("""Method endpoint URL (string).""")
    # TODO: constraint


class IContentMetadata:
    """OO-interface to content metadata.
    """

    id = property("""Unique identifier (string).""")
    title = property("""Human-targeted title (string).""")
    boundingBox = property("""Four bounding values and a coordinate reference system identifier (tuple).""")
    boundingBoxWGS84 = property("""Four bounding values in WGS coordinates.""")
    crsOptions = property("""List of available coordinate/spatial reference systems (list).""")
    styles = property("""List of style dicts (list).""")


# XXX: needed?

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



