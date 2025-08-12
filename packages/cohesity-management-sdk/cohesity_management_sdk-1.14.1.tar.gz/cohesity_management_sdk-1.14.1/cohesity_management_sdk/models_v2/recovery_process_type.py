# -*- coding: utf-8 -*-


class RecoveryProcessType(object):

    """Implementation of the 'Recovery Process Type' model.

    Recovery Process Type

    Attributes:
        recovery_process_type (RecoveryProcessType4Enum): Specifies the
            recovery process type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_process_type":'recoveryProcessType'
    }

    def __init__(self,
                 recovery_process_type=None):
        """Constructor for the RecoveryProcessType class"""

        # Initialize members of the class
        self.recovery_process_type = recovery_process_type


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
        recovery_process_type = dictionary.get('recoveryProcessType')

        # Return an object of this model
        return cls(recovery_process_type)


