import pytest

from sphinx.testing import restructuredtext
from sphinx.io import SphinxStandaloneReader
from sphinx import addnodes
from translator import translator

from .utils.test_utils import prepare_app_envs,prepare_refered_objects,load_rst_transform_to_doctree, do_autodoc

@pytest.mark.sphinx('dummy', testroot='numpy-syntax')
def test_numpy_style_default(app):
    # Test data definition
    objectToGenXml = 'code_with_numpy.TestClass.test_method'
    objectToGenXmlType = 'function'

    # Arrange
    prepare_app_envs(app, objectToGenXml)
    doctree = load_rst_transform_to_doctree(app, objectToGenXmlType, objectToGenXml)
    
    # Act
    translator(app, '', doctree)

    # Assert
    parameterDetail = app.env.docfx_info_field_data[objectToGenXml]['parameters'][0]
    assert (parameterDetail["defaultValue"] == 'True')
