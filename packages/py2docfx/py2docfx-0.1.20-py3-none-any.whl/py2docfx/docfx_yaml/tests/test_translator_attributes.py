import pytest
from sphinx.testing import restructuredtext
from sphinx.io import SphinxStandaloneReader
from sphinx import addnodes
from translator import translator
from .utils.test_utils import prepare_app_envs,prepare_refered_objects,load_rst_transform_to_doctree

@pytest.mark.sphinx('dummy', testroot='translator-attributes')
def test_aliasAttribute_skip(app):
    # Test data definition
    objectToGenXml = 'code_with_import'
    objectToGenXmlType = 'module'        
    referedApis = [
        ('refered_objects.ReferenceType1', 'class'),
    ]

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    prepare_refered_objects(app, referedApis)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    assert (objectToGenXml+'.alias1' not in app.env.docfx_info_field_data) # Alias attribute skipped


@pytest.mark.sphinx('dummy', testroot='translator-attributes')
def test_exceptionWithAttribute_checkAddedAttribute(app):
    # Test data definition
    objectToGenXml = 'code_with_docstring.ExceptionWithAttribute'
    objectToGenXmlType = 'exception'

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    # Attribute should be added to Exception's `added_attribute` property
    assert (app.env.docfx_info_field_data[objectToGenXml]['added_attribute'][0]['uid'] == 'code_with_docstring.ExceptionWithAttribute.attribute1')

@pytest.mark.sphinx('dummy', testroot='translator-attributes')
def test_classWithAttribute_checkAddedAttributeSummary(app):
    # Test data definition
    objectToGenXml = 'code_with_docstring.ClassWithAttribute'
    objectToGenXmlType = 'class'

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    # Attribute should be added to Exception's `added_attribute` property
    assert (app.env.docfx_info_field_data[objectToGenXml]['added_attribute'][0]['uid'] == 'code_with_docstring.ClassWithAttribute.attribute1')
    assert (app.env.docfx_info_field_data[objectToGenXml]['added_attribute'][0]['summary'] == 'Attribute 1 description')

@pytest.mark.sphinx('dummy', testroot='translator-attributes')
def test_duplicateNameClassWithAttribute_attributePutUnderCorrectClass(app):
    # Test data definition
    objectToGenXml1 = 'code_with_docstring.DuplicateNameClassWithAttribute'
    objectToGenXml2 = 'code_with_docstring2.DuplicateNameClassWithAttribute'
    objectToGenXmlType = 'class'

    # Arrange
    prepare_app_envs(app, objectToGenXml1)
    prepare_app_envs(app, objectToGenXml2)
    doctree1 = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml1)
    doctree2 = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml2)
    
    # Act
    translator(app, '', doctree1)
    translator(app, '', doctree2)

    # Assert
    # Attribute should be added to Exception's `added_attribute` property
    assert (app.env.docfx_info_field_data[objectToGenXml1]['added_attribute'][0]['uid'] == 'code_with_docstring.DuplicateNameClassWithAttribute.attribute2')
    assert(app.env.docfx_info_field_data[objectToGenXml1]['added_attribute'][0]['summary'] == 'Attribute2 under code_with_docstring.DuplicateNameClassWithAttribute')
    assert (app.env.docfx_info_field_data[objectToGenXml2]['added_attribute'][0]['uid'] == 'code_with_docstring2.DuplicateNameClassWithAttribute.attribute2')
    assert(app.env.docfx_info_field_data[objectToGenXml2]['added_attribute'][0]['summary'] == 'Attribute2 under code_with_docstring2.DuplicateNameClassWithAttribute')

@pytest.mark.sphinx('dummy', testroot='translator-attributes')
def test_attributeBeingDefinedInBothCodeAndClassSummary_attributeSummaryShouldShow(app):
    # Test data definition
    objectToGenXml1 = 'code_with_docstring3.DummyClass'
    objectToGenXml2 = 'code_with_docstring3.UpperLevelClass.LowerLevelClass'
    objectToGenXmlType = 'class'

    # Arrange
    prepare_app_envs(app, objectToGenXml1)
    prepare_app_envs(app, objectToGenXml2)
    doctree1 = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml1)
    doctree2 = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml2)

    # Act
    translator(app, '', doctree1)
    translator(app, '', doctree2)

    # Assert
    # Attribute summary should be added
    assert(app.env.docfx_info_field_data[objectToGenXml1]['added_attribute'][0]['uid'] == 'code_with_docstring3.DummyClass.SampleAttribute')
    assert(app.env.docfx_info_field_data[objectToGenXml1]['added_attribute'][0]['summary'] == 'just a test attribute')
    assert(app.env.docfx_info_field_data[objectToGenXml2]['added_attribute'][0]['uid'] == 'code_with_docstring3.UpperLevelClass.LowerLevelClass.SampleAttribute')
    assert(app.env.docfx_info_field_data[objectToGenXml2]['added_attribute'][0]['summary'] == 'just a test attribute')
