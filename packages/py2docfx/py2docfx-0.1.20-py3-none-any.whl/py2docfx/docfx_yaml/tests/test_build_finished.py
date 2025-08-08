import os
import pytest
import yaml
from translator import translator
from build_finished import build_finished, merge_data
from docfx_yaml.settings import API_ROOT
from .utils.test_utils import prepare_app_envs,load_rst_transform_to_doctree

@pytest.mark.sphinx('yaml', testroot='build-finished')
def test_build_finished(app):
    # Test data definition
    objectToGenXml = 'code_with_signature_and_docstring.TestClass'
    objectToGenXmlType = 'class'

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)

    translator(app, '', doctree)

    # Assert before build_finished
    target_node = app.env.docfx_yaml_classes[objectToGenXml][1]['syntax']
    parameter_node = target_node['parameters'][0]
    keyword_only_arg_node = target_node['keywordOnlyParameters'][0]
    positional_only_param_node = target_node['positionalOnlyParameters'][0]

    assert (parameter_node['id'] == 'self')
    parameter_node = target_node['parameters'][1]
    assert (parameter_node['id'] == 'parameter')
    assert ('type' not in parameter_node.keys())
    assert (keyword_only_arg_node['id'] == 'keyword_only_arg')
    assert ('type' not in keyword_only_arg_node.keys())
    assert (positional_only_param_node['id'] == 'positional_only_param')
    assert ('isRequired' not in positional_only_param_node.keys())
    # Act
    build_finished(app, None)

    # Assert after build_finished
    target_node = app.env.docfx_yaml_classes[objectToGenXml][1]['syntax']
    parameter_node = target_node['parameters'][0]
    keyword_only_arg_node = target_node['keywordOnlyParameters'][0]
    positional_only_param_node = target_node['positionalOnlyParameters'][0]

    assert (parameter_node['id'] == 'parameter')
    assert (parameter_node['type'] == ['<xref:str>'])
    assert (keyword_only_arg_node['id'] == 'keyword_only_arg')
    assert (keyword_only_arg_node['type'] == ['<xref:bool>'])
    assert (positional_only_param_node['id'] == 'positional_only_param')
    assert (positional_only_param_node['isRequired'] == True)

def test_merge_data():
    # Test data definition
    obj = {
        'uid': 'test_uid',
        'type': 'test_type',
        'syntax': {
            'parameters': [{'id': 'param1'}],
            'keywordOnlyParameters': [{'id': 'kwarg1'}]
        }
    }
    info_field_data = {
        'test_uid': {
            'type': 'test_type',
            'parameters': [{'id': 'param2'}],
            'keywordOnlyParameters': [{'id': 'kwarg2'}]
        }
    }
    yaml_data = []

    # Call the function to test
    merge_data(obj, info_field_data, yaml_data)

    # Assert the results
    assert 'type' in info_field_data['test_uid']
    assert info_field_data['test_uid']['type'] == 'test_type'
    assert len(obj['syntax']['parameters']) == 2
    assert len(obj['syntax']['keywordOnlyParameters']) == 2
    assert obj['syntax']['parameters'][0]['id'] == 'param2'
    assert obj['syntax']['parameters'][1]['id'] == 'param1'
    assert obj['syntax']['keywordOnlyParameters'][0]['id'] == 'kwarg2'
    assert obj['syntax']['keywordOnlyParameters'][1]['id'] == 'kwarg1'

def test_merge_data_no_syntax():
    # Test data definition
    obj = {
        'uid': 'test_uid',
        'type': 'test_type'
    }
    info_field_data = {
        'test_uid': {
            'type': 'test_type',
            'parameters': [{'id': 'param1'}],
            'keywordOnlyParameters': [{'id': 'kwarg1'}]
        }
    }
    yaml_data = []

    # Call the function to test
    merge_data(obj, info_field_data, yaml_data)

    # Assert the results
    assert 'syntax' in obj
    assert len(obj['syntax']['parameters']) == 1
    assert len(obj['syntax']['keywordOnlyParameters']) == 1
    assert obj['syntax']['parameters'][0]['id'] == 'param1'
    assert obj['syntax']['keywordOnlyParameters'][0]['id'] == 'kwarg1'

