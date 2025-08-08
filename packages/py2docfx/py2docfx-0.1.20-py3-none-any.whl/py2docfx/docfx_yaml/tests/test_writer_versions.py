import pytest
from sphinx.testing import restructuredtext
from sphinx.io import SphinxStandaloneReader
from sphinx import addnodes

from translator import translator
from py2docfx.docfx_yaml.tests.utils.test_utils import prepare_app_envs,prepare_refered_objects,load_rst_transform_to_doctree

def helper_assert_summary_contains_italic(summary, enclosed):
    assert '*' + enclosed + '*' in summary.replace('\n','')

@pytest.mark.sphinx('yaml', testroot='writer-versions')
def test_version_directives_should_be_italic(app):
    # Test data definition
    objectToGenXml = 'code_with_version_directives.testClassA'
    objectToGenXmlType = 'class'        

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)
    
    helper_assert_summary_contains_italic(
        app.env.docfx_info_field_data['code_with_version_directives.testClassA']['summary'],
        'New in version 0.0.1:')
    helper_assert_summary_contains_italic(
        app.env.docfx_info_field_data['code_with_version_directives.testClassA']['variables'][0]['description'],
        'New in version 0.0.2.')
    helper_assert_summary_contains_italic(
        app.env.docfx_info_field_data['code_with_version_directives.testClassA.method']['summary'],
        'Changed in version 0.0.1.')
    helper_assert_summary_contains_italic(
        app.env.docfx_info_field_data['code_with_version_directives.testClassA.method']['summary'],
        'New in version 0.1.0:')
    helper_assert_summary_contains_italic(
        app.env.docfx_info_field_data['code_with_version_directives.testClassA.method']['summary'],
        'New in version 0.2.0:')
    helper_assert_summary_contains_italic(
        app.env.docfx_info_field_data['code_with_version_directives.testClassA.method']['summary'],
        'Deprecated since version 1.1.0.')
    helper_assert_summary_contains_italic(
        app.env.docfx_info_field_data['code_with_version_directives.testClassA.method']['parameters'][0]['description'],
        'New in version 1.0.0.')
    helper_assert_summary_contains_italic(
        app.env.docfx_info_field_data['code_with_version_directives.testClassA.method']['parameters'][0]['description'],
        'Changed in version 0.0.3.')
    helper_assert_summary_contains_italic(
        app.env.docfx_info_field_data['code_with_version_directives.testClassA.method']['parameters'][1]['description'],
        'New in version 0.0.2.')
    helper_assert_summary_contains_italic(
        app.env.docfx_info_field_data['code_with_version_directives.testClassA.method']['keywordOnlyParameters'][0]['description'],
        'New in version 0.0.2.')
    helper_assert_summary_contains_italic(
        app.env.docfx_info_field_data['code_with_version_directives.testClassA.method']['keywordOnlyParameters'][0]['description'],
        'Changed in version 0.0.3.')