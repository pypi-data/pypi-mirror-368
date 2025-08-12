# -*- coding: utf-8 -*-


class OneDriveItem(object):

    """Implementation of the 'OneDriveItem' model.

    Specifies a OneDrive item to recover.

    Attributes:
        id (string): Specifies the item id.
        item_path (string): Specifies the path to the OneDrive item.
        is_file (bool): Specifies if the item is a file.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "item_path":'itemPath',
        "is_file":'isFile'
    }

    def __init__(self,
                 id=None,
                 item_path=None,
                 is_file=None):
        """Constructor for the OneDriveItem class"""

        # Initialize members of the class
        self.id = id
        self.item_path = item_path
        self.is_file = is_file


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
        item_path = dictionary.get('itemPath')
        is_file = dictionary.get('isFile')

        # Return an object of this model
        return cls(id,
                   item_path,
                   is_file)


