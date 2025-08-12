# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.physical_volume_protection_group_params
import cohesity_management_sdk.models_v2.physical_file_protection_group_params

class PhysicalProtectionGroupParams(object):

    """Implementation of the 'Physical Protection Group Params.' model.

    Specifies the parameters specific to Physical Protection Group.

    Attributes:
        file_protection_type_params (PhysicalFileProtectionGroupParams):
           Specifies the File based Physical Protection Group params.
        protection_type (ProtectionType8Enum): Specifies the Physical
            Protection Group type.
        volume_protection_type_params (PhysicalVolumeProtectionGroupParams):
            Specifies the parameters which are specific to Volume based
            physical Protection Groups.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_type":'protectionType',
        "volume_protection_type_params":'volumeProtectionTypeParams',
        "file_protection_type_params":'fileProtectionTypeParams'
    }

    def __init__(self,
                 protection_type=None,
                 volume_protection_type_params=None,
                 file_protection_type_params=None):
        """Constructor for the PhysicalProtectionGroupParams class"""

        # Initialize members of the class
        self.protection_type = protection_type
        self.volume_protection_type_params = volume_protection_type_params
        self.file_protection_type_params = file_protection_type_params


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
        protection_type = dictionary.get('protectionType')
        volume_protection_type_params = cohesity_management_sdk.models_v2.physical_volume_protection_group_params.PhysicalVolumeProtectionGroupParams.from_dictionary(dictionary.get('volumeProtectionTypeParams')) if dictionary.get('volumeProtectionTypeParams') else None
        file_protection_type_params = cohesity_management_sdk.models_v2.physical_file_protection_group_params.PhysicalFileProtectionGroupParams.from_dictionary(dictionary.get('fileProtectionTypeParams')) if dictionary.get('fileProtectionTypeParams') else None

        # Return an object of this model
        return cls(protection_type,
                   volume_protection_type_params,
                   file_protection_type_params)