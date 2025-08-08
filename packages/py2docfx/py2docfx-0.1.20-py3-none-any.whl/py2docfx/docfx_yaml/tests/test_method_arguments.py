import pytest
from translator import translator
from .utils.test_utils import prepare_app_envs, load_rst_transform_to_doctree, do_autodoc

@pytest.mark.sphinx('dummy', testroot='method-arguments')
def test_method_with_three_type_of_arguments(app):
    # Test data definition
    objectToGenXml = 'code_with_all_arg_types.TestClass'
    objectToGenXmlType = 'class'
    # Arrange
    prepare_app_envs(app, objectToGenXml)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)
    # Assert
    argumentsDetail = app.env.docfx_yaml_classes[objectToGenXml][1]['syntax']
    parameters = argumentsDetail.get('parameters', None)
    keywordOnlyParameters = argumentsDetail.get('keywordOnlyParameters', None)
    positionalOnlyParameters = argumentsDetail.get('positionalOnlyParameters', None)
    assert (parameters != None)
    assert (keywordOnlyParameters != None)
    assert (positionalOnlyParameters != None)
    assert (parameters[1]['id'] == 'parameter_with_default_value')
    assert (parameters[1]['defaultValue'] == 'True')
    assert (keywordOnlyParameters[0]['id'] == 'keyword_only_arg')
    assert (keywordOnlyParameters[0]['defaultValue'] == 'keyword_only_arg_default_value')
    assert (positionalOnlyParameters[0]['id'] == 'positional_only_param')
    assert (positionalOnlyParameters[0]['defaultValue'] == '10')