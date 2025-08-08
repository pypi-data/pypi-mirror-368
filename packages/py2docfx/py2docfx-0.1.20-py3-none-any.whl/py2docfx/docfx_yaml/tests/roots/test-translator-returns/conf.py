import os
import sys

sys.path.insert(0, os.path.abspath('.'))

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon', 'yaml_builder']

class includeTest:
    pass

# The suffix of source filenames.
source_suffix = '.rst'

autodoc_mock_imports = [
    'dummy'
]

nitpicky = True

autodoc_default_options = {
    'inherited-members': True
}

napoleon_preprocess_types = True
