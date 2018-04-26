from tests.utils import resource_file, compare_xml, setup_logging
from owslib.wps import WebProcessingService


def test_wps_response6():
    # Build WPS object; service has been down for some time so skip caps here
    wps = WebProcessingService('http://rsg.pml.ac.uk/wps/vector.cgi', skip_caps=True)

    # Execute face WPS invocation
    request = open(resource_file('wps_PMLExecuteRequest6.xml'), 'rb').read()
    response = open(resource_file('wps_PMLExecuteResponse6.xml'), 'rb').read()
    execution = wps.execute(None, [], request=request, response=response)

    # Check execution result
    assert execution.status == 'ProcessSucceeded'
    assert execution.url == 'http://rsg.pml.ac.uk/wps/vector.cgi'
    assert execution.statusLocation == \
        'http://rsg.pml.ac.uk/wps/wpsoutputs/pywps-132084838963.xml'
    assert execution.serviceInstance == \
        'http://rsg.pml.ac.uk/wps/vector.cgi?service=WPS&request=GetCapabilities&version=1.0.0'
    assert execution.version == '1.0.0'
    # check single output
    output = execution.processOutputs[0]
    assert output.identifier == 'output'
    assert output.title == 'Name for output vector map'
    assert output.mimeType == 'text/xml'
    assert output.dataType == 'ComplexData'
    assert output.reference is None

    response = output.data[0]
    should_return = '''<ns3:FeatureCollection xmlns:ns3="http://ogr.maptools.org/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns0="http://www.opengis.net/wps/1.0.0" xsi:schemaLocation="http://ogr.maptools.org/ output_0n7ij9D.xsd">\n\t\t\t\t\t  <gml:boundedBy xmlns:gml="http://www.opengis.net/gml">\n\t\t\t\t\t    <gml:Box>\n\t\t\t\t\t      <gml:coord><gml:X>-960123.1421801626</gml:X><gml:Y>4665723.56559387</gml:Y></gml:coord>\n\t\t\t\t\t      <gml:coord><gml:X>-101288.6510608822</gml:X><gml:Y>5108200.011823481</gml:Y></gml:coord>\n\t\t\t\t\t    </gml:Box>\n\t\t\t\t\t  </gml:boundedBy>                         \n\t\t\t\t\t  <gml:featureMember xmlns:gml="http://www.opengis.net/gml">\n\t\t\t\t\t    <ns3:output fid="F0">\n\t\t\t\t\t      <ns3:geometryProperty><gml:LineString><gml:coordinates>-960123.142180162365548,4665723.565593870356679,0 -960123.142180162365548,4665723.565593870356679,0 -960123.142180162598379,4665723.565593870356679,0 -960123.142180162598379,4665723.565593870356679,0 -711230.141176006174646,4710278.48552671354264,0 -711230.141176006174646,4710278.48552671354264,0 -623656.677859728806652,4848552.374973464757204,0 -623656.677859728806652,4848552.374973464757204,0 -410100.337491964863148,4923834.82589447684586,0 -410100.337491964863148,4923834.82589447684586,0 -101288.651060882242746,5108200.011823480948806,0 -101288.651060882242746,5108200.011823480948806,0 -101288.651060882257298,5108200.011823480948806,0 -101288.651060882257298,5108200.011823480948806,0</gml:coordinates></gml:LineString></ns3:geometryProperty>\n\t\t\t\t\t      <ns3:cat>1</ns3:cat>\n\t\t\t\t\t      <ns3:id>1</ns3:id>\n\t\t\t\t\t      <ns3:fcat>0</ns3:fcat>\n\t\t\t\t\t      <ns3:tcat>0</ns3:tcat>\n\t\t\t\t\t      <ns3:sp>0</ns3:sp>\n\t\t\t\t\t      <ns3:cost>1002619.181</ns3:cost>\n\t\t\t\t\t      <ns3:fdist>0</ns3:fdist>\n\t\t\t\t\t      <ns3:tdist>0</ns3:tdist>\n\t\t\t\t\t    </ns3:output>\n\t\t\t\t\t  </gml:featureMember>\n\t\t\t\t\t</ns3:FeatureCollection>'''  # noqa
    assert compare_xml(should_return, response) is True
