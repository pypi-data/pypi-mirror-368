# -*- coding: utf-8 -*-
import os
import yaml as yml
from functools import partial
from common import remove_empty_values, parse_references, convert_member
from logger import get_package_logger

def convert_module(obj, uid_type_mapping):
    py2docfx_logger = get_package_logger(__name__)
    record = {}
    reference_mapping = {}
    old_object = {}

    for item in obj:
        record[item['uid']] = item
        if item['type'] == 'module':
            old_object = item

    convert_function_partial = partial(
        convert_member, reference_mapping=reference_mapping)
    convert_data_partial = partial(
        convert_member, reference_mapping=reference_mapping)

    new_object = {
        'uid': old_object.get('uid', None),
        'name': old_object.get('name', None),
        'fullName': old_object.get('fullName', None),
        'summary': old_object.get('summary', None),
        'remarks': old_object.get('remarks', None),
        'type': old_object.get('kind', None),
        'functions': None,
        'classes': None,
        'modules': None,
        'enums': None,
        'data': None,
    }

    children = old_object.get('children', [])
    children_objects = list(
        filter(lambda y: y is not None, map(lambda x: record.get(x), children)))
    functions = list(filter(lambda x: x.get('type')
                     == 'function', children_objects))
    new_object['functions'] = list(map(convert_function_partial, functions))

    datas = list(filter(lambda x: x.get('type')
                     == 'data', children_objects))
    new_object['data'] = list(map(convert_data_partial, datas))
    
    new_object['classes'] = list(
        filter(lambda x: uid_type_mapping.get(x, None) == 'class', children))

    new_object['modules'] = list(
        filter(lambda x: uid_type_mapping.get(x, None) == 'module', children))
    new_object['enums'] = list(
        filter(lambda x: uid_type_mapping.get(x, None) == 'enum', children))

    toreturn = remove_empty_values(new_object)
    msg = "module: " + toreturn['uid'] # CodeQL: [py/clear-text-logging-sensitive-data] There is no sensitive data in the print statement.
    py2docfx_logger.info(msg)
    return toreturn
