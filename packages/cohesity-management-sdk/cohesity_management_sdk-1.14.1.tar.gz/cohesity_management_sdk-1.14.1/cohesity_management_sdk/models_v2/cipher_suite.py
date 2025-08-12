# -*- coding: utf-8 -*-


class CipherSuite(object):

    """Implementation of the 'CipherSuite' model.

    Cipher Suite

    Attributes:
        cipher (string): Specifies the cipher suite used for TLS handshake.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cipher":'cipher'
    }

    def __init__(self,
                 cipher=None):
        """Constructor for the CipherSuite class"""

        # Initialize members of the class
        self.cipher = cipher


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
        cipher = dictionary.get('cipher')

        # Return an object of this model
        return cls(cipher)


