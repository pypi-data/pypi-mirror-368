# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.one_drive_item

class OneDriveParam(object):

    """Implementation of the 'OneDriveParam' model.

    Specifies parameters to recover a OneDrive.

    Attributes:
        id (string): Specifies the OneDrive id.
        name (string): Specifies the OneDrive name.
        recover_entire_drive (bool): Specifies whether to recover the whole
            OneDrive. This is set to false when excluding recovering specific
            drive items.
        recover_items (list of OneDriveItem): Specifies a list of OneDrive
            items to recover.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "recover_entire_drive":'recoverEntireDrive',
        "recover_items":'recoverItems'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 recover_entire_drive=None,
                 recover_items=None):
        """Constructor for the OneDriveParam class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.recover_entire_drive = recover_entire_drive
        self.recover_items = recover_items


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
        id = dictionary.get('id')
        name = dictionary.get('name')
        recover_entire_drive = dictionary.get('recoverEntireDrive')
        recover_items = None
        if dictionary.get("recoverItems") is not None:
            recover_items = list()
            for structure in dictionary.get('recoverItems'):
                recover_items.append(cohesity_management_sdk.models_v2.one_drive_item.OneDriveItem.from_dictionary(structure))

        # Return an object of this model
        return cls(id,
                   name,
                   recover_entire_drive,
                   recover_items)