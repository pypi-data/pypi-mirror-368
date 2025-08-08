from py2docfx.docfx_yaml.utils import transform_node
from functools import partial
from sphinx.ext.autodoc.directive import DocumenterBridge, process_documenter_options
from sphinx.util.docutils import LoggingReporter
from sphinx.testing import restructuredtext
from sphinx.transforms import SphinxTransformer
from sphinx.transforms.post_transforms import ReferencesResolver
from unittest.mock import Mock

def do_autodoc(app, objtype, name, all_members=False, options=None):
    # Read a python class and generate autodoc RST
    if options is None:
        options = {}
    app.env.temp_data.setdefault('docname', 'index')  # set dummy docname
    doccls = app.registry.documenters[objtype]
    docoptions = process_documenter_options(doccls, app.config, options)
    state = Mock()
    state.document.settings.tab_width = 8
    bridge = DocumenterBridge(app.env, LoggingReporter(''), docoptions, 1, state)
    documenter = doccls(bridge, name)
    documenter.generate(all_members=all_members)
    return '\n'.join(list(bridge.result))

def resolve_reference_in_doctree(doctree, app):
    # Resolve "pending_xref" tags in doctree to "reference" tags
    app.env.temp_data.setdefault('docname', 'index')
    transformer = SphinxTransformer(doctree)
    transformer.set_environment(app.env)
    transformer.add_transforms([ReferencesResolver])
    transformer.apply_transforms()

def prepare_app_envs(app, objectToGenXml):
    # Prepare environment variables docfx_yaml needs
    app.docfx_transform_node = partial(transform_node, app)
    if not hasattr(app.env, 'docfx_info_uid_types'):
        app.env.docfx_info_uid_types = {objectToGenXml:None}
    else:
        app.env.docfx_info_uid_types[objectToGenXml] = None
    if not hasattr(app.env, 'docfx_info_field_data'):
        app.env.docfx_info_field_data = {}
    if not hasattr(app.env, 'docfx_yaml_modules'):
        app.env.docfx_yaml_modules = {}
    if not hasattr(app.env, 'docfx_root'):
        app.env.docfx_root = None
    if not hasattr(app.env, 'docfx_branch'):
        app.env.docfx_branch = None
    if not hasattr(app.env, 'docfx_remote'):
        app.env.docfx_remote = None
def prepare_refered_objects(app, referedApis):
    # Load refered objects to sphinx app domain for referenced by "resolve_reference_in_doctree"
    for referedApi in referedApis:
        (referedApiName, referedApiType) = referedApi
        referedApiRst = do_autodoc(app, referedApiType, referedApiName)
        _ = restructuredtext.parse(app, referedApiRst)    

def load_rst_transform_to_doctree(app, testObjectType, testObjectName):
    # Load and transform python code with docstring to doctree
    if testObjectType in ['module','class', 'exception']:
        options = {'undoc-members':'True'} # undoc_members will keep members without document (Keep consistent with pipeline settings)
    else:
        options = None
    rst = do_autodoc(app, testObjectType, testObjectName, True, options) 
    #[note]:should be alias of :class:`refered_objects.ReferenceType1` -> :py:class:`refered_objects.ReferenceType1`
    app.env.temp_data['default_domain'] = app.env.get_domain('py')
    doctree = restructuredtext.parse(app, rst)
    resolve_reference_in_doctree(doctree, app) # If there's refered objects in docstring, then need this step to resolve
    return doctree