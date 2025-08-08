

class SampleClass():
    """
    :param dummy_param:
        Dummy Param

        Table:

        +---------+---------+---------+---------+
        | header1 | header2 | header3 | header4 |
        +=========+=========+=========+=========+
        | a       | b       | c       | d       |
        +---------+---------+---------+---------+
        | e       | f       | g       | h       |
        +---------+---------+---------+---------+
    """
    def dummy_param(self):
        """
            Dummy Param
        """
        pass


class ExperimentalClass():
    """
        Experimental Class

        .. list-table:: Supported Functions
            :header-rows: 1
            :widths: 30 30 50

            * - Boo
              - API
              - Example
            * - Foo
              - List Foo
              - ``GET /dummy/foo``
            * - Bar
              - Create Bar
              - ``POST /dummy/bar``
    """
    def some_method(self):
        """
            Some method
        """
        return "some_result"
    