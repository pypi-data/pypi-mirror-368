import pytest

from translator import translator

from .utils.test_utils import prepare_app_envs,prepare_refered_objects,load_rst_transform_to_doctree

@pytest.mark.sphinx('dummy', testroot='translator-returns')
def test_rst_return_complex_type(app):
    # Test data definition
    objectToGenXml = 'code_with_returns_rst.dummyClass.complex_type'
    objectToGenXmlType = 'function'

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    return_type = app.env.docfx_info_field_data[objectToGenXml]['return']['type'][0]
    assert(return_type == "<xref:typing.Any>[<xref:typing.Dict>[<xref:str>, <xref:typing.Any>]]")

@pytest.mark.sphinx('yaml', testroot='translator-returns')
def test_rst_return_user_designated_builtin_type(app):
    # Test data definition
    objectToGenXml = 'code_with_returns_rst.dummyClass.user_designated_builtin_type'
    objectToGenXmlType = 'function'

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    return_type = app.env.docfx_info_field_data[objectToGenXml]['return']['type'][0]
    assert(return_type == "<xref:collections.abc.MutableMapping>")

@pytest.mark.sphinx('dummy', testroot='translator-returns')
def test_rst_return_user_defined_type_with_same_name_as_builtin_type(app):
    # Test data definition
    objectToGenXml = 'code_with_returns_rst.dummyClass.user_defined_type_with_same_name_as_builtin_type'
    objectToGenXmlType = 'function'
    referedApis = [
        ('refered_objects.List', 'class')
    ]   

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    prepare_refered_objects(app, referedApis)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    return_type = app.env.docfx_info_field_data[objectToGenXml]['return']['type'][0]
    assert(return_type == "<xref:refered_objects.List>")

@pytest.mark.sphinx('yaml', testroot='translator-returns')
def test_rst_return_user_defined_type(app):
    # Test data definition
    objectToGenXml = 'code_with_returns_rst.dummyClass.user_defined_type'
    objectToGenXmlType = 'function'
    referedApis = [
        ('refered_objects.List', 'class')
    ]   

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    prepare_refered_objects(app, referedApis)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    return_type = app.env.docfx_info_field_data[objectToGenXml]['return']['type'][0]
    assert(return_type == "<xref:refered_objects.referee>")