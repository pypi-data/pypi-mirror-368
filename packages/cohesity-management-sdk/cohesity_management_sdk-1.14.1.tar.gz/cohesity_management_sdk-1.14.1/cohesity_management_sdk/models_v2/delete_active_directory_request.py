# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.active_directory_admin_params_2

class DeleteActiveDirectoryRequest(object):

    """Implementation of the 'DeleteActiveDirectoryRequest' model.

    Specifies the request to delete an Active Directory.

    Attributes:
        active_directory_admin_params (ActiveDirectoryAdminParams2): Specifies
            the params of a user with administrative privilege of this Active
            Directory. This field is mandatory if machine accounts are
            updated.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "active_directory_admin_params":'activeDirectoryAdminParams'
    }

    def __init__(self,
                 active_directory_admin_params=None):
        """Constructor for the DeleteActiveDirectoryRequest class"""

        # Initialize members of the class
        self.active_directory_admin_params = active_directory_admin_params


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
        active_directory_admin_params = cohesity_management_sdk.models_v2.active_directory_admin_params_2.ActiveDirectoryAdminParams2.from_dictionary(dictionary.get('activeDirectoryAdminParams')) if dictionary.get('activeDirectoryAdminParams') else None

        # Return an object of this model
        return cls(active_directory_admin_params)


