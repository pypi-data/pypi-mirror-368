import pytest

from sphinx.testing import restructuredtext
from sphinx.io import SphinxStandaloneReader
from sphinx import addnodes
from translator import translator

from .utils.test_utils import prepare_app_envs,prepare_refered_objects,load_rst_transform_to_doctree

@pytest.mark.sphinx('dummy', testroot='translator-exceptions')
def test_docstringWithDescriptionRaise_modelShouldContainExceptionObejctWithDescription(app):
    # Test data definition
    objectToGenXml = 'code_with_docstring.ClassForTest.function_docstringWithDescriptionRaise'
    objectToGenXmlType = 'function'        
    referedApis = [
        ('refered_objects.ExceptionType1', 'class'),
    ]

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    prepare_refered_objects(app, referedApis)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    exceptionModels = app.env.docfx_info_field_data[objectToGenXml]['exceptions']
    assert (exceptionModels[0]['type'] == 'refered_objects.ExceptionType1')
    assert (exceptionModels[0]['description'] == 'if condition 1 happens')

@pytest.mark.sphinx('dummy', testroot='translator-exceptions')
def test_docstringWithDescriptionRaiseContainingNestedCodeSyntax_modelShouldContainExceptionObejctWithDescription(app):
    # Test data definition
    objectToGenXml = 'code_with_docstring.ClassForTest.function_docstringWithDescriptionRaiseContainingNestedCodeSyntax'
    objectToGenXmlType = 'function'        
    referedApis = [
        ('refered_objects.ExceptionType1', 'class'),
        ('refered_objects.ExceptionType2', 'class'),
    ]

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    prepare_refered_objects(app, referedApis)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    exceptionModels = app.env.docfx_info_field_data[objectToGenXml]['exceptions']
    assert (exceptionModels[0]['type'] == 'refered_objects.ExceptionType1')
    assert (exceptionModels[0]['description'] == 'if `condition` 1 happens')
    assert (exceptionModels[1]['type'] == 'refered_objects.ExceptionType2')
    assert (exceptionModels[1]['description'] == 'if *condition* 2 happens')

@pytest.mark.sphinx('dummy', testroot='translator-exceptions')
def test_docstringWithMultipleRaiseType_modelShouldContainMultipleExceptionObejcts(app):
    # Test data definition
    objectToGenXml = 'code_with_docstring.ClassForTest.function_docstringWithMultipleRaiseType'
    objectToGenXmlType = 'function'        
    referedApis = [
        ('refered_objects.ExceptionType1', 'class'),
        ('refered_objects.ExceptionType2', 'class')
    ]

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    prepare_refered_objects(app, referedApis)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    exceptionModels = app.env.docfx_info_field_data[objectToGenXml]['exceptions']
    assert (exceptionModels[0]['type'] == 'refered_objects.ExceptionType1')
    assert (exceptionModels[1]['type'] == 'refered_objects.ExceptionType2')

@pytest.mark.sphinx('dummy', testroot='translator-exceptions')
def test_docstringWithMultipleRaiseTypeWithLineBreaker_modelShouldContainMultipleExceptionObejcts(app):
    # Test data definition
    objectToGenXml = 'code_with_docstring.ClassForTest.function_docstringWithMultipleRaiseTypeWithLineBreaker'
    objectToGenXmlType = 'function'        
    referedApis = [
        ('refered_objects.ExceptionType1', 'class'),
        ('refered_objects.ExceptionType2', 'class')
    ]

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    prepare_refered_objects(app, referedApis)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    exceptionModels = app.env.docfx_info_field_data[objectToGenXml]['exceptions']
    assert (exceptionModels[0]['type'] == 'refered_objects.ExceptionType1')
    assert (exceptionModels[1]['type'] == 'refered_objects.ExceptionType2')
    assert ('description' not in exceptionModels[0]) # Description should contain alphabets or digits instead of pure punctuation
    assert ('description' not in exceptionModels[1])

@pytest.mark.sphinx('dummy', testroot='translator-exceptions')
def test_docstringWithMultipleInlineRaiseTypeConnectedByOr_modelShouldContainMultipleExceptionObejcts(app):
    # Test data definition
    objectToGenXml = 'code_with_docstring.ClassForTest.function_docstringWithMultipleInlineRaiseTypeConnectedByOr'
    objectToGenXmlType = 'function'        
    referedApis = [
        ('refered_objects.ExceptionType1', 'class'),
        ('refered_objects.ExceptionType2', 'class')
    ]

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    prepare_refered_objects(app, referedApis)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    exceptionModels = app.env.docfx_info_field_data[objectToGenXml]['exceptions']
    assert (exceptionModels[0]['type'] == 'refered_objects.ExceptionType1')
    assert (exceptionModels[1]['type'] == 'refered_objects.ExceptionType2')

