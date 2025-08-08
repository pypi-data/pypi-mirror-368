import os
import sys

sys.path.insert(0, os.path.abspath("..\\docfx_yaml\\"))
sys.path.insert(0, os.path.abspath("..\\test_source_code\\"))

extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon", "yaml_builder"]

source_suffix = ".rst"

language = None

pygments_style = "sphinx"

napoleon_use_admonition_for_examples = True

autoclass_content = "both"

napoleon_preprocess_types = True
