# -*- coding: utf-8 -*-


class CsrKeyType(object):

    """Implementation of the 'CsrKeyType' model.

    Csr Key Type

    Attributes:
        csr_key_type (CsrKeyType1Enum): Specifies the csr key type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "csr_key_type":'csrKeyType'
    }

    def __init__(self,
                 csr_key_type=None):
        """Constructor for the CsrKeyType class"""

        # Initialize members of the class
        self.csr_key_type = csr_key_type


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
        csr_key_type = dictionary.get('csrKeyType')

        # Return an object of this model
        return cls(csr_key_type)


