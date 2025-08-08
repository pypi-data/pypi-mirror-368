import pytest

from translator import translator

from .utils.test_utils import prepare_app_envs,load_rst_transform_to_doctree

@pytest.mark.sphinx('yaml', testroot='translator-typing')
def test_with_typing(app):
    # Test data definition
    objectToGenXml = 'code_with_typing.TestClass.test_method_with_typing'
    objectToGenXmlType = 'function'

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    parameterDetail = app.env.docfx_info_field_data[objectToGenXml]['parameters'][0]
    assert (parameterDetail["type"] == ['<xref:list>[<xref:typing.Container>]'])
    
@pytest.mark.sphinx('yaml', testroot='translator-typing')
def test_without_typing(app):
    # Test data definition
    objectToGenXml = 'code_with_typing.TestClass.test_method_without_typing'
    objectToGenXmlType = 'function'

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    parameterDetail = app.env.docfx_info_field_data[objectToGenXml]['parameters'][0]
    assert (parameterDetail["type"] == ['<xref:list>[<xref:foo.boo.dummy.Container>]'])
