# -*- coding: utf-8 -*-


class ResetOrRestoreNetworking(object):

    """Implementation of the 'ResetOrRestoreNetworking' model.

    Update cluster or node reset state information

    Attributes:
        operation (Operation1Enum): Cancel reset cluster or node state
            operation.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "operation":'operation'
    }

    def __init__(self,
                 operation=None):
        """Constructor for the ResetOrRestoreNetworking class"""

        # Initialize members of the class
        self.operation = operation


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
        operation = dictionary.get('operation')

        # Return an object of this model
        return cls(operation)


