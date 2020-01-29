from tests.utils import resource_file

from owslib.wms import WebMapService


def test_wms_capabilities():
    # Fake a request to a WMS Server using saved doc from
    # http://datageo.ambiente.sp.gov.br/serviceTranslator/rest/getXml/IPT_Geoserver_WMS/Risco_Louveira/1449249453587/wms
    xml = open(resource_file('wms_datageo_caps_130.xml'), 'rb').read()
    wms = WebMapService('url', version='1.3.0', xml=xml)

    # Test capabilities
    # -----------------

    assert wms.identification.type == 'WMS'
    assert wms.identification.version == '1.3.0'
    assert wms.identification.title == 'GeoServer Web Map Service'
