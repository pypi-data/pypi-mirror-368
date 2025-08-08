# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import inspect
import os
import re

from utils import transform_string
from enum import EnumMeta
from importlib import import_module
from logger import get_package_logger

PACKAGE = 'package'
METHOD = 'method'
FUNCTION = 'function'
DATA = 'data'
MODULE = 'module'
CLASS = 'class'
EXCEPTION = 'exception'
ATTRIBUTE = 'attribute'
PROPERTY = 'property'
REFMETHOD = 'meth'
REFFUNCTION = 'func'
REF_PATTERN = ':(py:)?(func|class|meth|mod|ref):`~?[a-zA-Z_\.<> ]*?`'
INITPY = '__init__.py'

def _fullname(obj):
    """
    Get the fullname from a Python object
    """
    return obj.__module__ + "." + obj.__name__


def _get_cls_module(_type, name):
    """
    Get the class and module name for an object

    .. _sending:

    Foo

    """
    cls = None
    if _type in [FUNCTION, EXCEPTION, DATA]:
        module = '.'.join(name.split('.')[:-1])
    elif _type in [METHOD, ATTRIBUTE]:
        cls = '.'.join(name.split('.')[:-1])
        module = '.'.join(name.split('.')[:-2])
    elif _type in [CLASS]:
        cls = name
        module = '.'.join(name.split('.')[:-1])
    elif _type in [MODULE]:
        module = name
    else:
        return (None, None)
    return (cls, module)


def _refact_example_in_module_summary(lines):
    new_lines = []
    block_lines = []
    example_block_flag = False
    for line in lines:
        if line.startswith('.. admonition:: Example'):
            example_block_flag = True
            line = '### Example\n\n'
            new_lines.append(line)
        elif example_block_flag and len(line) != 0 and not line.startswith('   '):
            example_block_flag = False
            new_lines.append(''.join(block_lines))
            new_lines.append(line)
            block_lines[:] = []
        elif example_block_flag:
            if line == '   ':  # origianl line is blank line ('\n').
                line = '\n'  # after outer ['\n'.join] operation,
                # this '\n' will be appended to previous line then. BINGO!
            elif line.startswith('   '):
                # will be indented by 4 spaces according to yml block syntax.
                # https://learnxinyminutes.com/docs/yaml/
                line = ' ' + line + '\n'
            block_lines.append(line)

        else:
            new_lines.append(line)
    return new_lines


def _resolve_reference_in_module_summary(lines):
    new_lines = []
    for line in lines:
        matched_objs = list(re.finditer(REF_PATTERN, line))
        new_line = line
        for matched_obj in matched_objs:
            start = matched_obj.start()
            end = matched_obj.end()
            matched_str = line[start:end]
            if '<' in matched_str and '>' in matched_str:
                # match string like ':func:`***<***>`'
                index = matched_str.index('<')
                ref_name = matched_str[index+1:-2]
            else:
                # match string like ':func:`~***`' or ':func:`***`'
                index = matched_str.index(
                    '~') if '~' in matched_str else matched_str.index('`')
                ref_name = matched_str[index+1:-1]
            new_line = new_line.replace(
                matched_str, '<xref:{}>'.format(ref_name))
        new_lines.append(new_line)
    return new_lines

def getParameterArgs(signature):
    args = []
    for param in signature.parameters.values():
        if param.kind in [param.POSITIONAL_OR_KEYWORD, param.POSITIONAL_ONLY]:
            arg = {'id': param.name}
            if param.default is not param.empty:
                if ' at 0x' not in str(param.default):
                    arg['defaultValue'] = str(param.default)
                else:
                    arg['isRequired'] = False
            args.append(arg)
    return args

def getKeywordOnlyParameters(signature):
    keyword_only_args = []
    for param in signature.parameters.values():
        if param.kind == param.KEYWORD_ONLY:
            kwarg = {'id': param.name}
            if param.default is not param.empty:
                kwarg['defaultValue'] = str(param.default)
            keyword_only_args.append(kwarg)
    return keyword_only_args

def getpositionalOnlyParameters(signature):
    positional_only_param = []
    # check if there is positional only params
    positional_only_param_list = [param
            for param in signature.parameters.values()
            if param.kind == param.POSITIONAL_ONLY]
    if positional_only_param_list:
        count = 0
        for po_param in positional_only_param_list:
            if po_param.name != 'self':
                positional_only_param.append({'id': po_param.name})

                try:
                    default_value = str(po_param.default)
                except KeyError:
                    # if the default value is not available, set it to inspect._empty
                    default_value = "<class 'inspect._empty'>"
                
                if default_value != "<class 'inspect._empty'>":
                    positional_only_param[count]['defaultValue'] = default_value
                
                count += 1
    return positional_only_param

def removePositonalOnlyFromArgs(args, positional_only_params):
    # Create a set of ids from positional_only_params for efficient lookup
    positional_only_params_ids = set(obj['id'] for obj in positional_only_params)

    # Filter out objects from args array whose id is in the set of positional_only_params_ids
    filtered_a = [obj for obj in args if obj['id'] not in positional_only_params_ids]

    return filtered_a

