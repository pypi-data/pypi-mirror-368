# -*- coding: utf-8 -*-


class ProtectionGroupIdentifier(object):

    """Implementation of the 'Protection Group Identifier.' model.

    Specifies Protection Group Identifier.

    Attributes:
        protection_group_id (string): Specifies Protection Group id.
        protection_group_name (string): Specifies Protection Group name.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_group_id":'protectionGroupId',
        "protection_group_name":'protectionGroupName'
    }

    def __init__(self,
                 protection_group_id=None,
                 protection_group_name=None):
        """Constructor for the ProtectionGroupIdentifier class"""

        # Initialize members of the class
        self.protection_group_id = protection_group_id
        self.protection_group_name = protection_group_name


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
        protection_group_id = dictionary.get('protectionGroupId')
        protection_group_name = dictionary.get('protectionGroupName')

        # Return an object of this model
        return cls(protection_group_id,
                   protection_group_name)


