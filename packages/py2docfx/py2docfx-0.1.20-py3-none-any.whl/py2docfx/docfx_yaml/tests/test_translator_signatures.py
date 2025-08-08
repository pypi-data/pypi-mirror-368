import pytest

from sphinx.testing import restructuredtext
from sphinx.io import SphinxStandaloneReader
from sphinx import addnodes
from translator import translator

from .utils.test_utils import prepare_app_envs,prepare_refered_objects,load_rst_transform_to_doctree

@pytest.mark.sphinx('dummy', testroot='translator-signatures')
def test_basicAsyncMethod_signatureStartsWithAsync(app):
    # Test data definition
    objectToGenXml = 'code_with_docstring.ClassForTest.function_basicAsyncMethod'
    objectToGenXmlType = 'function'        

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    signature = app.env.docfx_info_field_data[objectToGenXml]['content']
    assert (signature == 'async function_basicAsyncMethod(self, param1)')

@pytest.mark.sphinx('dummy', testroot='translator-signatures')
def test_basicNonAsyncMethod_signatureCorrect(app):
    # Test data definition
    objectToGenXml = 'code_with_docstring.ClassForTest.function_basicMethod'
    objectToGenXmlType = 'function'        

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    signature = app.env.docfx_info_field_data[objectToGenXml]['content']
    assert (signature == 'function_basicMethod(self, param1)')