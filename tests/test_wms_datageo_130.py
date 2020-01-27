from tests.utils import resource_file

from owslib.wms import WebMapService


def test_wms_capabilities():
    # Fake a request to a WMS Server using saved doc from
    # http://wms.jpl.nasa.gov/wms.cgi.
    xml = open(resource_file('wms_datageo_caps_130.xml'), 'rb').read()
    wms = WebMapService('url', version='1.3.0', xml=xml)
