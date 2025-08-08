# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from copy import deepcopy
import os
import re

import yaml as yml
from sphinx.util import ensuredir
from yaml import safe_dump as dump
from settings import API_ROOT

import common
from convert_class import convert_class
from convert_enum import convert_enum
from convert_module import convert_module
from convert_package import convert_package
from logger import get_package_logger

INITPY = '__init__.py'
MODULE = 'module'
scientific_notation_regex = re.compile(r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)$')

def string_representer(dumper, data):
    return dumper.represent_scalar(u"tag:yaml.org,2002:str", data,
                                    style="'" if (scientific_notation_regex.match(data)) else None)
yml.add_representer(str, string_representer)

def insert_node_to_toc_tree_return_is_root_package(toc_yaml, uid, project_name, toc_node_map):
    def generate_toc_node(name, uid):
        """
        Generate a TOC node with the given name and uid.
        """
        return {
            'name': name,
            'uid': uid,
            'no-loc': [name],
        }

    # Build nested TOC
    parent_level = uid
    cur_node = None
    is_root = False
    # Try all ancestors azure.core.class1 -> azure.core -> azure
    while parent_level.count('.') >= 1:
        parent_level = '.'.join(parent_level.split('.')[:-1])
        found_node = toc_node_map[parent_level] if parent_level in toc_node_map else None
        if found_node:
            # If ancestor already in current TOC, insert to its items
            name = uid.split('.')[-1] if '.' in uid and project_name != uid else uid
            cur_node = generate_toc_node(name, uid)
            if 'uid' in found_node:
                # Only leaf nodes should have uid
                found_node.pop('uid', 'No uid found')
            # Subpackages should have its Overview page
            found_node.setdefault('items', [{'name': 'Overview', 'uid': parent_level}]).append(cur_node)
            break
    
    # uid is representing a package in TOC as root node
    if cur_node is None:
        # if uid doesn't contain '.', the name doesn't need to be simplified
        cur_node = generate_toc_node(uid, uid)
        toc_yaml.append(cur_node)
        is_root = True

    # insert to uid-toc map
    toc_node_map[uid] = cur_node
    return is_root

def merge_params(arg_params, doc_params):
    merged_params = deepcopy(doc_params)
    # merge arg_params into merged_params
    for arg_param in arg_params:
        for merged_param in merged_params:
            if arg_param['id'] == merged_param['id']:
                if "defaultValue" in arg_param.keys():
                    merged_param["defaultValue"] = arg_param["defaultValue"]
                if "type" in arg_param.keys():
                    merged_param["type"] = arg_param["type"]
                if "isRequired" in arg_param.keys():
                    if  arg_param["isRequired"] == False:
                        merged_param["isRequired"] = arg_param["isRequired"]
                break
        else:
            merged_params.append(arg_param)
    return merged_params

def remove_params_without_id(params):
    new_params = []
    for param in params:
        if 'id' in param:
            new_params.append(param)
    return new_params

def add_isrequired_if_needed(obj, key: str):
    if key in obj['syntax'] and obj['type'] in ['class', 'function', 'method']:
        for args in obj['syntax'][key]:
            if 'isRequired' not in args and 'defaultValue' not in args:
                args['isRequired'] = True

def get_merged_params(obj, info_field_data, key: str):
    py2docfx_logger = get_package_logger(__name__)
    merged_params = []
    arg_params = obj.get('syntax', {}).get(key, [])
    if key in info_field_data[obj['uid']]:
        doc_params = info_field_data[obj['uid']].get(
            key, [])
        if arg_params and doc_params:
            if len(arg_params) - len(doc_params) > 0:
                msg = f'Documented params don\'t match size of params:{obj["uid"]}' # CodeQL: [py/clear-text-logging-sensitive-data] There is no sensitive data in the print statement.
                py2docfx_logger.warning(msg)
            doc_params = remove_params_without_id(doc_params)
            merged_params = merge_params(arg_params, doc_params)
    else:
        merged_params = arg_params

    return merged_params

