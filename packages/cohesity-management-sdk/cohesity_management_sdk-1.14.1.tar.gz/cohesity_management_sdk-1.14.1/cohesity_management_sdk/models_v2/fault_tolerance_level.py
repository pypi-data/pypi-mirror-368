# -*- coding: utf-8 -*-


class FaultToleranceLevel(object):

    """Implementation of the 'FaultToleranceLevel' model.

    Fault Tolerance Level

    Attributes:
        state (State1Enum): Fault Tolerance Level

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "state":'state'
    }

    def __init__(self,
                 state=None):
        """Constructor for the FaultToleranceLevel class"""

        # Initialize members of the class
        self.state = state


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
        state = dictionary.get('state')

        # Return an object of this model
        return cls(state)