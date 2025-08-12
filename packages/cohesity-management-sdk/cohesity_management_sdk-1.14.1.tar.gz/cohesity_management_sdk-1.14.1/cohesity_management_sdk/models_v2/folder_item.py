# -*- coding: utf-8 -*-


class FolderItem(object):

    """Implementation of the 'FolderItem' model.

    Specifies an email folder to recover.

    Attributes:
        key (long|int): Specifies the email folder key.
        recover_entire_folder (bool): Specifies whether to recover the whole
            email folder.
        item_ids (list of string): Specifies a list of item ids to recover.
            This field is applicable only if 'recoverEntireFolder' is false.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "key":'key',
        "recover_entire_folder":'recoverEntireFolder',
        "item_ids":'itemIds'
    }

    def __init__(self,
                 key=None,
                 recover_entire_folder=None,
                 item_ids=None):
        """Constructor for the FolderItem class"""

        # Initialize members of the class
        self.key = key
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
        key = dictionary.get('key')
        recover_entire_folder = dictionary.get('recoverEntireFolder')
        item_ids = dictionary.get('itemIds')

        # Return an object of this model
        return cls(key,
                   recover_entire_folder,
                   item_ids)


