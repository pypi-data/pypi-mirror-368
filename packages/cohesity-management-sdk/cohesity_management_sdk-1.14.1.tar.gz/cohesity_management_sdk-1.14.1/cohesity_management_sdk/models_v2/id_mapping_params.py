# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.user_id_mapping_params_2

class IdMappingParams(object):

    """Implementation of the 'IdMappingParams' model.

    Specifies the params of the user id mapping info of an Active Directory.

    Attributes:
        sid_mapped_to_unix_root_user (string): Specifies the sid of an Active
            Directory domain user mapping to unix root user.
        user_id_mapping_params (UserIdMappingParams2): Specifies the
            information about how the Unix and Windows users are mapped for
            this domain.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "sid_mapped_to_unix_root_user":'sidMappedToUnixRootUser',
        "user_id_mapping_params":'userIdMappingParams'
    }

    def __init__(self,
                 sid_mapped_to_unix_root_user=None,
                 user_id_mapping_params=None):
        """Constructor for the IdMappingParams class"""

        # Initialize members of the class
        self.sid_mapped_to_unix_root_user = sid_mapped_to_unix_root_user
        self.user_id_mapping_params = user_id_mapping_params


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
        sid_mapped_to_unix_root_user = dictionary.get('sidMappedToUnixRootUser')
        user_id_mapping_params = cohesity_management_sdk.models_v2.user_id_mapping_params_2.UserIdMappingParams2.from_dictionary(dictionary.get('userIdMappingParams')) if dictionary.get('userIdMappingParams') else None

        # Return an object of this model
        return cls(sid_mapped_to_unix_root_user,
                   user_id_mapping_params)


