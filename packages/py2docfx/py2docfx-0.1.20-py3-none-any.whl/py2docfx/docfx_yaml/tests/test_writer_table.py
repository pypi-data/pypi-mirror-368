import pytest
from sphinx.testing import restructuredtext
from sphinx.io import SphinxStandaloneReader
from sphinx import addnodes

from py2docfx.docfx_yaml.utils import transform_node
from py2docfx.docfx_yaml.tests.utils.test_utils import prepare_app_envs,prepare_refered_objects,load_rst_transform_to_doctree

@pytest.mark.sphinx('dummy', testroot='writer-table')
def test_table_docstring_to_markdown(app):
    # Test data definition
    objectToGenXml = 'code_with_table_desc.SampleClass'
    objectToGenXmlType = 'class'        

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    node = doctree[1][1][0][0][1][0]
    result = transform_node(app, node)

    # Assert
    expected = "**dummy_param** -- \n\nDummy Param\n\nTable:\n\n\n:::row:::\n:::column:::\n**header1**\n:::column-end:::\n:::column:::\n**header2**\n:::column-end:::\n:::column:::\n**header3**\n:::column-end:::\n:::column:::\n**header4**\n:::column-end:::\n:::row-end:::\n:::row:::\n:::column:::\na\n:::column-end:::\n:::column:::\nb\n:::column-end:::\n:::column:::\nc\n:::column-end:::\n:::column:::\nd\n:::column-end:::\n:::row-end:::\n:::row:::\n:::column:::\ne\n:::column-end:::\n:::column:::\nf\n:::column-end:::\n:::column:::\ng\n:::column-end:::\n:::column:::\nh\n:::column-end:::\n:::row-end:::\n"
    assert(result == expected)


@pytest.mark.sphinx('dummy', testroot='writer-table')
def test_list_table_docstring_to_markdown(app):
    # Test data definition
    objectToGenXml = 'code_with_table_desc.ExperimentalClass'
    objectToGenXmlType = 'class'        

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act - The list-table directive creates a table that should be at a different path
    # Try to find the table node in the doctree
    table_node = None
    for node in doctree.findall(lambda x: x.tagname == 'table'):
        table_node = node
        break
    
    if table_node is None:
        # Fallback to the original node if table is not found
        node = doctree[1][1][0][0][1][0]
    else:
        node = table_node
    
    result = transform_node(app, node)

    # Assert
    expected = "\n\n# Supported Functions\n:::row:::\n:::column:::\n**Boo**\n:::column-end:::\n:::column:::\n**API**\n:::column-end:::\n:::column:::\n**Example**\n:::column-end:::\n:::row-end:::\n:::row:::\n:::column:::\nFoo\n:::column-end:::\n:::column:::\nList Foo\n:::column-end:::\n:::column:::\n`GET /dummy/foo`\n:::column-end:::\n:::row-end:::\n:::row:::\n:::column:::\nBar\n:::column-end:::\n:::column:::\nCreate Bar\n:::column-end:::\n:::column:::\n`POST /dummy/bar`\n:::column-end:::\n:::row-end:::\n"
    assert(result == expected)
    