import sys
import parameter_utils

def split_by(symbol, text):
    return [item.strip() for item in text.split(symbol)]

def is_part_of_name(character) -> bool:
    # an upper or lower case letter and an underscore would be a valid type name
    return character.isalpha() or character.isnumeric() or character == '_' or character == '.'

def endswith_mathching(class_obj_cache, type_name, refuri):

    matches = [item for item in class_obj_cache if item.endswith('.' + type_name)]

    # if there is no match, return the refuri if it ends with type_name
    if len(matches) == 0:
        if refuri.endswith("." + type_name):
            return refuri
        else:
            return type_name

    # if there is only one match, return the match
    if len(matches) == 1:
        return matches[0]

    # if there are multiple matches, get a list of canonicals, return the first one
    if len(matches) > 1:
        canonicals = [m for m in matches if not class_obj_cache[m].aliased]
        return canonicals[0]

def full_text_matching(match_string, class_obj_cache, type_dict):
    # check for class_obj_cache first, because we want user defined type to be prioritized
    if match_string in class_obj_cache:
        return f'<xref:{match_string}>'
    if match_string in type_dict:
        if type_dict[match_string] == parameter_utils.TYPING_TYPE:
            return f'<xref:typing.{match_string}>'
        else:
            return f'<xref:{match_string}>'
    return None

def proceed_type_name(class_obj_cache, type_name, module_name, refuri):
    """
    Priority Ranking:
    1. refuri full text matching
    2. refuri sys.modules matching
    3. type name full text matching
    4. module name + type name full text matching
    5. type name endswith matching

    The reason why we always want to use refuri to be top priority is because
    refuri will mostly have more information.
    For example, ~some_module.SomeClass
    Refuri will be some_module.SomeClass, while type name will only be SomeClass

    Sometimes, there will be empty refuri or error refuri, in that case, we will 1 and 2 would find no match
    and type name matching would be the fallback option.
    For example, in numpy style docstring
    Refuri could be some_module.SomeClass.Any]] and type name is Any

    4, module name + type name full text matching, is a reasonalbe guess that the user is trying to reference
    a type that is user defined in the same module, but the user did not use the full name.

    If all 1 to 4 fails, we will use endswith matching as the final fallback option.
    """

    if type_name in ["", "or"]:
        return type_name

    # if # in refuri, it means that sphinx has resolved the type name
    # take the part after # as the type name
    if len(refuri.split('#')) > 1:
        type_name = refuri.split('#')[-1]
        return f'<xref:{type_name}>'

    type_dict = parameter_utils.builtin_type_dict

    # try get the match using refuri
    refuri_matching_result = full_text_matching(refuri, class_obj_cache, type_dict)

    # if the module name of refuri is not the same as module name of the current file
    # and the module name of refuri can be found in sys.modules (means it is imported in source code)
    # we can assume that writer was intenionally crossreferencing to another module
    # return the refuri
    refuri_module_name = refuri[0:refuri.rfind('.')] if '.' in refuri else None
    if refuri_module_name:
        if refuri_module_name != module_name and refuri_module_name in sys.modules:
            return f'<xref:{refuri}>'

    # try get the match using type name
    type_name_matching_result = full_text_matching(type_name, class_obj_cache, type_dict)

    # if both type name and refuri have a match, return the one from refuri
    # because we want user defined type to be prioritized
    if type_name_matching_result and refuri_matching_result:
        return refuri_matching_result
    elif type_name_matching_result:
        return type_name_matching_result
    elif refuri_matching_result:
        return refuri_matching_result

    # try get the match using module name + type name
    fullname_matching_result = full_text_matching(module_name + "." + type_name, class_obj_cache, type_dict)
    if fullname_matching_result is not None:
        return fullname_matching_result

    # try get the match using endswith matching mode
    endwith_matching_result = endswith_mathching(class_obj_cache, type_name, refuri)
    if endwith_matching_result is not None:
        return f'<xref:{endwith_matching_result}>'

    return f'<xref:{type_name}>'

def proceed_return_type(class_obj_cache, return_node, module_name):
    node_text = return_node.astext()
    symbol_index_list = [] # symbols are "[" and "]" etc.
    
    # record the full reference name from sphinx
    # primirily from refuri, some nodes do not have refuri but have reftarget instead
    # if there is no refuri or reftarget, leave resolved_type_from_sphinx to be an empty string
    resolved_type_from_sphinx = ""
    if return_node.tagname == 'reference':
        if "reftarget" in return_node.attributes:
            resolved_type_from_sphinx = return_node.attributes["reftarget"]
        elif "refid" in return_node.attributes:
            resolved_type_from_sphinx = return_node.attributes["refid"]
        elif "refuri" in return_node.attributes:
            resolved_type_from_sphinx = return_node.attributes["refuri"]

    # find all the symbols in the node text
    for i, character in enumerate(node_text):
        if not is_part_of_name(character):
            symbol_index_list.append(i)

    # if there is just one symbol or empty in the node text, return the node text
    if node_text.strip() in ["[", "]", "(", ")", ",", "", "or"]:
        return node_text

    # if there is no symbol in the node text, which means it is a simple type name
    # return proceeded type name
    if len(symbol_index_list) == 0:
        return proceed_type_name(class_obj_cache, node_text, module_name, resolved_type_from_sphinx)

    # if there is a symbol in the node text, which means it is a complex type name
    # use index list to split the node text into several parts and proceed each part
    type_name = ""
    for i,symbol_index in enumerate(symbol_index_list):
        if i == 0:
            temp_type_name = proceed_type_name(class_obj_cache, node_text[:symbol_index], module_name, resolved_type_from_sphinx) + node_text[symbol_index]
        else:
            temp_type_name = proceed_type_name(class_obj_cache, node_text[symbol_index_list[i-1]+1:symbol_index], module_name, resolved_type_from_sphinx) + node_text[symbol_index]
        type_name += temp_type_name

    # the last symbol index might not be at the end of the node text srting
    # so we need to proceed the rest of the node text
    if symbol_index_list[-1] < len(node_text) - 1:
        type_name += proceed_type_name(class_obj_cache, node_text[symbol_index_list[-1] + 1:], module_name, resolved_type_from_sphinx)

    return type_name

def get_return_type(class_obj_cache ,return_node, module_name):
    type_string = ""
    for child_node in return_node:
        type_string += proceed_return_type(class_obj_cache, child_node, module_name)
    return type_string.lstrip("~").replace("\n", " ").split(" or ")
