# -*- coding: utf-8 -*-


class FilesAndFoldersObject(object):

    """Implementation of the 'FilesAndFoldersObject' model.

    Specifies a file or folder to download.

    Attributes:
        absolute_path (string): Specifies the absolute path of the file or
            folder.
        is_directory (bool): Specifies whether the file or folder object is a
            directory.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "absolute_path":'absolutePath',
        "is_directory":'isDirectory'
    }

    def __init__(self,
                 absolute_path=None,
                 is_directory=None):
        """Constructor for the FilesAndFoldersObject class"""

        # Initialize members of the class
        self.absolute_path = absolute_path
        self.is_directory = is_directory


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
        absolute_path = dictionary.get('absolutePath')
        is_directory = dictionary.get('isDirectory')

        # Return an object of this model
        return cls(absolute_path,
                   is_directory)


