# Test data class
# Use :py: prefix to reference an api (since our test utils isn't appointing python domain now)
# use fullname (MODULE_NAME.OBJECT_NAME) to reference an object to ensure transformer can find it

class ClassForTest:
    async def function_basicAsyncMethod(self, param1):
        """
        Some description
        """
        pass

    def function_basicMethod(self, param1):
        """
        Some description
        """
        pass