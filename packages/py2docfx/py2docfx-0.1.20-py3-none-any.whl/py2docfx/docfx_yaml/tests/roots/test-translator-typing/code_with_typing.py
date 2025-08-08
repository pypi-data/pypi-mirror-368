class TestClass:
    def test_method_with_typing(param):
        """
        :param param: Test Param
        :type param: list[typing.Container]
        """
        pass
    
    def test_method_without_typing(param):
        """
        :param param: Test Param
        :type param: list[~foo.boo.dummy.Container]
        """
        pass