def _create_datam(app, cls, module, name, _type, obj, lines=None):
    """
    Build the data structure for an autodoc class
    """
    py2docfx_logger = get_package_logger(__name__)
    if lines is None:
        lines = []
    short_name = name.split('.')[-1]
    args = []
    keyword_only_args = []
    positional_only_params = []
    try:
        if _type in [CLASS, METHOD, FUNCTION]:
            if not (_type  == CLASS and isinstance(type(obj).__call__, type(EnumMeta.__call__))):       
                signature = inspect.signature(obj)
                args = getParameterArgs(signature)
                keyword_only_args = getKeywordOnlyParameters(signature)
                positional_only_params = getpositionalOnlyParameters(signature)
                # The args will contain both regular args and positional only params
                # so we need to remove the positional only args from params
                if positional_only_params:
                    args = removePositonalOnlyFromArgs(args, positional_only_params)

    except Exception as e:
        msg = "Can't get argspec for {}: {}. Exception: {}".format(type(obj), name, e)
        py2docfx_logger.warning(msg)

    datam = {
        'module': module if module else None,
        'uid': name,
        'type': _type,
        'name': short_name,
        'fullName': name,
        'langs': ['python'],
    }

    # Only add summary to parts of the code that we don't get it from the monkeypatch
    if _type in [MODULE, PACKAGE]:
        lines = _resolve_reference_in_module_summary(lines)
        summary = app.docfx_transform_string(
            '\n'.join(_refact_example_in_module_summary(lines)))
        if summary:
            datam['summary'] = summary.strip(" \n\r\r")

    if args or keyword_only_args or positional_only_params:
        datam['syntax'] = {}
        if args:
            datam['syntax']['parameters'] = args
        if keyword_only_args:
            datam['syntax']['keywordOnlyParameters'] = keyword_only_args
        if positional_only_params:
            datam['syntax']['positionalOnlyParameters'] = positional_only_params
    if cls:
        datam[CLASS] = cls
    if _type in [CLASS, MODULE, PACKAGE]:
        datam['children'] = []
        datam['references'] = []

    return datam


def insert_inheritance(app, _type, obj, datam):

    def collect_inheritance(base, to_add):
        for new_base in base.__bases__:
            new_add = {'type': _fullname(new_base)}
            collect_inheritance(new_base, new_add)
            if 'inheritance' not in to_add:
                to_add['inheritance'] = []
            to_add['inheritance'].append(new_add)

    if hasattr(obj, '__bases__'):
        if 'inheritance' not in datam:
            datam['inheritance'] = []
        for base in obj.__bases__:
            to_add = {'type': _fullname(base)}
            collect_inheritance(base, to_add)
            datam['inheritance'].append(to_add)


def insert_children_on_module(app, _type, datam):
    """
    Insert children of a specific module
    """

    if MODULE not in datam or datam[MODULE] not in app.env.docfx_yaml_modules:
        return
    insert_module = app.env.docfx_yaml_modules[datam[MODULE]]
    # Find the module which the datam belongs to
    for obj in insert_module:
        # Add standardlone function to global class
        if _type in [FUNCTION, DATA] and \
                obj['type'] == MODULE and \
                obj[MODULE] == datam[MODULE]:
            obj['children'].append(datam['uid'])

            # If it is a function, add this to its module. No need for class and module since this is
            # done before calling this function.
            insert_module.append(datam)

            # obj['references'].append(_create_reference(datam, parent=obj['uid']))
            break
        # Add classes & exceptions to module
        if _type in [CLASS, EXCEPTION] and \
                obj['type'] == MODULE and \
                obj[MODULE] == datam[MODULE]:
            obj['children'].append(datam['uid'])
            # obj['references'].append(_create_reference(datam, parent=obj['uid']))
            break

    if _type in [MODULE]:  # Make sure datam is a module.
        # Add this module(datam) to parent module node
        if datam[MODULE].count('.') >= 1:
            parent_module_name = '.'.join(datam[MODULE].split('.')[:-1])

            if parent_module_name not in app.env.docfx_yaml_modules:
                return

            insert_module = app.env.docfx_yaml_modules[parent_module_name]

            for obj in insert_module:
                if obj['type'] == MODULE and obj[MODULE] == parent_module_name:
                    obj['children'].append(datam['uid'])
                    # obj['references'].append(_create_reference(datam, parent=obj['uid']))
                    break

        # Add datam's children modules to it. Based on Python's passing by reference.
        # If passing by reference would be changed in python's future release.
        # Time complex: O(N^2)
        for module, module_contents in app.env.docfx_yaml_modules.items():
            if module != datam['uid'] and \
                    module[:module.rfind('.')] == datam['uid']:  # Current module is submodule/subpackage of datam
                for obj in module_contents:  # Traverse module's contents to find the module itself.
                    if obj['type'] == MODULE and obj['uid'] == module:
                        datam['children'].append(module)
                        # datam['references'].append(_create_reference(obj, parent=module))
                        break

