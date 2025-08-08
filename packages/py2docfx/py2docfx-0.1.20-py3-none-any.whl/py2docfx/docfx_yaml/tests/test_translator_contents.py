import pytest

from sphinx.testing import restructuredtext
from sphinx.io import SphinxStandaloneReader
from sphinx import addnodes
from translator import translator

from .utils.test_utils import prepare_app_envs,prepare_refered_objects,load_rst_transform_to_doctree

@pytest.mark.sphinx('dummy', testroot='translator-contents')
def test_nestedBulletinList_checkNestedListSummaryIndent(app):
    # Test data definition
    objectToGenXml = 'code_with_docstring.ClassForTest.function_NestedBulletinList'
    objectToGenXmlType = 'function'        

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    summary = app.env.docfx_info_field_data[objectToGenXml]['summary']
    summaryList = [line for line in summary.splitlines() if line]
    assert (summaryList[2] == '   * Item1.SubItem1 ') # Subitem indent should be kept

@pytest.mark.sphinx('dummy', testroot='translator-contents')
def test_classWithCodeSummary_checkLastLineBracket(app):
    # Test data definition
    objectToGenXml = 'code_with_docstring.ClassWithCodeSummary'
    objectToGenXmlType = 'class'        

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    summary = app.env.docfx_info_field_data[objectToGenXml]['summary']
    summaryList = [line for line in summary.splitlines() if line]
    assert (summaryList[-1] == '}') # Translator shouldn't skip last line of bracket (even there's no alphabet =or digit in this line)
