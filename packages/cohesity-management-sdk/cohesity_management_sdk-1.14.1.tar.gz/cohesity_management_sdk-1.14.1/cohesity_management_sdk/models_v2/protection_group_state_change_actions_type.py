# -*- coding: utf-8 -*-


class ProtectionGroupStateChangeActionsType(object):

    """Implementation of the 'Protection Group State Change Actions type.' model.

    Protection Group State Change Actions type.

    Attributes:
        protection_group_state_change_actions
            (ProtectionGroupStateChangeActionsEnum): Specifies Protection
            Group State Change Actions type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_group_state_change_actions":'protectionGroupStateChangeActions'
    }

    def __init__(self,
                 protection_group_state_change_actions=None):
        """Constructor for the ProtectionGroupStateChangeActionsType class"""

        # Initialize members of the class
        self.protection_group_state_change_actions = protection_group_state_change_actions


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
        protection_group_state_change_actions = dictionary.get('protectionGroupStateChangeActions')

        # Return an object of this model
        return cls(protection_group_state_change_actions)


