import pytest
import inspect
from sphinx.config import Config
from docfx_yaml.process_doctree import (
    getParameterArgs,
    getKeywordOnlyParameters
)
from unittest.mock import Mock
from docfx_yaml.process_doctree import process_docstring
from sphinx.config import ENUM

# Test data for getParameterArgs
@pytest.mark.parametrize("func, expected_args", [
    (lambda a, b=2, *, c=3, d=4: None, [
        {'id': 'a', 'isRequired': True},
        {'id': 'b', 'defaultValue': '2'}
    ]),
    (lambda x, y, z=5: None, [
        {'id': 'x', 'isRequired': True},
        {'id': 'y', 'isRequired': True},
        {'id': 'z', 'defaultValue': '5'}
    ])
])
def test_getParameterArgs(func, expected_args):
    signature = inspect.signature(func)
    args = getParameterArgs(signature)
    assert args == expected_args

# Test data for getKeywordOnlyParameters
@pytest.mark.parametrize("func, expected_kwonlyargs", [
    (lambda a, b=2, *, c=3, d=4: None, [
        {'id': 'c', 'defaultValue': '3'},
        {'id': 'd', 'defaultValue': '4'}
    ]),
    (lambda x, y, *, z=5: None, [
        {'id': 'z', 'defaultValue': '5'}
    ])
])
def test_getKeywordOnlyParameters(func, expected_kwonlyargs):
    signature = inspect.signature(func)
    kwonlyargs = getKeywordOnlyParameters(signature)
    assert kwonlyargs == expected_kwonlyargs


@pytest.fixture
def app():
    app = Mock()
    app.config = Config()
    app.config.autoclass_content = 'both'
    app.config.autodoc_functions = True
    app.env = Mock()
    app.env.docfx_yaml_packages = {}
    app.env.docfx_yaml_modules = {}
    app.env.docfx_yaml_classes = {}
    app.env.docfx_yaml_functions = {}
    app.env.docfx_info_uid_types = {}
    return app


def test_process_docstring_class(app):
    class DummyClass:
        """This is a dummy class."""
        def method(self):
            pass

    process_docstring(app, 'class', 'test_module.DummyClass', DummyClass, {}, [])

    assert 'test_module.DummyClass' in app.env.docfx_yaml_classes
    assert len(app.env.docfx_yaml_classes['test_module.DummyClass']) == 1
    datam = app.env.docfx_yaml_classes['test_module.DummyClass'][0]
    assert datam['type'] == 'class'
    assert datam['name'] == 'DummyClass'
    assert datam['fullName'] == 'test_module.DummyClass'


def test_process_docstring_function(app):
    def dummy_function():
        """This is a dummy function."""
        pass

    process_docstring(app, 'function', 'test_module.dummy_function', dummy_function, {}, [])

    assert 'test_module.dummy_function' in app.env.docfx_yaml_functions
    assert len(app.env.docfx_yaml_functions['test_module.dummy_function']) == 1
    datam = app.env.docfx_yaml_functions['test_module.dummy_function'][0]
    assert datam['type'] == 'function'
    assert datam['name'] == 'dummy_function'
    assert datam['fullName'] == 'test_module.dummy_function'


def test_process_docstring_decorated_method(app):
    class DecoratedClass:
        """This is a decorated class."""
        @staticmethod
        def decorated_method(a, b=2, *, c=3):
            """This is a decorated method."""
            pass

    process_docstring(app, 'class', 'test_module.DecoratedClass', DecoratedClass, {}, [])

    assert 'test_module.DecoratedClass' in app.env.docfx_yaml_classes
    assert len(app.env.docfx_yaml_classes['test_module.DecoratedClass']) == 1
    datam = app.env.docfx_yaml_classes['test_module.DecoratedClass'][0]
    assert datam['type'] == 'class'
    assert datam['name'] == 'DecoratedClass'
    assert datam['fullName'] == 'test_module.DecoratedClass'

    process_docstring(app, 'method', 'test_module.DecoratedClass.decorated_method', DecoratedClass.decorated_method, {}, [])

    method_syntax_list = [m for m in app.env.docfx_yaml_classes['test_module.DecoratedClass'] if m['name'] == 'decorated_method']
    assert len(method_syntax_list) == 1
    method_syntax = method_syntax_list[0]['syntax']
    assert method_syntax['parameters'] == [
        {'id': 'a', 'isRequired': True},
        {'id': 'b', 'defaultValue': '2'}
    ]
    assert method_syntax['keywordOnlyParameters'] == [
        {'id': 'c', 'defaultValue': '3'}
    ]
    assert 'positionalOnlyParameters' not in method_syntax