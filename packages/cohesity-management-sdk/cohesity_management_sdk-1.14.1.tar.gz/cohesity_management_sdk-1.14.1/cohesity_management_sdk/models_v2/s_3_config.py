# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.acl_config_1
import cohesity_management_sdk.models_v2.owner_info_2

class S3Config(object):

    """Implementation of the 'S3Config' model.

    Specifies the S3 config settings for this View.

    Attributes:
        s_3_access_path (string): Specifies the path to access this View as an
            S3 share.
        acl_config (AclConfig1): Specifies the ACL config of the View as an S3
            bucket.
        owner_info (OwnerInfo2): Specifies the owner info of the View as an S3
            bucket.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "s_3_access_path":'s3AccessPath',
        "acl_config":'aclConfig',
        "owner_info":'ownerInfo'
    }

    def __init__(self,
                 s_3_access_path=None,
                 acl_config=None,
                 owner_info=None):
        """Constructor for the S3Config class"""

        # Initialize members of the class
        self.s_3_access_path = s_3_access_path
        self.acl_config = acl_config
        self.owner_info = owner_info


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
        s_3_access_path = dictionary.get('s3AccessPath')
        acl_config = cohesity_management_sdk.models_v2.acl_config_1.AclConfig1.from_dictionary(dictionary.get('aclConfig')) if dictionary.get('aclConfig') else None
        owner_info = cohesity_management_sdk.models_v2.owner_info_2.OwnerInfo2.from_dictionary(dictionary.get('ownerInfo')) if dictionary.get('ownerInfo') else None

        # Return an object of this model
        return cls(s_3_access_path,
                   acl_config,
                   owner_info)


