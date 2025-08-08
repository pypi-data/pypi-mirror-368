class TestClass:
    def test_method(self,
                    positional_only_param,
                    /,
                    parameter,
                    *,
                    keyword_only_arg,
                    **kwargs):
        """
        This is a test method
        
        :param str parameter: This is a parameter
        :keyword bool keyword_only_arg: This is a keyword only argument
        """
        pass
    