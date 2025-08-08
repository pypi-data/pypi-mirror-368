import re
import builtins
import typing

from inspect import isclass

TYPE_SEP_PATTERN = '(\[|\]|, |\(|\))'
PARAMETER_NAME = "[*][*](.*?)[*][*]"
PARAMETER_TYPE = "[(]((?:.|\n)*)[)]"
SYSTEM_TYPE = "system type"
TYPING_TYPE = "typing type"

def get_builtin_type_dict():
    system_type_list = []
    # loop through the attributes of the builtins module to get builtin types list
    for attr in dir(builtins):
        value = getattr(builtins, attr)
        if isinstance(value, type):
            system_type_list.append(value.__name__)

    # get typing types list
    typing_type_list = typing.__all__

    type_dict = {}
    for item in system_type_list:
        type_dict[item] = SYSTEM_TYPE
    for item in typing_type_list:
        type_dict[item] = TYPING_TYPE

    return type_dict

builtin_type_dict = get_builtin_type_dict()

def make_param(_id, _description, _type=None, _default_value=None, _required=None):
    ret = {}
    if _id:
        ret['id'] = _id.strip(" \n\r\r")
    if _description:
        ret['description'] = _description.strip(" \n\r\r")
    if _type:
        ret['type'] = _type
    if _default_value:
        ret['defaultValue'] = _default_value
        
    if _required is not None:
        if _default_value is not None:
            ret['isRequired'] = False
        else:
            ret['isRequired'] = _required

    return ret

def resolve_type(data_type):
    # Remove @ ~ and \n for cross reference in parameter/return value type to apply to docfx correctly
    data_type = re.sub('[@~\n]', '', data_type)

    # Add references for docfx to resolve ref if type contains TYPE_SEP_PATTERN
    _spec_list = []
    _spec_fullnames = re.split(TYPE_SEP_PATTERN, data_type)

    _added_reference = {}
    if len(_spec_fullnames) > 1:
        _added_reference_name = ''
        for _spec_fullname in _spec_fullnames:
            if _spec_fullname != '':
                _spec = {}
                _spec['name'] = _spec_fullname.split('.')[-1]
                _spec['fullName'] = _spec_fullname
                if re.match(TYPE_SEP_PATTERN, _spec_fullname) is None:
                    _spec['uid'] = _spec_fullname
                _spec_list.append(_spec)
                _added_reference_name += _spec['name']

        _added_reference = {
            'uid': data_type,
            'name': _added_reference_name,
            'fullName': data_type,
            'spec.python': _spec_list
        }

    return data_type, _added_reference

def resolve_xref_type(reference):
    ''' Convert an aggregated type into markdown string with xref tag.
        e.g. input: 'list[azure.core.Model]' -> output: '<xref:list>[<xref:azure.core.Model>]'
    '''
    xref = ''
    http_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    if reference.get('spec.python', None):
        specList = reference['spec.python']
        filterList = list(filter(lambda x: x.get('uid', None), specList))
        d = {}
        for i, item in enumerate(filterList):
            if re.match(http_pattern, item.get('uid')):
                d[item.get('uid')] = True
                d[filterList[i-1].get('uid')] = True
            else:
                d[item.get('uid')] = False

        for i, item in enumerate(specList):
            if item.get('uid', None) and d[item.get('uid')]:
                xref += item["uid"]
            elif item.get('uid', None):
                xref += f'<xref:{item["uid"]}>'
            else:
                xref += item['name']
    else:
        xref += f'<xref:{reference["uid"]}>'

    return xref

def check_shorten_type_name(type_name: str) -> bool:
    type_name_elements = type_name.split('.')
    if len(type_name_elements) == 1:
        return True
    else:
        return False

def check_is_complex_type(type_name: str) -> bool:
    # check if the type_name contains any of the complex type characters
    complex_type_chars = ['[', ']', '(', ')', ',']
    for char in complex_type_chars:
        if char in type_name:
            return True
    return False

def is_typing(node_text: str, node) -> bool:
    is_in_typing_module_list = False
    is_shorten_type_name = False
    has_typing_in_node_attributes = False
    
    # check if the node_text is in typing module list
    check_str = node_text.split('.', 1)[-1]
    is_in_typing_module_list = check_str in typing.__all__

    # check if the node_text is a simple type name or has form of 'typing.TypeName'
    typing_prefix = 'typing.'
    check_typing_str = typing_prefix + node_text.strip()

    def check_shorten_name_and_typing_str(node, attr_str):
        is_shorten_type_name = check_shorten_type_name(node[attr_str])
        temp_str = node[attr_str]
        has_typing_in_node_attributes = check_typing_str == temp_str.strip()
        return is_shorten_type_name, has_typing_in_node_attributes

    if 'refid' in node.attributes:
        is_shorten_type_name, has_typing_in_node_attributes = check_shorten_name_and_typing_str(node, 'refid')
    elif 'refuri' in node.attributes:
        is_shorten_type_name, has_typing_in_node_attributes = check_shorten_name_and_typing_str(node, 'refuri')
    elif 'reftarget' in node.attributes:
        is_shorten_type_name, has_typing_in_node_attributes = check_shorten_name_and_typing_str(node, 'reftarget')
    else:
        has_typing_in_node_attributes = False

    # 1. The type has to be in typing module list to be a typing type.
    # 2. The node['refid'] or node['refuri'] is an abbreviated type name or has typing prefix in its attributes, it is a typing type
    if is_in_typing_module_list and (is_shorten_type_name or has_typing_in_node_attributes):
        return True
    else:
        return False