def test_merge_data_added_attribute():
    # Test data definition
    obj = {
        'uid': 'test_uid',
        'type': 'test_type',
        'syntax': {
            'parameters': [{'id': 'param1'}],
            'keywordOnlyParameters': [{'id': 'kwarg1'}],
            'added_attribute': [{'uid': 'attr1'}]
        }
    }
    info_field_data = {
        'test_uid': {
            'type': 'test_type',
            'parameters': [{'id': 'param2'}],
            'keywordOnlyParameters': [{'id': 'kwarg2'}]
        }
    }
    yaml_data = []

    # Call the function to test
    merge_data(obj, info_field_data, yaml_data)

    # Assert the results
    assert 'added_attribute' not in obj['syntax']
    assert len(yaml_data) == 1
    assert yaml_data[0]['uid'] == 'attr1'


@pytest.mark.sphinx('yaml', testroot='build-finished')
def test_build_finished_check_toc(tmp_path, app):
    app.builder.outdir = tmp_path
    app.config.project = 'azure-durable-functions'
    app.env.docfx_yaml_packages = {
        'azure.durable_functions':[{'uid':'azure.durable_functions','type':'package'}], 
        'azure.durable_functions.models':[{'uid':'azure.durable_functions.models','type':'package'}], 
        }
    app.env.docfx_yaml_modules = {
        'azure.durable_functions.constants':[{'uid':'azure.durable_functions.constants','type':'module'}],
        'azure.durable_functions.models.DurableEntityContext':[{'uid':'azure.durable_functions.models.DurableEntityContext','type':'module'}],
        }
    app.env.docfx_yaml_classes = {'azure.durable_functions.Blueprint':[{'uid':'azure.durable_functions.Blueprint','type':'class', 'inheritance':[]}]}

    # Act
    build_finished(app, None)

    # Assert after build_finished
    toc = None
    with open(os.path.join(tmp_path, API_ROOT, 'toc.yml'), 'r', encoding='utf-8') as file:
        toc = yaml.safe_load(file)
    
    assert 1 == len(toc)
    assert 'azure.durable_functions' == toc[0]['name']
    assert 'uid' not in toc[0] # root packages shouldn't have uid
    
    assert 4 == len(toc[0]['items'])
    assert 'Overview' == toc[0]['items'][0]['name']
    assert 'azure.durable_functions' == toc[0]['items'][0]['uid']
    
    assert 'models' == toc[0]['items'][1]['name']
    assert 'uid' not in toc[0]['items'][1]
    assert 2 == len(toc[0]['items'][1]['items'])
    assert 'Overview' == toc[0]['items'][1]['items'][0]['name']
    assert 'azure.durable_functions.models' == toc[0]['items'][1]['items'][0]['uid']
    assert 'DurableEntityContext' == toc[0]['items'][1]['items'][1]['name']
    assert 'azure.durable_functions.models.DurableEntityContext' == toc[0]['items'][1]['items'][1]['uid']

    assert 'constants' == toc[0]['items'][2]['name']
    assert 'azure.durable_functions.constants' == toc[0]['items'][2]['uid']

    assert 'Blueprint' == toc[0]['items'][3]['name']
    assert 'azure.durable_functions.Blueprint' == toc[0]['items'][3]['uid']

@pytest.mark.sphinx('yaml', testroot='build-finished')
def test_build_finished_check_root_package_type(tmp_path, app):
    app.builder.outdir = tmp_path
    app.config.project = 'azure-durable-functions'
    app.env.docfx_yaml_packages = {
        'azure.durable_functions':[{'uid':'azure.durable_functions','type':'package'}], 
        'azure.durable_functions.models':[{'uid':'azure.durable_functions.models','type':'package'}], 
        }
    app.env.docfx_yaml_modules = {
        'azure.durable_functions.constants':[{'uid':'azure.durable_functions.constants','type':'module'}],
        'azure.durable_functions.models.DurableEntityContext':[{'uid':'azure.durable_functions.models.DurableEntityContext','type':'module'}],
        }
    app.env.docfx_yaml_classes = {'azure.durable_functions.Blueprint':[{'uid':'azure.durable_functions.Blueprint','type':'class', 'inheritance':[]}]}

    # Act
    build_finished(app, None)

    # Assert after build_finished
    rootPackageYaml = None
    with open(os.path.join(tmp_path, API_ROOT, 'azure.durable_functions.yml'), 'r', encoding='utf-8') as file:
        rootPackageYaml = yaml.safe_load(file)
    assert 'rootImport' == rootPackageYaml['type']

    subPackageYaml = None
    with open(os.path.join(tmp_path, API_ROOT, 'azure.durable_functions.models.yml'), 'r', encoding='utf-8') as file:
        subPackageYaml = yaml.safe_load(file)
    assert 'import' == subPackageYaml['type']