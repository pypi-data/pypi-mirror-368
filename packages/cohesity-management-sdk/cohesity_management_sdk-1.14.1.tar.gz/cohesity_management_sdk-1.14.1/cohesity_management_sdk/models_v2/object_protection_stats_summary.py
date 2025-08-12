# -*- coding: utf-8 -*-


class ObjectProtectionStatsSummary(object):

    """Implementation of the 'Object Protection Stats Summary' model.

    Specifies the count and size of protected and unprotected objects
      for a given environment.

    Attributes:
        deleted_protected_count (long|int): Specifies the count of protected leaf objects which were deleted
          from the source after being protected.
        environment (Environment2Enum): Specifies the environment of the
            object.
        protected_count (long|int): Specifies the count of the protected leaf
            objects.
        unprotected_count (long|int): Specifies the count of the unprotected
            leaf objects.
        protected_size_bytes (long|int): Specifies the protected logical size
            in bytes.
        unprotected_size_bytes (long|int): Specifies the unprotected logical
            size in bytes.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "deleted_protected_count":'deletedProtectedCount',
        "environment":'environment',
        "protected_count":'protectedCount',
        "unprotected_count":'unprotectedCount',
        "protected_size_bytes":'protectedSizeBytes',
        "unprotected_size_bytes":'unprotectedSizeBytes'
    }

    def __init__(self,
                 deleted_protected_count=None,
                 environment=None,
                 protected_count=None,
                 unprotected_count=None,
                 protected_size_bytes=None,
                 unprotected_size_bytes=None):
        """Constructor for the ObjectProtectionStatsSummary class"""

        # Initialize members of the class
        self.deleted_protected_count = deleted_protected_count
        self.environment = environment
        self.protected_count = protected_count
        self.unprotected_count = unprotected_count
        self.protected_size_bytes = protected_size_bytes
        self.unprotected_size_bytes = unprotected_size_bytes


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        deleted_protected_count = dictionary.get('deletedProtectedCount')
        environment = dictionary.get('environment')
        protected_count = dictionary.get('protectedCount')
        unprotected_count = dictionary.get('unprotectedCount')
        protected_size_bytes = dictionary.get('protectedSizeBytes')
        unprotected_size_bytes = dictionary.get('unprotectedSizeBytes')

        # Return an object of this model
        return cls(
                   deleted_protected_count,
                   environment,
                   protected_count,
                   unprotected_count,
                   protected_size_bytes,
                   unprotected_size_bytes)