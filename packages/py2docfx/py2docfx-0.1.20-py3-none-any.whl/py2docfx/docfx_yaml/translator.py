# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re
import parameter_utils
import return_type_utils

from docutils import nodes
from sphinx import addnodes
from sphinx.addnodes import desc_signature,desc_content
from sphinx.util.docfields import _is_single_paragraph
from collections import OrderedDict
from nodes import remarks
from logger import get_package_logger

TYPE_SEP_PATTERN = '(\[|\]|, |\(|\))'
PARAMETER_NAME = "[*][*](.*?)[*][*]"
PARAMETER_TYPE = "[(]((?:.|\n)*)[)]"
CLASS_TYPE = 'class'
EXCEPTION_TYPE = 'exception'
ATTRIBUTE_TYPE = 'attribute'

types_contain_constructor = {CLASS_TYPE, EXCEPTION_TYPE}
types_contain_attributes = {CLASS_TYPE, EXCEPTION_TYPE}

def translator(app, docname, doctree):

    py2docfx_logger = get_package_logger(__name__)
    transform_node = app.docfx_transform_node

    class_obj_cache = app.env.domains['py'].objects

    def _remove_exception_xref_tag(exception_type):
        exception_type = exception_type.replace('<xref:', '')
        exception_type = exception_type.replace('>', '')
        exception_type = exception_type.replace('*', '')
        return exception_type

    def transform_para(para_field):
        if isinstance(para_field, nodes.paragraph):
            return transform_node(para_field)
        else:
            return para_field.astext()

    def type_mapping(type_name):
        mapping = {
            "staticmethod": "method",
            "classmethod": "method",
            "exception": "class",
        }

        return mapping[type_name] if type_name in mapping else type_name

    def _get_uid_and_type_from_desc(node):
        assert node.tagname == 'desc'
        if node.attributes['domain'] != 'py':
            msg = str('Skipping Domain Object (%s)' % node.attributes['domain'])
            py2docfx_logger.info(msg)
            return None, None

        try:
            module = node[0].attributes['module']
            full_name = node[0].attributes['fullname']
        except KeyError as e:
            py2docfx_logger.error("There maybe some syntax error in docstring near: " + node.astext())
            raise e

        uid = '{module}.{full_name}'.format(module=module, full_name=full_name)
        type = node.get('desctype')
        return (uid, module, type)

    def _is_desc_of_enum_class(content_child):
        assert content_child.tagname == 'desc_content'
        if content_child.children and content_child[0] and content_child[0].tagname == 'paragraph' and content_child[0].astext() == 'Bases: enum.Enum':
            return True

        return False
    
    def extract_exception_desc(exception_fieldbody_node):
        def extract_exception_type(exception_node):
            _type_without_xref = transform_node(exception_node).strip(" \n\r\t")
            _type_without_xref = _type_without_xref.replace('<xref:', '')
            _type_without_xref = _type_without_xref.replace('>', '')
            _type_without_xref, _added_reference = parameter_utils.resolve_type(_type_without_xref)
            if _added_reference:
                exception_type = parameter_utils.resolve_xref_type(_added_reference)
            else:
                exception_type = _type_without_xref
            return exception_type
            
        extractedExceptions = []
        for pararaph_node in exception_fieldbody_node.traverse(nodes.paragraph):
            for exception_node in pararaph_node:
                if (exception_node.tagname == 'reference'):
                    exception_type = extract_exception_type(exception_node)
                    extractedExceptions.append({'type': exception_type})
                elif (isinstance(exception_node, nodes.TextElement) or isinstance(exception_node, nodes.Text)):
                    # If current subnode isn't reference, extract its text if possible
                    if (len(extractedExceptions)!=0):
                        description = transform_node(exception_node).strip(" \n\r\t")
                        if ('description' in extractedExceptions[-1]):
                            if (re.match(r'[\*`a-zA-z0-9]+', description)): # Should support * and ` for markdown code and italic
                                if (extractedExceptions[-1]['description'].endswith(' ')):
                                    extractedExceptions[-1]['description'] += description
                                else:
                                    # Ensure there's a space when concat text from 2 nodes
                                    extractedExceptions[-1]['description'] += (' ' + description)
                        else:
                            if (re.match(r'[a-zA-z0-9]+', description)):
                                extractedExceptions[-1]['description'] = description
            if not extractedExceptions:
                exception_type = extract_exception_type(exception_node)
                if exception_type:
                    extractedExceptions.append({'type': exception_type})
        for exception in extractedExceptions:
            if 'description' in exception:
                exception['description'] = exception['description'].strip(" ")
        return extractedExceptions

    def _get_full_data(node, module_name):
        data = {
            'parameters': [],
            'keywordOnlyParameters': [],
            'variables': [],
            'exceptions': [],
            'return': {},
            'references': [],
        }

        for field in node:
            fieldname, fieldbody = field
            try:
                # split into field type and argument
                fieldtype, _ = fieldname.astext().split(None, 1)
            except ValueError:
                # maybe an argument-less field type?
                fieldtype = fieldname.astext()

            # collect the content, trying not to keep unnecessary paragraphs
            if _is_single_paragraph(fieldbody):
                content = fieldbody
            else:
                content = fieldbody.children

            if fieldtype == 'Raises':
                if data['exceptions']:
                    data['exceptions'].extend(extract_exception_desc(fieldbody))
                else:    
                    data['exceptions'] = extract_exception_desc(fieldbody)   

            if fieldtype == 'Returns':
                returnvalue_ret = transform_node(content[0])
                if returnvalue_ret:
                    data['return']['description'] = returnvalue_ret.strip(" \n\r\t")

            if fieldtype in ['Return']:
                for returntype_node in content:
                    returntype = return_type_utils.get_return_type(class_obj_cache, returntype_node, module_name)
                    for item in returntype:
                        data['return'].setdefault('type', []).append(item)

            if fieldtype in ['Parameters', 'Variables', 'Keyword']:
                if _is_single_paragraph(fieldbody):
                    #_data = parse_parameter(ret_data, fieldtype)
                    _data = parameter_utils.parse_parameter(content[0], fieldtype, app)
                    if fieldtype == 'Parameters':
                        data['parameters'].append(_data)
                    elif fieldtype == 'Keyword':
                        data['keywordOnlyParameters'].append(_data)
                    else:
                        _data['id'] = _parse_variable_id(content[0].astext())
                        data['variables'].append(_data)
                else:
                    for child in content[0]:
                        _data = parameter_utils.parse_parameter(child[0], fieldtype, app)
                        if fieldtype in ['Parameters']:
                            data['parameters'].append(_data)
                        elif fieldtype == 'Keyword':
                            data['keywordOnlyParameters'].append(_data)
                        else:
                            _data['id'] = _parse_variable_id(child.astext())
                            data['variables'].append(_data)

        return data

    def _parse_variable_id(variable_content):
        if variable_content.find('–') >= 0:
            id_part = variable_content[:variable_content.find('–') - 1]
        else:
            id_part = variable_content
        if id_part.find('(') >= 0:
            variable_id = id_part[:id_part.find('(')].strip(' ')
        else:
            variable_id = id_part.strip(' ')
        return variable_id

    def _is_property_node(signature_child):
        assert signature_child.tagname == 'desc_signature'
        first_child = signature_child.children[0]
        if isinstance(first_child, addnodes.desc_annotation):
            if (first_child.astext().strip(" ") == 'property'):
                return True
        return False

    # TODO: Should use a class like attribute_helper to classify below attribute-only methods
    def extract_sig_child_from_attribute_desc_node(node):
        assert node.tagname == 'desc'
        signature_child = node.children[0]
        if (not isinstance(signature_child, desc_signature)):
            raise Exception('First child of attribute node isn\'t signature, node: {0}'.format(node.astext()))
        return signature_child

    def extract_content_child_from_attribute_desc_node(node):
        assert node.tagname == 'desc'
        content_child = node.children[1]
        if (not isinstance(content_child, desc_content)):
            raise Exception('First child of attribute node isn\'t content, node: {0}'.format(node.astext()))
        return content_child

    def extract_attribute(node, class_nodes, module_name):
        def find_ancestor_class_content_node(node_class, node_module, node_ids, class_nodes):
            for class_node in class_nodes:
                if isinstance(class_node.children[0], desc_signature):
                    signature_child = class_node.children[0]
                    if node_class == signature_child['fullname'] and node_module == signature_child['module']:
                        for child_node in class_node.children[1:]:
                            if (isinstance(child_node, desc_content)):
                                return child_node
                        raise Exception('Can\'t find the content node: {0}'.format(class_node.astext().replace("\\r\\n", "")))
                else:
                    raise Exception('First child of class node isn\'t signature, node: {0}'.format(class_node.astext()))
            raise Exception('Can\'t find ancestor class node for attribute, node id is: {0}'.format(node_ids[0]))

        assert node.tagname == 'desc'
        attribute_map = {}
        signature_child = extract_sig_child_from_attribute_desc_node(node)
        content_child = extract_content_child_from_attribute_desc_node(node)
        curuid = signature_child.get('module', '') + '.' + signature_child.get('fullname', '')
        addedData = {}                
        name = signature_child.children[0].astext()
        if isinstance(signature_child, desc_signature) and any(isinstance(n, addnodes.desc_annotation) for n in signature_child):                
            signature_child_ids = signature_child.get('ids', [''])                
            
            if len(curuid) > 0:
                parent = curuid[:curuid.rfind('.')]
                
                if curuid in attribute_map:
                    # ensure the order of docstring attributes and real attributes is fixed
                    if len(signature_child_ids) == 0:
                        attribute_map[curuid]['syntax']['content'] += (
                            ' ' + signature_child.astext())
                        # concat the description of duplicated nodes
                    else:
                        attribute_map[curuid]['syntax']['content'] = signature_child.astext() 
                        + ' ' + attribute_map[curuid]['syntax']['content']
                else:
                    ancestor_class_content_node = find_ancestor_class_content_node(signature_child['class'], signature_child['module'], signature_child['ids'], class_nodes)
                    if _is_desc_of_enum_class(ancestor_class_content_node):
                        addedData = {
                            'uid': curuid,
                            'id': name,
                            'parent': parent,
                            'langs': ['python'],
                            'name': name,
                            'fullName': curuid,
                            'type': node.get('desctype'),
                            'module': signature_child.get('module'),
                            'syntax': {
                                'content': signature_child.astext(),
                                'return': {
                                    'type': [parent]
                                }
                            }
                        }
                    else:
                        addedData = {
                            'uid': curuid,
                            'class': parent,
                            'langs': ['python'],
                            'name': name,
                            'fullName': curuid,
                            'type': ATTRIBUTE_TYPE,
                            'module': signature_child.get('module'),
                            'syntax': {
                                'content': signature_child.astext()
                            }
                        }
            else:
                raise Exception('ids of node: ' + repr(signature_child) + ' is missing.')
                 # no ids and no duplicate or uid can not be generated.

        # Currently only utilize summary to avoid code repetition, 
        # if we need to change other attribute generator logic, 
        # better to get from extracted_content_data below too
        
        extracted_content_data = extract_content(content_child, ATTRIBUTE_TYPE, module_name)
        if not addedData:
            # If current attribute doesn't have correct signature child, fill in basic information
            # TODO: append fullName here, currently when fallback to here, 
            # information like fullname, name of attribute comes from process_docstring
            addedData = {
                'uid': curuid,
                'type': ATTRIBUTE_TYPE,
                'name': name,
                'fullName': curuid,
            }
        if 'summary' in extracted_content_data:
            addedData['summary'] = extracted_content_data['summary']
        if 'remarks' in extracted_content_data:
            addedData['remarks'] = extracted_content_data['remarks']
        if 'seealso' in extracted_content_data:
            addedData['seealso'] = extracted_content_data['seealso']
        if 'example' in extracted_content_data:
            addedData['example'] = extracted_content_data['example']

        attribute_map[curuid] = addedData
        return addedData

    def extract_signature(node):
        def parameter_list_astext(node):
            # Sphinx 3.5.4 has issue to parse default value containing comma in signature
            # e.g. delimiter=',' => parameter "delimiter='" and parameter "'"
            # Use a custom astext to workaround (mainly copy logic from addnodes)
            parameter_list_text = '('
            child_text_separator = ', '
            first_paramter = True
            for parameter_node in node.children:
                if first_paramter:
                    parameter_list_text += parameter_node.astext()
                    first_paramter = False
                else:
                    paramter_text = parameter_node.astext()
                    if (paramter_text == "'"):
                        parameter_list_text += ',' + paramter_text
                    else:
                        parameter_list_text += child_text_separator + paramter_text
            parameter_list_text += ')'
            return parameter_list_text

        assert node.tagname == 'desc_signature'
        annotation_to_skip = ['class','classmethod', 'exception']
        signature = ''
        if node.children:
            first_child = node.children[0]
            included_child_start = 0
            isClass = False
            if isinstance(first_child, addnodes.desc_annotation):
                if (first_child.astext().strip(" \n\r\t") == 'property'):
                    return None # Don't generate signature for property
                elif (first_child.astext().strip(" \n\r\t") in annotation_to_skip):
                    # Don't include 'class' declaration for constructors, 
                    # don't include 'classmethod' front of signature (To keep behavior consistent)
                    included_child_start = 1 
                    isClass = True
            for included_child in node.children[included_child_start:]:
                # Skip class name when write signature (To keep same behavior as before signature async support)
                if (not isinstance(included_child, addnodes.desc_addname)):
                    if (isinstance(included_child, addnodes.desc_parameterlist)):
                        signature += parameter_list_astext(included_child)
                    else:
                        signature += included_child.astext()
                # Append parentheses after constructor if constructor hasn't parameter (To keep consistent behavior)
            if (isClass and ('(' not in signature) and (')' not in signature)):
                signature += '()'
        return signature

    def extract_content(node, api_type, module_name):
        def merge_field_list_data(api_type, current_data, field_list_data):
            # If node is a class node and autoclass=both, class docstring params are first, __init__ docstring params come second.
            # If class hasn't init, the second param list will come from inherit base class
            # don't simply merge parameters when it's classif api_type == CLASS_TYPE:
            if api_type in types_contain_constructor:
                if 'parameters' in current_data and 'parameters' in field_list_data:
                    current_data['parameters'].extend(field_list_data['parameters'])
                    field_list_data.pop('parameters')
                if 'keywordOnlyParameters' in current_data and 'keywordOnlyParameters' in field_list_data:
                    current_data['keywordOnlyParameters'].extend(field_list_data['keywordOnlyParameters'])
                    field_list_data.pop('keywordOnlyParameters')
                if 'variables' in current_data and 'variables' in field_list_data:
                    current_data['variables'].extend(field_list_data['variables'])
                    field_list_data.pop('variables')
            current_data.update(field_list_data)

        assert node.tagname == 'desc_content'
        summary = []
        data = {}
        for child in node:
            if isinstance(child, remarks):
                remarks_string = transform_node(child)
                data['remarks'] = remarks_string
            elif isinstance(child, nodes.field_list):
                merge_field_list_data(api_type, data, _get_full_data(child, module_name))
            elif isinstance(child, addnodes.seealso):
                data['seealso'] = transform_node(child)
            elif isinstance(child, nodes.admonition) and 'Example' in child[0].astext():
                # Remove the admonition node
                # TODO: we can replace way with preciser visit to avoid deepcopy
                child_copy = child.deepcopy()
                child_copy.pop(0)
                data['example'] = transform_node(child_copy)
            elif isinstance(child, nodes.target) and len(child.astext()) == 0:
                # Skip target nodes because they shouldn't be transformed to a links as part of summary
                pass
            elif isinstance(child, addnodes.desc):
                # Skip desc nodes because they represents child api, and will be visited in the main loop
                pass
            elif isinstance(child, nodes.literal_block):
                content = transform_node(child).strip(" \n\r\t")
                summary.append(content)
            else:
                content = transform_node(child).strip("\n\r\t") # Don't strip space because lists like bullet_list need space to work
                if not content.startswith('Bases: '):
                    # Because summary can contain code examples,
                    # need to allow summary line to contain punctuation ony
                    if len(content) > 0:
                        summary.append(content) 
        
        if "desctype" in node.parent and node.parent["desctype"] == CLASS_TYPE:
            # Make sure class doesn't have 'exceptions' field.
            data.pop('exceptions', '')

        if summary:
            data['summary'] = '\n\n'.join(summary)
        
        return data


    def extract_class_nodes_from_doctree(doctree):
        class_nodes = []
        for desc_node in doctree.traverse(addnodes.desc):
            if (desc_node['desctype'] in types_contain_attributes):
                class_nodes.append(desc_node)
        return class_nodes
    
    class_nodes = extract_class_nodes_from_doctree(doctree)
    class_added_attributes = {}
    class_data = {}
    for node in doctree.traverse(addnodes.desc):   
        (uid, module_name, node_type) = _get_uid_and_type_from_desc(node)
        data = {}
        signature_child = node.children[node.first_child_matching_class(addnodes.desc_signature)]
        content_child = node.children[node.first_child_matching_class(addnodes.desc_content)]
        if node_type == ATTRIBUTE_TYPE:
            attribute_sig_child = extract_sig_child_from_attribute_desc_node(node)

            if content_child.astext().startswith('alias of'):
                # Ignore alias attribute
                # e.g. azure.cognitiveservices.speech.intent.IntentRecognizer.IntentsIte (alias of Iterable[Tuple[Union[str, azure.cognitiveservices.speech.intent.LanguageUnderstandingModel], str]]) 
                continue

            if attribute_sig_child['class']: 
                attribute_class = attribute_sig_child['module'] + '.' + attribute_sig_child['class']
                class_added_attributes.setdefault(attribute_class, OrderedDict())
                # TODO: Merge attribute_data if same uid
                attribute_data = extract_attribute(node, class_nodes, module_name)

                #Check if attribute information is already added
                if attribute_data['uid'] in class_added_attributes[attribute_class].keys():
                    existed_data = class_added_attributes[attribute_class][attribute_data['uid']]
                    #Merge existed_data with new attribute_data
                    for key in attribute_data.keys():
                        if key not in existed_data.keys():
                            existed_data[key] = attribute_data[key]
                    class_added_attributes[attribute_class][attribute_data['uid']] = existed_data
                else:
                    class_added_attributes[attribute_class][attribute_data['uid']] = attribute_data
            else:
                raise Exception('Attribute doesn\'t have class information. Attribute_name: {0}'.format(attribute_sig_child['fullname']))
            continue
        
        data.update(extract_content(content_child, node_type, module_name))
        data['content'] = extract_signature(signature_child)

        data['type'] = type_mapping(node_type) if node_type else 'unknown'
        if _is_property_node(signature_child):
            data['type'] = ATTRIBUTE_TYPE
        
        # Don't include empty data
        for key, val in data.copy().items():
            if not val:
                del data[key]
        
        if uid in app.env.docfx_info_field_data:
            # Sphinx autodoc already provides method signature, skip declaration in RST comments (py:class/py:method)
            sig_id = signature_child.get('ids', [''])[0].lower()
            fullname = signature_child.get('fullname', '').lower()
            if not sig_id.endswith(fullname):
                continue

        # Write into collection in environment variable
        if (uid in app.env.docfx_info_uid_types):
            app.env.docfx_info_field_data[uid] = data

        if node_type in types_contain_attributes:
            api_full_name = signature_child['module'] + '.' + signature_child['fullname']
            class_data[api_full_name] = data

    # Append added_attribute to class
    for class_name, added_attributes in class_added_attributes.items():
        if not added_attributes:
            # `class_added_attributes` Maybe be in default value []
            # Indicates that all doctree attribute desc nodes under this class 
            # are skipped attributes/properties (like alias)
            continue

        if class_name in class_data:
            class_data[class_name].setdefault('added_attribute', [])
            class_data[class_name]['added_attribute'].extend(added_attributes.values())
        else:
            raise Exception('Can\'t find generated class data for attribute. class_name: {0}, attribute_name: {1}'.format(class_name, added_attributes))
