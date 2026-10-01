import pytest

from owslib.opensearch import OpenSearch


@pytest.mark.parametrize('tags_xml, expected_tags', [
    ('', []),
    ('<Tags/>', []),
    ('<Tags>   </Tags>', []),
    ('<Tags>earth observation</Tags>', ['earth', 'observation']),
])
def test_opensearch_description_optional_tags(tags_xml, expected_tags):
    xml = f'''<OpenSearchDescription xmlns="http://a9.com/-/spec/opensearch/1.1/">
        <ShortName>Example search</ShortName>
        <Description>Search public observations</Description>
        <Url type="application/atom+xml"
             template="https://example.com/search?q={{searchTerms}}"/>
        {tags_xml}
    </OpenSearchDescription>'''

    client = OpenSearch('https://example.com/opensearch', xml=xml)

    assert client.description.tags == expected_tags
    assert client.description.shortname == 'Example search'
    assert client.description.urls['application/atom+xml']['template'] == (
        'https://example.com/search?q={searchTerms}'
    )
