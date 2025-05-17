import pytest

import owslib
from owslib.etree import etree
from owslib.wfs import WebFeatureService
from tests.utils import service_ok

WFS_SERVICE_URL = 'https://www.dov.vlaanderen.be/geoserver/wfs?request=GetCapabilities'


@pytest.fixture
def mp_wfs_110(monkeypatch):
    """Monkeypatch the call to the remote GetCapabilities request of WFS
    version 1.1.0.

    Parameters
    ----------
    monkeypatch : pytest.fixture
        PyTest monkeypatch fixture.

    """
    def read(*args, **kwargs):
        with open('tests/resources/wfs_dov_getcapabilities_110.xml', 'r') as f:
            data = f.read()
            if type(data) is not bytes:
                data = data.encode('utf-8')
            data = etree.fromstring(data)
        return data

    monkeypatch.setattr(
        owslib.feature.common.WFSCapabilitiesReader, 'read', read)


@pytest.fixture()
def mp_remote_describefeaturetype(monkeypatch):
    """Monkeypatch the call to the remote DescribeFeatureType request.

    Returns a standard DescribeFeatureType response.

    Parameters
    ----------
    monkeypatch : pytest.fixture
        PyTest monkeypatch fixture.

    """
    def __remote_describefeaturetype(*args, **kwargs):
        with open('tests/resources/wfs_schema_dov_boringen.xml', 'r') as f:
            data = f.read()
            if type(data) is not bytes:
                data = data.encode('utf-8')
            data = etree.fromstring(data)
        return data

    monkeypatch.setattr(owslib.feature.schema,
                        '_get_remote_describefeaturetype',
                        __remote_describefeaturetype)


@pytest.fixture()
def mp_remote_describefeaturetype_typename_eq_attribute(monkeypatch):
    """Monkeypatch the call to the remote DescribeFeatureType request.

    Returns a DescribeFeatureType response where the typeName equals one of
    the attributes.

    Parameters
    ----------
    monkeypatch : pytest.fixture
        PyTest monkeypatch fixture.

    """
    def __remote_describefeaturetype(*args, **kwargs):
        with open('tests/resources/wfs_schema_dov_hhz.xml', 'r') as f:
            data = f.read()
            if type(data) is not bytes:
                data = data.encode('utf-8')
            data = etree.fromstring(data)
        return data

    monkeypatch.setattr(owslib.feature.schema,
                        '_get_remote_describefeaturetype',
                        __remote_describefeaturetype)





class TestOnline(object):
    """Class grouping online tests for the WFS get_schema method."""
    @pytest.mark.xfail
    @pytest.mark.online
    @pytest.mark.skipif(not service_ok(WFS_SERVICE_URL),
                        reason="WFS service is unreachable")
    @pytest.mark.parametrize("wfs_version", ["1.1.0", "2.0.0"])
    def test_get_schema(self, wfs_version):
        """Test the get_schema method for a standard schema."""
        wfs = WebFeatureService(WFS_SERVICE_URL, version=wfs_version)
        schema = wfs.get_schema('dov-pub:Boringen')

    @pytest.mark.xfail
    @pytest.mark.online
    @pytest.mark.skipif(not service_ok(WFS_SERVICE_URL),
                        reason="WFS service is unreachable")
    @pytest.mark.parametrize("wfs_version", ["1.1.0", "2.0.0"])
    def test_schema_result(self, wfs_version):
        """Test whether the output from get_schema is a wellformed dictionary."""
        wfs = WebFeatureService(WFS_SERVICE_URL, version=wfs_version)
        schema = wfs.get_schema('dov-pub:Boringen')
        assert isinstance(schema, dict)

        assert 'properties' in schema or 'geometry' in schema

        if 'geometry' in schema:
            assert 'geometry_column' in schema

        if 'properties' in schema:
            assert isinstance(schema['properties'], dict)

        assert 'required' in schema
        assert isinstance(schema['required'], list)


