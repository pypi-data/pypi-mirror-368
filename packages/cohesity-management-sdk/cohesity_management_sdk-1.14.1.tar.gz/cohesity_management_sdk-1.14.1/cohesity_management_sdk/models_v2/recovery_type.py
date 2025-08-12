# -*- coding: utf-8 -*-


class RecoveryType(object):

    """Implementation of the 'Recovery Type' model.

    Recovery Type

    Attributes:
        recovery_type (RecoveryType1Enum): Specifies the recovery types.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_type":'recoveryType'
    }

    def __init__(self,
                 recovery_type=None):
        """Constructor for the RecoveryType class"""

        # Initialize members of the class
        self.recovery_type = recovery_type


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
        recovery_type = dictionary.get('recoveryType')

        # Return an object of this model
        return cls(recovery_type)


