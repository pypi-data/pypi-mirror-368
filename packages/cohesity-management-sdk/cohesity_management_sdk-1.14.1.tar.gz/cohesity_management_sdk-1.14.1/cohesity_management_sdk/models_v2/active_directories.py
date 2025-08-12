# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.active_directory

class ActiveDirectories(object):

    """Implementation of the 'ActiveDirectories' model.

    Response of Active Directories.

    Attributes:
        active_directories (list of ActiveDirectory): A list of Active
            Directories.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "active_directories":'activeDirectories'
    }

    def __init__(self,
                 active_directories=None):
        """Constructor for the ActiveDirectories class"""

        # Initialize members of the class
        self.active_directories = active_directories


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
        active_directories = None
        if dictionary.get("activeDirectories") is not None:
            active_directories = list()
            for structure in dictionary.get('activeDirectories'):
                active_directories.append(cohesity_management_sdk.models_v2.active_directory.ActiveDirectory.from_dictionary(structure))

        # Return an object of this model
        return cls(active_directories)


