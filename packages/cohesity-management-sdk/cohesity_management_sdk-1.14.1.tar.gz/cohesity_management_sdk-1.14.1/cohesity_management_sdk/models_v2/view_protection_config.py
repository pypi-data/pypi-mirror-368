# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.existing_group_param
import cohesity_management_sdk.models_v2.new_group_param

class ViewProtectionConfig(object):

    """Implementation of the 'View Protection Config.' model.

    Specifies the View protection config.

    Attributes:
        protection_group_type (ProtectionGroupTypeEnum): Specifies the View
            protection group type.
        existing_group_param (ExistingGroupParam): Specifies the parameters
            used for existing protection group.
        new_group_param (NewGroupParam): Specifies the parameters used for
            new protection group.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_group_type":'protectionGroupType',
        "existing_group_param":'existingGroupParam',
        "new_group_param":'newGroupParam'
    }

    def __init__(self,
                 protection_group_type=None,
                 existing_group_param=None,
                 new_group_param=None):
        """Constructor for the ViewProtectionConfig class"""

        # Initialize members of the class
        self.protection_group_type = protection_group_type
        self.existing_group_param = existing_group_param
        self.new_group_param = new_group_param


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
        protection_group_type = dictionary.get('protectionGroupType')
        existing_group_param = cohesity_management_sdk.models_v2.existing_group_param.ExistingGroupParam.from_dictionary(dictionary.get('existingGroupParam')) if dictionary.get('existingGroupParam') else None
        new_group_param = cohesity_management_sdk.models_v2.new_group_param.NewGroupParam.from_dictionary(dictionary.get('newGroupParam')) if dictionary.get('newGroupParam') else None


        # Return an object of this model
        return cls(protection_group_type,
                   existing_group_param,
                   new_group_param)