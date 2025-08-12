# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.rename_recovered_volume_params
import cohesity_management_sdk.models_v2.recovery_object_identifier

class OriginalSourceConfig19(object):

    """Implementation of the 'OriginalSourceConfig19' model.

    Specifies the Source configuration if Pure volume is being recovered to
    Original Source. If not specified, all the configuration parameters will
    be retained.

    Attributes:
        resource_pool (RecoveryObjectIdentifier): Specifies the id of the resource pool to recover the SAN Volume
          to. This field can be specified for cases where the resource pool can be
          altered on the original source.
        rename_recovered_volume_params (RenameRecoveredVolumeParams):
            Specifies params to rename the recovered SAN volumes. If not
            specified, the original names of the volumes are preserved.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "resource_pool" : 'resourcePool' ,
        "rename_recovered_volume_params":'renameRecoveredVolumeParams'
    }

    def __init__(self,
                 resource_pool=None ,
                 rename_recovered_volume_params=None):
        """Constructor for the OriginalSourceConfig19 class"""

        # Initialize members of the class
        self.resource_pool = resource_pool
        self.rename_recovered_volume_params = rename_recovered_volume_params


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
        resource_pool = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(
            dictionary.get('resourcePool')) if dictionary.get('resourcePool') else None
        rename_recovered_volume_params = cohesity_management_sdk.models_v2.rename_recovered_volume_params.RenameRecoveredVolumeParams.from_dictionary(dictionary.get('renameRecoveredVolumeParams')) if dictionary.get('renameRecoveredVolumeParams') else None

        # Return an object of this model
        return cls(resource_pool,
                   rename_recovered_volume_params)