def raise_up_fields(obj):
    # Raise up summary
    if 'summary' in obj['syntax'] and obj['syntax']['summary']:
        obj['summary'] = obj['syntax'].pop(
            'summary').strip(" \n\r\r")
    
    # Raise up remarks
    if 'remarks' in obj['syntax'] and obj['syntax']['remarks']:
        obj['remarks'] = obj['syntax'].pop('remarks')

    # Raise up seealso
    if 'seealso' in obj['syntax'] and obj['syntax']['seealso']:
        obj['seealsoContent'] = obj['syntax'].pop('seealso')

    # Raise up example
    if 'example' in obj['syntax'] and obj['syntax']['example']:
        obj.setdefault('example', []).append(
            obj['syntax'].pop('example'))

    # Raise up exceptions
    if 'exceptions' in obj['syntax'] and obj['syntax']['exceptions']:
        obj['exceptions'] = obj['syntax'].pop('exceptions')

    # Raise up references
    if 'references' in obj['syntax'] and obj['syntax']['references']:
        obj.setdefault('references', []).extend(
            obj['syntax'].pop('references'))

def merge_data(obj, info_field_data, yaml_data):
    # Avoid entities with same uid and diff type.
    # Delete `type` temporarily
    del(info_field_data[obj['uid']]['type'])
    if 'syntax' not in obj:
        obj['syntax'] = {}
    merged_params = get_merged_params(obj, info_field_data, 'parameters')
    merged_kwargs = get_merged_params(obj, info_field_data, 'keywordOnlyParameters')

    obj['syntax'].update(info_field_data[obj['uid']])

    # Merging parameters and keywordOnlyParameters is required,
    # becasue parameters and keywordOnlyParameters can be in both signature and docstring
    # For positionalOnlyParameters, it's not required, because it's only in signature so far
    if merged_params:
        obj['syntax']['parameters'] = merged_params
    if merged_kwargs:
        obj['syntax']['keywordOnlyParameters'] = merged_kwargs

    add_isrequired_if_needed(obj, 'parameters')
    add_isrequired_if_needed(obj, 'keywordOnlyParameters')
    add_isrequired_if_needed(obj, 'positionalOnlyParameters')

    raise_up_fields(obj)

    # add content of temp list 'added_attribute' to children and yaml_data
    if 'added_attribute' in obj['syntax'] and obj['syntax']['added_attribute']:
        added_attribute = obj['syntax'].pop('added_attribute')
        # TODO: yaml_data is updated wihle iterated. 
        # `added_attribute` items are copied from class api's `obj` to `yaml_data`
        # Then iterate again
        # Should iterate uid and merge yaml_data, added_attribute
        for attrData in added_attribute:
            existed_Data = next(
                (n for n in yaml_data if n['uid'] == attrData['uid']), None)
            if existed_Data:
                # Update data for already existed one which has attribute comment in source file
                existed_Data.update(attrData)
            else:
                obj.get('children', []).append(attrData['uid'])
                yaml_data.append(attrData)
    # Revert `type` for other objects to use
    info_field_data[obj['uid']]['type'] = obj['type']