def insert_children_on_package(app, _type, datam):
    """
    Insert children of a specific package
    """
    # Find the package which the datam belongs to
    if _type in [PACKAGE, MODULE]:  # Make sure datam is a package.
        # Add this package to parent package
        if datam['uid'].count('.') >= 1:
            parent_package_name = '.'.join(datam['uid'].split('.')[:-1])

            if parent_package_name not in app.env.docfx_yaml_packages:
                return

            insert_package = app.env.docfx_yaml_packages[parent_package_name]

            for obj in insert_package:
                if (obj['type'] == PACKAGE) and obj['uid'] == parent_package_name:
                    obj['children'].append(datam['uid'])
                    # obj['references'].append(_create_reference(datam, parent=obj['uid']))
                    break
        return
    if datam[MODULE] not in app.env.docfx_yaml_packages:
        return
    insert_package = app.env.docfx_yaml_packages[datam[MODULE]]
    
    for obj in insert_package:
        if obj['type'] == PACKAGE and obj['uid'] == datam[MODULE]:
            if _type in [CLASS, EXCEPTION]:               
                obj['children'].append(datam['uid'])
                break
            if _type in [FUNCTION, DATA]:
                obj['children'].append(datam['uid'])
                insert_package.append(datam)
                break

def insert_children_on_class(app, _type, datam):
    """
    Insert children of a specific class
    """
    if CLASS not in datam:
        return

    insert_class = app.env.docfx_yaml_classes[datam[CLASS]]
    # Find the class which the datam belongs to
    for obj in insert_class:
        if obj['type'] != CLASS:
            continue
        # Add methods & attributes to class
        if _type in [METHOD, ATTRIBUTE] and \
                obj[CLASS] == datam[CLASS]:
            obj['children'].append(datam['uid'])
            # obj['references'].append(_create_reference(datam, parent=obj['uid']))
            insert_class.append(datam)


def insert_children_on_function(app, _type, datam):
    """
    Insert children of a specific class
    """
    if FUNCTION not in datam:
        return

    insert_functions = app.env.docfx_yaml_functions[datam[FUNCTION]]
    insert_functions.append(datam)


def process_docstring(app, _type, name, obj, options, lines):
    """
    This function takes the docstring and indexes it into memory.
    """
    # Use exception as class
    py2docfx_logger = get_package_logger(__name__)

    def check_convert_package_type(obj, _type):
        if _type == MODULE:
            filename = getattr(obj, '__file__', None)
            if not filename:
                if getattr(obj, '__name__', None) == getattr(obj, '__package__', None):
                    return PACKAGE
            if filename.endswith(INITPY):
                return PACKAGE
        return _type

    if _type == EXCEPTION:
        _type = CLASS

    if _type == PROPERTY:
        _type = ATTRIBUTE

    _type = check_convert_package_type(obj, _type)
    cls, module = _get_cls_module(_type, name)

    if _type != PACKAGE and not module:
        py2docfx_logger.warning('Unknown Type: %s' % _type)
        return None

    if app.config.__contains__('autoclass_content') and app.config.autoclass_content.lower() == 'both':
        # When autoclass_content=both is set, process_docstring will be called twice
        # Once is for class docstring, the other is for class init method docstring
        # Use this check to avoid duplicate datamodel in docfx_yaml_classes
        # For class objects, process_docstring only cares its basic informaton
        # e.g. name, type, children.
        # Summaries and signatures are processed by translator.
        if _type == CLASS and cls in app.env.docfx_yaml_classes:
            return

    datam = _create_datam(app, cls, module, name, _type, obj, lines)

    if _type == PACKAGE:
        if name not in app.env.docfx_yaml_packages:
            app.env.docfx_yaml_packages[name] = [datam]
        else:
            app.env.docfx_yaml_packages[name].append(datam)

    if _type == MODULE:
        if module not in app.env.docfx_yaml_modules:
            app.env.docfx_yaml_modules[module] = [datam]
        else:
            app.env.docfx_yaml_modules[module].append(datam)

    if _type == CLASS:
        if cls not in app.env.docfx_yaml_classes:
            app.env.docfx_yaml_classes[cls] = [datam]
        else:
            app.env.docfx_yaml_classes[cls].append(datam)

    if _type == FUNCTION and app.config.autodoc_functions:
        if datam['uid'] is None:
            raise ValueError("Issue with {0} (name={1})".format(datam, name))
        if cls is None:
            cls = name
        if cls is None:
            raise ValueError(
                "cls is None for name='{1}' {0}".format(datam, name))
        if cls not in app.env.docfx_yaml_functions:
            app.env.docfx_yaml_functions[cls] = [datam]
        else:
            app.env.docfx_yaml_functions[cls].append(datam)

    if _type != MODULE:
        insert_inheritance(app, _type, obj, datam)
    insert_children_on_package(app, _type, datam)
    insert_children_on_module(app, _type, datam)
    insert_children_on_class(app, _type, datam)
    insert_children_on_function(app, _type, datam)

    app.env.docfx_info_uid_types[datam['uid']] = _type