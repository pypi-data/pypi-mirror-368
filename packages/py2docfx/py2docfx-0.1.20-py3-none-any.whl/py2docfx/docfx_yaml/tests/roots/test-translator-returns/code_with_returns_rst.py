from refered_objects import referee
from refered_objects import List
from collections.abc import MutableMapping

class dummyClass():

    def complex_type(self):
        """
        :rtype: Any[Dict[str, Any]]
        """
        pass

    def user_designated_builtin_type(self):
        """
        :rtype: ~collections.abc.MutableMapping
        """
        pass

    def user_defined_type_with_same_name_as_builtin_type(self):
        """
        :rtype: ~refered_objects.List
        """
        pass

    def user_defined_type(self):
        """
        :rtype: ~refered_objects.referee
        """
        pass