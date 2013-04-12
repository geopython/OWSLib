from owslib.waterml.wml import SitesResponse, TimeSeriesResponse, VariablesResponse, namespaces
from owslib.etree import etree

def ns(namespace):
    return namespaces.get(namespace)

class WaterML_1_0(object):
    def __init__(self, xml):
        try:
            self._root = etree.parse(xml)
        except:
            self._root = xml

        self._ns = 'wml1.0'

    @property
    def response(self):
        try:
            if self._root.getroot().tag == str(ns(self._ns) + 'variablesResponse'):
                return VariablesResponse(self._root, self._ns)
            elif self._root.getroot().tag == str(ns(self._ns) + 'timeSeriesResponse'):
                return TimeSeriesResponse(self._root, self._ns)
            elif self._root.getroot().tag == str(ns(self._ns) + 'sitesResponse'):
                return SitesResponse(self._root, self._ns)
        except:
            raise

        raise ValueError('Unable to determine response type from xml')