
from tests.utils import resource_file
from owslib.etree import etree
from owslib.gm03 import GM03


def test_gm03():
    """Test GM03 parsing"""

    e = etree.parse(resource_file('gm03_example1.xml'))
    gm03 = GM03(e)
    assert gm03.header.version == '2.3'
    assert gm03.header.sender == 'geocat.ch'
    assert not hasattr(gm03.data, 'core')
    assert hasattr(gm03.data, 'comprehensive')
    assert len(gm03.data.comprehensive.elements) == 13
    assert sorted(list(gm03.data.comprehensive.elements.keys())) == ['address', 'citation', 'contact', 'data_identification', 'date', 'extent', 'extent_geographic_element', 'geographic_bounding_box', 'identification_point_of_contact', 'keywords', 'metadata', 'metadata_point_of_contact', 'responsible_party']  # noqa
    assert isinstance(gm03.data.comprehensive.date, list)
    assert len(gm03.data.comprehensive.date) == 1
    assert gm03.data.comprehensive.metadata.file_identifier == '41ac321f632e55cebf0508a2cea5d9023fd12d9ad46edd679f2c275127c88623fb9c9d29726bef7c'  # noqa
    assert gm03.data.comprehensive.metadata.date_stamp == '1999-12-31T12:00:00'
    assert gm03.data.comprehensive.metadata.language == 'de'

    # Test TID searching

    assert gm03.data.comprehensive.metadata.tid == 'xN6509077498146737843'

    search_tid = gm03.data.comprehensive.metadata.tid
    assert gm03.data.comprehensive.get_element_by_tid('404') is None
    assert gm03.data.comprehensive.get_element_by_tid(search_tid) is not None
    search_tid2 = gm03.data.comprehensive.extent.data_identification.ref
    assert search_tid2 == 'xN8036063300808707346'
    assert gm03.data.comprehensive.get_element_by_tid(search_tid2) is not None

    e = etree.parse(resource_file('gm03_example2.xml'))
    gm03 = GM03(e)
    assert gm03.data.comprehensive.geographic_bounding_box.extent_type_code == 'false'
    assert gm03.data.comprehensive.geographic_bounding_box.north_bound_latitude == '47.1865387201702'
    assert gm03.data.comprehensive.geographic_bounding_box.south_bound_latitude == '47.1234508676764'
    assert gm03.data.comprehensive.geographic_bounding_box.east_bound_longitude == '9.10597474389878'
    assert gm03.data.comprehensive.geographic_bounding_box.west_bound_longitude == '9.23798212070671'
