# -*- coding: utf-8 -*-


class AwsParams(object):

    """Implementation of the 'AwsParams' model.

    Specifies the parameters specific to AWS type snapshot.

    Attributes:
        protection_type (ProtectionType1Enum): Specifies the protection type
            of AWS snapshots.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_type":'protectionType'
    }

    def __init__(self,
                 protection_type=None):
        """Constructor for the AwsParams class"""

        # Initialize members of the class
        self.protection_type = protection_type


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
        protection_type = dictionary.get('protectionType')

        # Return an object of this model
        return cls(protection_type)


