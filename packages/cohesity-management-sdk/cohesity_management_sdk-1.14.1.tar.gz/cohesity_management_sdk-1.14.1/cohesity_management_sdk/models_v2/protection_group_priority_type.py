# -*- coding: utf-8 -*-


class ProtectionGroupPriorityType(object):

    """Implementation of the 'Protection Group Priority type.' model.

    Protection Group Priority type.

    Attributes:
        protection_group_priority (ProtectionGroupPriorityEnum): Specifies
            Protection Group priority.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_group_priority":'protectionGroupPriority'
    }

    def __init__(self,
                 protection_group_priority=None):
        """Constructor for the ProtectionGroupPriorityType class"""

        # Initialize members of the class
        self.protection_group_priority = protection_group_priority


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
        protection_group_priority = dictionary.get('protectionGroupPriority')

        # Return an object of this model
        return cls(protection_group_priority)