def is_system_type(name: str) -> bool:
    return isclass(getattr(builtins, name, None))

def is_complex_type(node_text: str) -> bool:
    complex_type_chars = ['[', ']', '(', ')']
    for char in complex_type_chars:
        if char in node_text:
            return True
    return False

def process_complex_type(type_string: str) -> str:
    # replace "or" with ","
    type_string = type_string.replace(" or ", ",")
    
    result = ""
    skip_list = ["[", "]", "(", ")", ","]
    in_skip_zone = False
    for char in type_string:
        if (char not in skip_list) and (not in_skip_zone):
            result += "<xref:" + char
            in_skip_zone = True
        elif (char in skip_list) and (in_skip_zone):
            result += ">" + char
            in_skip_zone = False
        else:
            result += char
    if result[-1].isalpha():
        result += ">" 
    return result

def get_resolved_xref(_type_without_xref):
    _type = _type_without_xref
    _type_without_xref, _added_reference = resolve_type( _type_without_xref)
    if _added_reference:
        _type = resolve_xref_type(_added_reference)
    if _type.find('<xref:') >= 0:
        return _type
    else:
        return '<xref:' + _type + '>'

def extract_types(ret_data, skip_index_set = [], description_index = None):
    nodes = ret_data.children
    type_list = []
    type_str = ""
    param_zone_start_index = 2
    if description_index is not None:
        param_zone_end_index = description_index - 2
    else:
        param_zone_end_index = len(nodes) - 2
    
    for i in range(param_zone_start_index, param_zone_end_index):
        if i in skip_index_set:
            continue
        node = nodes[i]
        node_text = node.astext().lstrip('~')
        if node.tagname == 'reference':
            if is_system_type(node_text):
                type_str += f'<xref:{node_text}>'
            elif is_typing(node_text, node):
                if "typing." not in node_text:
                    type_str += f'<xref:typing.{node_text}>'
                else:
                    type_str += f'<xref:{node_text}>'
            elif is_complex_type(node_text):
                type_str += process_complex_type(node_text)
            else:
                if 'refid' in node.attributes:
                    temp_str = node["refid"].lstrip('~')
                    type_str += f'<xref:{temp_str}>'
                elif 'refuri' in node.attributes:
                    temp_str = node["refuri"].lstrip('~')
                    type_str += f'<xref:{temp_str}>'
                else:
                    type_str += get_resolved_xref(node_text)
        else:
            type_str += node_text
    type_str = type_str.replace('\n', ' ')

    raw_type_list = type_str.split(' or ')
        
    for _type in raw_type_list:
        if 'xref' in _type:
            type_list.append(_type.strip().rstrip(','))

    return type_list

def extract_default_value(ret_data):
    nodes = ret_data.children
    default_value = None
    skip_index = None
    for node in nodes:
        if node.tagname == 'emphasis' and node.astext() == 'default':
            skip_index = nodes.index(node) + 2
            default_value = nodes[skip_index].astext()
    
    if skip_index is None:
        return default_value, None
    else:
        return default_value, set(range(skip_index - 2, skip_index + 2))

def extract_description(ret_data, app):
    transform_node = app.docfx_transform_node
    nodes = ret_data.children
    description_index = None
    for node in nodes:
        if node.tagname == "#text" and node.astext().strip() in ['–', '––', '--']:
            description_index = nodes.index(node) + 1
            break
    
    transformed_node = transform_node(ret_data)
    description_part_index = transformed_node.find('–')
    _description = transformed_node[description_part_index + 1 : ]
    return _description, description_index
    
def parse_parameter(ret_data, fieldtype, app):
    _id = None
    _description = None
    _type_list = []
    _default_value = None
    description_index = None
    
    ret_data_text = ret_data.astext()
    hyphen_index = ret_data_text.find('–')
    parameter_definition_part = ret_data_text[:hyphen_index]
    _description, description_index = extract_description(ret_data, app)

    if parameter_definition_part.find('(') >= 0:
        _id = parameter_definition_part[: parameter_definition_part.find('(')]
        
        _default_value, skip_index_set = extract_default_value(ret_data)
        if skip_index_set is  None:
            skip_index_set = {}
        _type_list = extract_types(ret_data, skip_index_set, description_index)
    else:
        _id = parameter_definition_part
    
    _data = make_param(_id, _description, _type_list, _default_value, _required=False if fieldtype == 'Keyword' else True)
    return _data