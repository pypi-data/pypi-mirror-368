# -*- coding: utf-8 -*-


class KeystoneScopeType(object):

    """Implementation of the 'Keystone Scope Type' model.

    Scope type of a Keystone configuration.

    Attributes:
        keystone_scope_type (KeystoneScopeType1Enum): Specifies the scope type
            of a Keystone configuration.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "keystone_scope_type":'keystoneScopeType'
    }

    def __init__(self,
                 keystone_scope_type=None):
        """Constructor for the KeystoneScopeType class"""

        # Initialize members of the class
        self.keystone_scope_type = keystone_scope_type


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
        keystone_scope_type = dictionary.get('keystoneScopeType')

        # Return an object of this model
        return cls(keystone_scope_type)


