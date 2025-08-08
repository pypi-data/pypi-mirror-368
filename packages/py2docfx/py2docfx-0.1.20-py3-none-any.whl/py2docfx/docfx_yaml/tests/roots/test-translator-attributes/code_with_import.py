# Test data class
# Use :py: prefix to reference an api (since our test utils isn't appointing python domain now)
# use fullname (MODULE_NAME.OBJECT_NAME) to reference an object to ensure transformer can find it

from refered_objects import ReferenceType1 as alias1

__all__ = ("alias1", )
