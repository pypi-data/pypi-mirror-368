import pytest

from sphinx.testing import restructuredtext
from sphinx.io import SphinxStandaloneReader
from sphinx import addnodes
from translator import translator

from .utils.test_utils import prepare_app_envs,prepare_refered_objects,load_rst_transform_to_doctree, do_autodoc

@pytest.mark.sphinx('dummy', testroot='translator-data')
def test_add_data_type(app):
    # Test data definition
    objectToGenXml = 'code_with_data'
    objectToGenXmlType = 'module'
    objectDataName= 'code_with_data.test'    

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    app.env.docfx_info_uid_types[objectDataName] = 'data'
    translator(app, '', doctree)

    # Assert
    data = app.env.docfx_info_field_data[objectDataName]
    assert (data['summary'] == 'test test test')
    assert (data['content'] == 'test = <code_with_data.ClassForTest object>')