class TestOffline(object):
    """Class grouping offline tests for the WFS get_schema method."""
    def test_get_schema(self, mp_wfs_110, mp_remote_describefeaturetype):
        """Test the get_schema method for a standard schema.

        Parameters
        ----------
        mp_wfs_110 : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.
        mp_remote_describefeaturetype : pytest.fixture
            Monkeypatch the call to the remote DescribeFeatureType request.
        """
        wfs110 = WebFeatureService(WFS_SERVICE_URL, version='1.1.0')
        schema = wfs110.get_schema('dov-pub:Boringen')

    def test_schema_result(self, mp_wfs_110, mp_remote_describefeaturetype):
        """Test whether the output from get_schema is a wellformed dictionary.

        Parameters
        ----------
        mp_wfs_110 : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.
        mp_remote_describefeaturetype : pytest.fixture
            Monkeypatch the call to the remote DescribeFeatureType request.
        """
        wfs110 = WebFeatureService(WFS_SERVICE_URL, version='1.1.0')
        schema = wfs110.get_schema('dov-pub:Boringen')
        assert isinstance(schema, dict)

        assert 'properties' in schema or 'geometry' in schema

        if 'geometry' in schema:
            assert 'geometry_column' in schema

        if 'properties' in schema:
            assert isinstance(schema['properties'], dict)

        assert 'required' in schema
        assert isinstance(schema['required'], list)

    def test_get_schema_typename_eq_attribute(
            self, mp_wfs_110,
            mp_remote_describefeaturetype_typename_eq_attribute):
        """Test the get_schema method for a schema where the typeName equals
        one of the attributes.

        Parameters
        ----------
        mp_wfs_110 : pytest.fixture
            Monkeypatch the call to the remote GetCapabilities request.
        mp_remote_describefeaturetype : pytest.fixture
            Monkeypatch the call to the remote DescribeFeatureType
            request.
        """
        wfs110 = WebFeatureService(WFS_SERVICE_URL, version='1.1.0')
        schema = wfs110.get_schema('gw_varia:hhz')

    def test_get_datatype_geometry(self):
        """Test the _get_datatype helper function with geometry types."""
        from owslib.feature.schema import _get_datatype, XS_NAMESPACE
        from owslib.etree import etree

        ns = {
            'xs': XS_NAMESPACE,
            'gml': 'http://www.opengis.net/gml',
            'xsd': 'http://www.w3.org/2001/XMLSchema'
        }

        # Test geometry type
        # XML: <element name="field1" type="gml:PointPropertyType"/>
        element = etree.Element('{%s}element' % XS_NAMESPACE,
                              attrib={'name': 'field1', 'type': 'gml:PointPropertyType'},
                              nsmap=ns)
        assert _get_datatype(element, "xsd", "gml") == "PointPropertyType"

    def test_get_datatype_reference(self):
        """Test the _get_datatype helper function with element references."""
        from owslib.feature.schema import _get_datatype, XS_NAMESPACE
        from owslib.etree import etree

        ns = {
            'xs': XS_NAMESPACE,
            'gml': 'http://www.opengis.net/gml',
            'xsd': 'http://www.w3.org/2001/XMLSchema'
        }

        # Test element reference
        # XML: <element name="field2" ref="gml:polygonProperty"/>
        element = etree.Element('{%s}element' % XS_NAMESPACE,
                              attrib={'name': 'field2', 'ref': 'gml:polygonProperty'},
                              nsmap=ns)
        assert _get_datatype(element, "xsd", "gml") == "polygonProperty"

    @pytest.mark.parametrize("data_type", [
        "xsd:boolean",
        "xsd:date",
        "xsd:dateTime",
        "xsd:double",
        "xsd:float",
        "xsd:integer",
        "xsd:int",
        "xsd:string",
    ])
    def test_get_datatype_simple_types(self, data_type):
        """Test the _get_datatype helper function with different simple types.

        Parameters
        ----------
        data_type : str
            The XML Schema data type to test
        """
        from owslib.feature.schema import _get_datatype, XS_NAMESPACE
        from owslib.etree import etree

        ns = {
            'xs': XS_NAMESPACE,
            'gml': 'http://www.opengis.net/gml',
            'xsd': 'http://www.w3.org/2001/XMLSchema'
        }

        # Test simple type with restriction
        # XML:
        # <element name="field3">
        #     <simpleType>
        #         <restriction base="[data_type]"/>
        #     </simpleType>
        # </element>
        element = etree.Element('{%s}element' % XS_NAMESPACE, attrib={'name': 'field3'}, nsmap=ns)
        simple_type = etree.SubElement(element, '{%s}simpleType' % XS_NAMESPACE)
        restriction = etree.SubElement(simple_type, '{%s}restriction' % XS_NAMESPACE,
                                    attrib={'base': data_type})
        expected_type = data_type.split(":")[-1]
        assert _get_datatype(element, "xsd", "gml") == expected_type

    @pytest.mark.parametrize("data_type", [
        "xsd:boolean",
        "xsd:date",
        "xsd:dateTime",
        "xsd:double",
        "xsd:float",
        "xsd:integer",
        "xsd:int",
        "xsd:string",
    ])
    def test_get_datatype_direct_types(self, data_type):
        """Test the _get_datatype helper function with direct type attributes.

        Parameters
        ----------
        data_type : str
            The XML Schema data type to test
        """
        from owslib.feature.schema import _get_datatype, XS_NAMESPACE
        from owslib.etree import etree

        ns = {
            'xs': XS_NAMESPACE,
            'gml': 'http://www.opengis.net/gml',
            'xsd': 'http://www.w3.org/2001/XMLSchema'
        }

        # Test direct type attribute
        # XML: <element name="field1" type="xsd:string"/>
        element = etree.Element('{%s}element' % XS_NAMESPACE,
                              attrib={'name': 'field1', 'type': data_type},
                              nsmap=ns)
        expected_type = data_type.split(":")[-1]
        assert _get_datatype(element, "xsd", "gml") == expected_type

    @pytest.mark.parametrize("data_type", [
        "xsd:boolean",
        "xsd:date",
        "xsd:dateTime",
        "xsd:double",
        "xsd:float",
        "xsd:integer",
        "xsd:int",
        "xsd:string",
    ])
    def test_get_datatype_complex_types(self, data_type):
        """Test the _get_datatype helper function with complex type definitions.

        Parameters
        ----------
        data_type : str
            The XML Schema data type to test
        """
        from owslib.feature.schema import _get_datatype, XS_NAMESPACE
        from owslib.etree import etree

        ns = {
            'xs': XS_NAMESPACE,
            'gml': 'http://www.opengis.net/gml',
            'xsd': 'http://www.w3.org/2001/XMLSchema'
        }

        # Test complex type
        # XML:
        # <element name="field4">
        #     <complexType>
        #         <sequence>
        #             <element type="xsd:type"/>
        #         </sequence>
        #     </complexType>
        # </element>
        element = etree.Element('{%s}element' % XS_NAMESPACE, attrib={'name': 'field4'}, nsmap=ns)
        complex_type = etree.SubElement(element, '{%s}complexType' % XS_NAMESPACE)
        sequence = etree.SubElement(complex_type, '{%s}sequence' % XS_NAMESPACE)
        sub_element = etree.SubElement(sequence, '{%s}element' % XS_NAMESPACE,
                                    attrib={'type': data_type})
        expected_type = data_type.split(":")[-1]
        assert _get_datatype(element, "xsd", "gml") == expected_type



    def test_get_datatype_unknown(self):
        """Test the _get_datatype helper function with unknown structure."""
        from owslib.feature.schema import _get_datatype, XS_NAMESPACE
        from owslib.etree import etree

        ns = {
            'xs': XS_NAMESPACE,
            'gml': 'http://www.opengis.net/gml',
            'xsd': 'http://www.w3.org/2001/XMLSchema'
        }

        # Test unknown structure
        # XML: <element name="field5"/>
        element = etree.Element('{%s}element' % XS_NAMESPACE, attrib={'name': 'field5'}, nsmap=ns)
        assert _get_datatype(element, "xsd", "gml") is None
