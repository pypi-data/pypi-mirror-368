# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recovery_object_identifier
import cohesity_management_sdk.models_v2.recover_or_clone_vm_s_rename_config_params

class RecoverPureVolumeNewSourceConfig(object):

    """Implementation of the 'Recover Pure Volume New Source Config.' model.

    Specifies the new destination Source configuration where the Pure volume
    will be recovered.

    Attributes:
        source (RecoveryObjectIdentifier): Specifies the id of the new target parent source to
            recover the Pure SAN Volume to. This field must be specified if
            recoverToNewSource is true.
        resource_pool (RecoveryObjectIdentifier): Specifies the id of the resource pool to recover the Pure SAN
          Volume to. This field must be specified if recoverToNewSource is true.
        rename_recovered_volume_params (RecoverOrCloneVMsRenameConfigparams):
            Specifies params to rename the recovered SAN volumes. If not
            specified, the original names of the volumes are preserved.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source":'source',
        "resource_pool":'resourcePool',
        "rename_recovered_volume_params":'renameRecoveredVolumeParams'
    }

    def __init__(self,
                 source=None,
                 resource_pool=None,
                 rename_recovered_volume_params=None):
        """Constructor for the RecoverPureVolumeNewSourceConfig class"""

        # Initialize members of the class
        self.source = source
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
        source = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None
        resource_pool = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(
            dictionary.get('resourcePool')) if dictionary.get('resourcePool') else None
        rename_recovered_volume_params = cohesity_management_sdk.models_v2.recover_or_clone_vm_s_rename_config_params.RecoverOrCloneVMsRenameConfigparams.from_dictionary(dictionary.get('renameRecoveredVolumeParams')) if dictionary.get('renameRecoveredVolumeParams') else None

        # Return an object of this model
        return cls(source,
                   resource_pool,
                   rename_recovered_volume_params)