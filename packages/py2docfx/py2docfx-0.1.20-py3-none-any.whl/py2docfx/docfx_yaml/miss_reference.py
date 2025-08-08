from docutils import nodes
from docutils.nodes import Element, Node
from utils import is_built_in_type

CLASS = 'class'
REFMETHOD = 'meth'
REFFUNCTION = 'func'


def missing_reference(app, env, node, contnode):
    reftarget = ''
    refdoc = ''
    reftype = ''
    module = ''
    if 'refdomain' in node.attributes and node.attributes['refdomain'] == 'py':
        reftarget = node['reftarget']
        reftype = node['reftype']
        if 'refdoc' in node:
            refdoc = node['refdoc']
        if 'py:module' in node:
            module = node['py:module']

        # Refactor reftarget to fullname if it is a short name
        # refdoc is set as default starting from sphinx 4.x https://github.com/sphinx-doc/sphinx/pull/9685
        # So we use refwarn here to be compatible with sphinx 3.x
        if reftype in [CLASS, REFFUNCTION, REFMETHOD] and module and '.' not in reftarget and 'refwarn' in node.attributes:
            if reftype in [CLASS, REFFUNCTION]:
                fields = (module, reftarget)
            else:
                fields = (module, node['py:class'], reftarget)
            
            if not is_built_in_type(reftarget , node):
                reftarget = '.'.join(
                    field for field in fields if field is not None)

        # Workaround for reference like: ~$(python-base-namespace).v2022_10_01.models.PredictiveResponse
        # Which is unable to be resolved by sphinx 6.x
        elif reftarget.startswith('.'):
            target_index = module.find(reftarget.split('.', 2)[1])
            if target_index != -1:
                reftarget = module[:target_index] + reftarget[1:]

        return make_refnode(app.builder, refdoc, reftarget, '', contnode)


def make_refnode(builder: "Builder", fromdocname: str, todocname: str, targetid: str,
                 child: Node, title: str = None) -> nodes.reference:
    """Shortcut to create a reference node."""
    node = nodes.reference('', '', internal=True)
    if fromdocname == todocname and targetid:
        node['refid'] = targetid
    else:
        if targetid:
            node['refuri'] = (builder.get_relative_uri(fromdocname, todocname) +
                              '#' + targetid)
        else:
            node['refuri'] = builder.get_relative_uri(fromdocname, todocname)
    if title:
        node['reftitle'] = title
    node.append(child)
    return node