@pytest.mark.sphinx('dummy', testroot='translator-exceptions')
def test_docstringWithMultipleInlineRaiseDirectives_modelShouldContainMultipleExceptionObejctsWithDescription(app):
    # Test data definition
    objectToGenXml = 'code_with_docstring.ClassForTest.function_docstringWithMultipleInlineRaiseDirectives'
    objectToGenXmlType = 'function'        
    referedApis = [
        ('refered_objects.ExceptionType1', 'class'),
        ('refered_objects.ExceptionType2', 'class')
    ]

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    prepare_refered_objects(app, referedApis)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    exceptionModels = app.env.docfx_info_field_data[objectToGenXml]['exceptions']
    assert (exceptionModels[0]['type'] == 'refered_objects.ExceptionType1')
    assert (exceptionModels[1]['type'] == 'refered_objects.ExceptionType2')
    assert (exceptionModels[0]['description'] == 'if condition 1 happens')
    assert (exceptionModels[1]['description'] == 'if condition 2 happens')

@pytest.mark.sphinx('dummy', testroot='translator-exceptions')
def test_docstringWithExplicitTitleAndReferenceRaiseDirectives_modelShouldContainCorrectExceptionTarget(app):
    # Test data definition
    objectToGenXml = 'code_with_docstring.ClassForTest.function_docstringWithExplicitTitleAndReferenceRaiseDirectives'
    objectToGenXmlType = 'function'        
    referedApis = [
        ('refered_objects.ExceptionType1', 'class')
    ]

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    prepare_refered_objects(app, referedApis)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    exceptionModels = app.env.docfx_info_field_data[objectToGenXml]['exceptions']
    assert (exceptionModels[0]['type'] == 'refered_objects.ExceptionType1')
    assert (exceptionModels[0]['description'] == 'if condition 1 happens')

@pytest.mark.sphinx('dummy', testroot='translator-exceptions')
def test_docstringWithExplicitTitleAndReferenceRaiseDirectives_modelShouldContainCorrectExceptionTarget(app):
    # Test data definition
    objectToGenXml = 'code_with_docstring.ClassForTest.function_docstringWithExplicitTitleAndReferenceRaiseDirectives'
    objectToGenXmlType = 'function'        
    referedApis = [
        ('refered_objects.ExceptionType1', 'class')
    ]

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    prepare_refered_objects(app, referedApis)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    exceptionModels = app.env.docfx_info_field_data[objectToGenXml]['exceptions']
    assert (exceptionModels[0]['type'] == 'refered_objects.ExceptionType1')
    assert (exceptionModels[0]['description'] == 'if condition 1 happens')

@pytest.mark.sphinx('dummy', testroot='translator-exceptions')
def test_docstringWithIncorrectSyntax_shouldTransferToType(app):
    # Test data definition
    objectToGenXml = 'code_with_docstring.ClassForTest.function_docstringWithIncorrectSyntax'
    objectToGenXmlType = 'function'        
    referedApis = [
        ('refered_objects.ExceptionType1', 'class')
    ]

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    prepare_refered_objects(app, referedApis)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    exceptionModels = app.env.docfx_info_field_data[objectToGenXml]['exceptions']
    assert (exceptionModels[0]['type'] == '<xref:if the HTTP response status is not in >[<xref:200>]<xref:.>')

@pytest.mark.sphinx('dummy', testroot='translator-exceptions')
def test_docstringWithMultipleRaiseDeclarationSections_shouldIncludeAllExcetion(app):
    # Test data definition
    objectToGenXml = 'code_with_docstring.ClassForTest.function_docstringWithMultipleRaiseDeclarationSections'
    objectToGenXmlType = 'function'        
    referedApis = [
        ('refered_objects.ExceptionType1', 'class'),
        ('refered_objects.ExceptionType2', 'class')
    ]

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    prepare_refered_objects(app, referedApis)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    exceptionModels = app.env.docfx_info_field_data[objectToGenXml]['exceptions']
    assert (exceptionModels[0]['type'] == 'refered_objects.ExceptionType1')
    assert (exceptionModels[0]['description'] == 'if condition 1 happens')
    assert (exceptionModels[1]['type'] == 'refered_objects.ExceptionType2')
    assert (exceptionModels[1]['description'] == 'if condition 2 happens')