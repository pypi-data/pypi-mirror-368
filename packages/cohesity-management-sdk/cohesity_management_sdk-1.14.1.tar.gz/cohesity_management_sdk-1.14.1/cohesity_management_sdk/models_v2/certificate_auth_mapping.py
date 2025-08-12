# -*- coding: utf-8 -*-


class CertificateAuthMapping(object):

    """Implementation of the 'Certificate Auth Mapping' model.

    Describes certificate mapping options for certificate based
    authentication.

    Attributes:
        enum (Enum1Enum): Specifies the auth field options

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "enum":'enum'
    }

    def __init__(self,
                 enum=None):
        """Constructor for the CertificateAuthMapping class"""

        # Initialize members of the class
        self.enum = enum


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
        enum = dictionary.get('enum')

        # Return an object of this model
        return cls(enum)


