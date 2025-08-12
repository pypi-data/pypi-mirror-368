# -*- coding: utf-8 -*-


class PublicFolder(object):

    """Implementation of the 'PublicFolder' model.

    Specifies an PublicFolder item to recover.

    Attributes:
        folder_id (string): Specifies the Unique ID of the folder.
        recover_entire_folder (bool): Specifies whether to recover the whole
            PublicFolder.
        item_ids (list of string): Specifies a list of item ids to recover.
            This field is applicable only if 'recoverEntireFolder' is false.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "folder_id":'folderId',
        "recover_entire_folder":'recoverEntireFolder',
        "item_ids":'itemIds'
    }

    def __init__(self,
                 folder_id=None,
                 recover_entire_folder=None,
                 item_ids=None):
        """Constructor for the PublicFolder class"""

        # Initialize members of the class
        self.folder_id = folder_id
        self.recover_entire_folder = recover_entire_folder
        self.item_ids = item_ids


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
        folder_id = dictionary.get('folderId')
        recover_entire_folder = dictionary.get('recoverEntireFolder')
        item_ids = dictionary.get('itemIds')

        # Return an object of this model
        return cls(folder_id,
                   recover_entire_folder,
                   item_ids)


