# Test data class
# Use :py: prefix to reference an api (since our test utils isn't appointing python domain now)
# use fullname (MODULE_NAME.OBJECT_NAME) to reference an object to ensure transformer can find it
class ClassForTest:
    def function_docstringWithDescriptionRaise(self):
        """
        Some description

        :returns: An instance of KeyVaultCertificate
        :rtype: :py:class:`int`
        :raises: 
            :py:class:`~refered_objects.ExceptionType1` if condition 1 happens
        """
        pass

    def function_docstringWithDescriptionRaiseContainingNestedCodeSyntax(self):
        """
        Some description

        :returns: An instance of KeyVaultCertificate
        :rtype: :py:class:`int`
        :raises: 
            :py:class:`~refered_objects.ExceptionType1` if ``condition`` 1 happens
            :py:class:`~refered_objects.ExceptionType2` if `condition` 2 happens
        """
        pass

    def function_docstringWithMultipleRaiseType(self):
        """
        Some description

        :returns: An instance of KeyVaultCertificate
        :rtype: :py:class:`int`
        :raises: 
            :py:class:`~refered_objects.ExceptionType1`
            :py:class:`~refered_objects.ExceptionType2`
        """
        pass

    def function_docstringWithMultipleRaiseTypeWithLineBreaker(self):
        """
        Some description

        :returns: An instance of KeyVaultCertificate
        :rtype: :py:class:`int`
        :raises: 
            :py:class:`~refered_objects.ExceptionType1`, \
            :py:class:`~refered_objects.ExceptionType2`, \
        """

    def function_docstringWithMultipleInlineRaiseTypeConnectedByOr(self):
        """
        Some description

        :returns: An instance of KeyVaultCertificate
        :rtype: :py:class:`int`
        :raises ~refered_objects.ExceptionType1 or ~refered_objects.ExceptionType2:
        """
        pass

    def function_docstringWithMultipleInlineRaiseDirectives(self):
        """
        Some description

        :returns: An instance of KeyVaultCertificate
        :rtype: :py:class:`int`
        :raises ~refered_objects.ExceptionType1: if condition 1 happens 
        :raises ~refered_objects.ExceptionType2: if condition 2 happens
        """
        pass

    def function_docstringWithExplicitTitleAndReferenceRaiseDirectives(self):
        """
        Some description

        :returns: An instance of KeyVaultCertificate
        :rtype: :py:class:`int`
        :raises: :py:class:`ExceptionType1<refered_objects.ExceptionType1>` 
            if condition 1 happens
        """
        pass

    # This docstring lacks :class: declaration, at least we should try to turn it to type
    def function_docstringWithIncorrectSyntax(self):
        """
        Some description

        :returns: An instance of KeyVaultCertificate
        :rtype: :py:class:`int`
        :raises: `HttpOperationError<msrest.exceptions.HttpOperationError>`
            if the HTTP response status is not in [200].
        """
        pass
    
    def function_docstringWithMultipleRaiseDeclarationSections(self):
        """
        Some description

        :returns: An instance of KeyVaultCertificate
        :rtype: :py:class:`int`
        :raises: :py:class:`~refered_objects.ExceptionType1` if condition 1 happens
        :raises: :py:class:`~refered_objects.ExceptionType2` if condition 2 happens
        """
        pass