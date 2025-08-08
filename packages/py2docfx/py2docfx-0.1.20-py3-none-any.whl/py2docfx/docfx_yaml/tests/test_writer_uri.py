import pytest
from sphinx.testing import restructuredtext
from sphinx.io import SphinxStandaloneReader
from sphinx import addnodes

from py2docfx.docfx_yaml.utils import transform_node
from py2docfx.docfx_yaml.tests.utils.test_utils import prepare_app_envs,prepare_refered_objects,load_rst_transform_to_doctree

@pytest.mark.sphinx('dummy', testroot='writer-uri')
def test_http_link_in_summary_should_not_nest_parenthesis(app):
    # Test data definition
    objectToGenXml = 'code_with_uri.SampleClass'
    objectToGenXmlType = 'class'        

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    class_summary_result = transform_node(app, doctree[1][1][0])
    method1_summary_result = transform_node(app, doctree[1][1][2][1])
    method2_summary_result = transform_node(app, doctree[1][1][4][1])
    method3_summary_result = transform_node(app, doctree[1][1][6][1])

    # Assert
    # Shouldn't see something like [title]((link))
    class_summary_expected = 'Some summary with link [https://www.microsoft.com](https://www.microsoft.com)\n'
    method1_summary_expected = ("\n\n   This is a content issue link [microsoft](https://www.microsoft.com)\n   "
                               "We should not generate nested parenthesis causing docs validation warnings\n")
    method2_summary_expected = ("\n\n   This isn't a content issue link ([https://www.microsoft.com](https://www.microsoft.com))\n   "
                                "Should expect a transformed Markdown link.\n")
    method3_summary_expected = ("\n\n   This is a bare URL that shouldn't be transformed into a link\n   "
                                "because it's in the exclusion list: `https://management.azure.com`\n")
    assert(class_summary_expected == class_summary_result)
    assert(method1_summary_expected == method1_summary_result)
    assert(method2_summary_expected == method2_summary_result)
    assert(method3_summary_expected == method3_summary_result)
    