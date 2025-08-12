# -*- coding: utf-8 -*-


class AuditActions(object):

    """Implementation of the 'Audit Actions' model.

    Audit Actions

    Attributes:
        actions (ActionsEnum): Audit Actions

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "actions":'actions'
    }

    def __init__(self,
                 actions=None):
        """Constructor for the AuditActions class"""

        # Initialize members of the class
        self.actions = actions


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
        actions = dictionary.get('actions')

        # Return an object of this model
        return cls(actions)


