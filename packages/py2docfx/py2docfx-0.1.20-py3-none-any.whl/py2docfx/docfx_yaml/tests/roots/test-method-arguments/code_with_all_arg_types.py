class TestClass:
    def test_method(self,
                    positional_only_param = 10,
                    /,
                    parameter_with_default_value=True,
                    *,
                    keyword_only_arg = "keyword_only_arg_default_value",
                    **kwargs):
        pass
    