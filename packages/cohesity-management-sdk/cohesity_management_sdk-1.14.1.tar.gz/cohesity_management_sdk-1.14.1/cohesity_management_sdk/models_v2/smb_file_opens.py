# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.smb_active_file_path

class SmbFileOpens(object):

    """Implementation of the 'SmbFileOpens' model.

    Specifies the response to SMB active file opens.

    Attributes:
        active_file_paths (list of SmbActiveFilePath): Specifies the active
            opens for an SMB file in a view.
        cookie (string): Specifies the pagination cookie.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "active_file_paths":'activeFilePaths',
        "cookie":'cookie'
    }

    def __init__(self,
                 active_file_paths=None,
                 cookie=None):
        """Constructor for the SmbFileOpens class"""

        # Initialize members of the class
        self.active_file_paths = active_file_paths
        self.cookie = cookie


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
        active_file_paths = None
        if dictionary.get("activeFilePaths") is not None:
            active_file_paths = list()
            for structure in dictionary.get('activeFilePaths'):
                active_file_paths.append(cohesity_management_sdk.models_v2.smb_active_file_path.SmbActiveFilePath.from_dictionary(structure))
        cookie =  dictionary.get('cookie')

        # Return an object of this model
        return cls(active_file_paths,
                   cookie)


