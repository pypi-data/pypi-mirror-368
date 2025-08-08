# Test data class
# Use :py: prefix to reference an api (since our test utils isn't appointing python domain now)
# use fullname (MODULE_NAME.OBJECT_NAME) to reference an object to ensure transformer can find it

__all__ = ["test"]

class ClassForTest:
    """
        not suppose to show
    """
    pass


test = ClassForTest()
"""
    test test test
"""