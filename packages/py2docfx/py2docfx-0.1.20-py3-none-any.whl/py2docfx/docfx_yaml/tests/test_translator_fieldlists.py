import pytest

from sphinx.testing import restructuredtext
from sphinx.io import SphinxStandaloneReader
from sphinx import addnodes
from translator import translator

from .utils.test_utils import prepare_app_envs,prepare_refered_objects,load_rst_transform_to_doctree, do_autodoc

@pytest.mark.sphinx('dummy', testroot='translator-fieldlists')
def test_add_data_type(app):
    # Test data definition
    objectToGenXml = 'code_with_multiple_fieldlists'
    objectToGenXmlType = 'module'
    objectDataName= 'code_with_multiple_fieldlists.testClassA'    

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    app.env.docfx_info_uid_types[objectDataName] = 'data'
    translator(app, '', doctree)

    # Assert
    data = app.env.docfx_info_field_data[objectDataName]
    assert (len(data['variables']) == 2)
    assert (data['variables'][0]['id'] == 'paramA')
    assert (data['variables'][1]['id'] == 'paramB')
    assert (len(data['parameters']) == 2)
    assert (data['parameters'][0]['id'] == 'paramC')
    assert (data['parameters'][1]['id'] == 'paramD')
