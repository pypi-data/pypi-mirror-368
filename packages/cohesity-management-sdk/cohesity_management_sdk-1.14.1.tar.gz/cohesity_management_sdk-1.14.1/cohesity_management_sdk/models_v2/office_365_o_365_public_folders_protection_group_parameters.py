# -*- coding: utf-8 -*-


class Office365O365PublicFoldersProtectionGroupParameters(object):

    """Implementation of the 'Office 365(O365) PublicFolders Protection Group Parameters.' model.

    Specifies the parameters which are specific to Office 365 PublicFolders
    related Protection Groups.

    Attributes:
        exclude_folders (list of string): Array of Excluded Public folders.
            Specifies filters to match PublicFolder folders which should be
            excluded when backing up Office 365 source. Two kinds of filters
            are supported. a) prefix which always starts with '/'. b) posix
            which always starts with empty quotes(''). Regular expressions are
            not supported. If not specified, all the PublicFolders will be
            protected.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "exclude_folders":'excludeFolders'
    }

    def __init__(self,
                 exclude_folders=None):
        """Constructor for the Office365O365PublicFoldersProtectionGroupParameters class"""

        # Initialize members of the class
        self.exclude_folders = exclude_folders


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
        exclude_folders = dictionary.get('excludeFolders')

        # Return an object of this model
        return cls(exclude_folders)


