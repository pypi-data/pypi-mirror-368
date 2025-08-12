# -*- coding: utf-8 -*-


class CommonTdmTaskRequestParams(object):

    """Implementation of the 'CommonTdmTaskRequestParams' model.

    Specifies the common parameters used in TDM Task Creation.

    Attributes:
        action (Action1Enum): Specifies the TDM Task action.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "action":'action'
    }

    def __init__(self,
                 action=None):
        """Constructor for the CommonTdmTaskRequestParams class"""

        # Initialize members of the class
        self.action = action


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
        action = dictionary.get('action')

        # Return an object of this model
        return cls(action)


