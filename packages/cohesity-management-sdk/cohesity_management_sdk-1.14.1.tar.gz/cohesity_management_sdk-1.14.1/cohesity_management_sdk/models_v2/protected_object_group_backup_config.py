# -*- coding: utf-8 -*-


class ProtectedObjectGroupBackupConfig(object):

    """Implementation of the 'ProtectedObjectGroupBackupConfig' model.

    Specifies the parameters of a protection group which is protecting an
    object.

    Attributes:
        protection_group_id (string): Specifies the protection group id, if
            given object is also protected by a protection group.
        protection_group_name (string): Specifies the protection group name,
            if given object is also protected by a protection group.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_group_id":'protectionGroupId',
        "protection_group_name":'protectionGroupName'
    }

    def __init__(self,
                 protection_group_id=None,
                 protection_group_name=None):
        """Constructor for the ProtectedObjectGroupBackupConfig class"""

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


