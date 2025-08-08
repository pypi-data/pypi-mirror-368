def is_inline_text_children_of_versionmodified(node):
    if hasattr(node, 'parent') and node.parent is not None:
        if hasattr(node.parent, 'parent') and node.parent.parent is not None:
            if node.parent.parent.tagname == 'versionmodified':
                return True
    return False