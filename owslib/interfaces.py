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
        Describes the capabilities of the WMS.
    """

    def getcapabilities():
        """Make a request to the WMS, returns an XML document."""

    def getmap(**kw):
        """Make a request to the WMS, returns an image."""

    def getfeatureinfo(**kw):
        """Make a request to the WMS, returns data."""