def build_finished(app, exception):
    """
    Output YAML on the file system.
    """
    
    py2docfx_logger = get_package_logger(__name__)

    def convert_class_to_enum_if_needed(obj):
        if (obj.get('inheritance'), None):
            children = obj.get('inheritance', None)
            inheritanceLines = []
            for child in children:
                iLine = []
                if child.get('inheritance', None) and child['inheritance'][0].get('type', None):
                    iLine.append(child['inheritance'][0]['type'])
                if child.get('type', None):
                    iLine.append(child['type'])
                inheritanceLines.append(iLine)
            if inheritanceLines:
                for iLine in inheritanceLines:
                    for inheritance in iLine:
                        if inheritance.find('enum.Enum') > -1:
                            obj['type'] = 'enum'
                            app.env.docfx_info_uid_types[obj['uid']] = 'enum'
                            return

    normalized_outdir = os.path.normpath(os.path.join(
        app.builder.outdir,  # Output Directory for Builder
        API_ROOT
    ))

    ensuredir(normalized_outdir)
    project_name = app.config.project.replace('-','.')
    toc_node_map = {}

    def filter_out_self_from_args(obj):
        arg_params = obj.get('syntax', {}).get('parameters', [])
        if(len(arg_params) > 0 and 'id' in arg_params[0]):
            if (arg_params[0]['id'] == 'self') or (obj['type'] in ['class', 'method'] and arg_params[0]['id'] == 'cls'):
                # Support having `self` as an arg param, but not documented
                # Not document 'cls' of constuctors and class methods too
                arg_params = arg_params[1:]
                obj['syntax']['parameters'] = arg_params
        return obj

    toc_yaml = []
    # Used to record filenames dumped to avoid confliction
    # caused by Windows case insensitive file system
    file_name_set = set()

    # Order matters here, we need modules before lower level classes,
    # so that we can make sure to inject the TOC properly
    # put app.env.docfx_yaml_packages after app.env.docfx_yaml_modules to keep same TOC items order
    for data_set in (app.env.docfx_yaml_packages,
                     app.env.docfx_yaml_modules,
                     app.env.docfx_yaml_classes,
                     app.env.docfx_yaml_functions):  # noqa

        for uid, yaml_data in iter(sorted(data_set.items())):
            if not uid:
                # Skip objects without a module
                continue

            references = []
            # Merge module data with class data
            package_obj = None
            for obj in yaml_data:
                obj = filter_out_self_from_args(obj)

                if obj['uid'] in app.env.docfx_info_field_data and \
                        obj['type'] == app.env.docfx_info_field_data[obj['uid']]['type']:
                    merge_data(obj, app.env.docfx_info_field_data, yaml_data)

                if 'references' in obj:
                    # Ensure that references have no duplicate ref
                    ref_uids = [r['uid'] for r in references]
                    for ref_obj in obj['references']:
                        if ref_obj['uid'] not in ref_uids:
                            references.append(ref_obj)
                    obj.pop('references')

                # To distinguish distribution package and import package
                if obj.get('type', '') == 'package' and obj.get('kind', '') != 'distribution':
                    obj['kind'] = 'import'
                    package_obj = obj

                if (obj['type'] == 'class' and obj['inheritance']):
                    convert_class_to_enum_if_needed(obj)

            is_root = insert_node_to_toc_tree_return_is_root_package(toc_yaml, uid, project_name, toc_node_map)
            if is_root and package_obj is not None:
                package_obj['kind'] = 'rootImport' # API Browser only list root packages for ApiList feature

    for data_set in (app.env.docfx_yaml_packages,
                     app.env.docfx_yaml_modules,
                     app.env.docfx_yaml_classes,
                     app.env.docfx_yaml_functions):  # noqa
        for uid, yaml_data in iter(sorted(data_set.items())):
            # Output file
            if uid.lower() in file_name_set:
                filename = uid + "(%s)" % app.env.docfx_info_uid_types[uid]
            else:
                filename = uid
            out_file = os.path.join(normalized_outdir, '%s.yml' % filename)
            ensuredir(os.path.dirname(out_file))

            transformed_obj = None
            if yaml_data[0]['type'] == 'package':
                transformed_obj = convert_package(
                    yaml_data, app.env.docfx_info_uid_types)
                mime = "PythonPackage"
            elif yaml_data[0].get('type', None) == 'class':
                transformed_obj = convert_class(yaml_data)
                mime = "PythonClass"
            elif yaml_data[0].get('type', None) == 'enum':
                transformed_obj = convert_enum(yaml_data)
                mime = "PythonEnum"
            else:
                transformed_obj = convert_module(
                    yaml_data, app.env.docfx_info_uid_types)
                mime = "PythonModule"

            if transformed_obj == None:
                msg = f"Unknown yml, uid is: {uid}"
                py2docfx_logger.warning(msg)
            else:
                # save file
                common.write_yaml(transformed_obj, out_file, mime)
                file_name_set.add(filename)

    # Write TOC, the toc should include at least 1 
    if len(toc_yaml) == 0:
        msg = "No documentation for this module."
        py2docfx_logger.error(msg)
        raise RuntimeError(msg)

    toc_file = os.path.join(normalized_outdir, 'toc.yml')
    with open(toc_file, 'w') as writable:
        writable.write(
            dump(
                toc_yaml,
                default_flow_style=False,
            )
        )
