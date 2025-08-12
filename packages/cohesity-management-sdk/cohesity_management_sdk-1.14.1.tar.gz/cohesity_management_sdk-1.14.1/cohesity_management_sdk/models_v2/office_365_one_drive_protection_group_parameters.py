# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.office_365_preservation_hold_library_params

class Office365OneDriveProtectionGroupParameters(object):

    """Implementation of the 'Office 365 OneDrive Protection Group Parameters.' model.

    Specifies the parameters which are specific to Office 365 OneDrive related
    Protection Groups.

    Attributes:
        exclude_folders (list of string): Array of Excluded OneDrive folders.
            Specifies filters to match OneDrive folders which should be
            excluded when backing up Office 365 source. Two kinds of filters
            are supported. a) prefix which always starts with '/'. b) posix
            which always starts with empty quotes(''). Regular expressions are
            not supported. If not specified, all the mailboxes will be
            protected.
        preservation_hold_library_params (Office365PreservationHoldLibraryParams):
            Specifies the parameters specific to the protection of the Preservation
          Hold library.


    """

    # Create a mapping from Model property names to API property names
    _names = {
        "exclude_folders":'excludeFolders',
        "preservation_hold_library_params":'preservationHoldLibraryParams'
    }

    def __init__(self,
                 exclude_folders=None,
                 preservation_hold_library_params=None):
        """Constructor for the Office365OneDriveProtectionGroupParameters class"""

        # Initialize members of the class
        self.exclude_folders = exclude_folders
        self.preservation_hold_library_params = preservation_hold_library_params


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
        preservation_hold_library_params = cohesity_management_sdk.models_v2.office_365_preservation_hold_library_params.Office365PreservationLibraryHoldParams.from_dictionary(dictionary.get('preservationHoldLibraryParams')) if dictionary.get('preservationHoldLibraryParams') else None

        # Return an object of this model
        return cls(exclude_folders,
                   preservation_hold_library_params)