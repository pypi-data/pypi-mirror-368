# -*- coding: utf-8 -*-


class Office365O365OutlookProtectionGroupParameters(object):

    """Implementation of the 'Office 365(O365) Outlook Protection Group Parameters.' model.

    Specifies the parameters which are specific to Office 365 Outlook related
    Protection Groups.

    Attributes:
        exclude_folders (list of string): Array of Excluded Outlook folders.
            Specifies filters to match Outlook folders which should be
            excluded when backing up Office 365 source. Two kinds of filters
            are supported. a) prefix which always starts with '/'. b) posix
            which always starts with empty quotes(''). Regular expressions are
            not supported. If not specified, all the mailboxes will be
            protected.
        include_folders (list of string): Array of prefixes used to include folders which are by default
          excluded. Two kinds of filters are supported. a) prefix which always starts
          with '/'. b) posix which always starts with empty quotes(''). Regular expressions
          are not supported. If not specified, all folders which are excluded by default
          will be excluded. These prefixes have no effect on folders that are included
          by default. All folders are included by default except for the Recoverable
          Items folder.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "exclude_folders":'excludeFolders',
        "include_folders":'includeFolders'
    }

    def __init__(self,
                 exclude_folders=None,
                 include_folders=None):
        """Constructor for the Office365O365OutlookProtectionGroupParameters class"""

        # Initialize members of the class
        self.exclude_folders = exclude_folders
        self.include_folders = include_folders


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
        include_folders = dictionary.get('includeFolders')

        # Return an object of this model
        return cls(exclude_folders,
                   include_folders)