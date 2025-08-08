class ExceptionWithAttribute(Exception):
    attribute1 = "foo"

class ClassWithAttribute():
    attribute1 = "foo"
    '''
    Attribute 1 description
    '''

class DuplicateNameClassWithAttribute():
    attribute2 = "foo"
    '''
    Attribute2 under code_with_docstring.DuplicateNameClassWithAttribute
    '''