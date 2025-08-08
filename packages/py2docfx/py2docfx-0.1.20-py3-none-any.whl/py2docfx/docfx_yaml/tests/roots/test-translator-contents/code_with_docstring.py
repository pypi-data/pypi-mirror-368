# Test data class
# Use :py: prefix to reference an api (since our test utils isn't appointing python domain now)
# use fullname (MODULE_NAME.OBJECT_NAME) to reference an object to ensure transformer can find it

class ClassForTest:
    def function_NestedBulletinList(self, param1):
        """
        Bulletin list description:
        1. Item1
           * Item1.SubItem1
           * Item1.SubItem2
        2. Item2
        """
        pass

class ClassWithCodeSummary:
    """
    json: {
        "key": "value",
        "array": [
            {
                "key1": "value",
            },
            {
                "key2": "value",
            }
        ]
    }
    """