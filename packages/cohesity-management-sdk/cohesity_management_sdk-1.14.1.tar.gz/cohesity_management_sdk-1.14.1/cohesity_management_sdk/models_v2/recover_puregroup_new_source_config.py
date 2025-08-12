# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_or_clone_vm_s_rename_config_params
import cohesity_management_sdk.models_v2.recovery_object_identifier

class RecoverPuregroupNewSourceConfig(object):

    """Implementation of the 'RecoverPuregroupNewSourceConfig' model.

    Specifies the new destination Source configuration parameters where the
    Pure volume will be recovered. This is mandatory if recoverToNewSource is
    set to true.

    Attributes:
        resource_pool (RecoveryObjectIdentifier): Specifies the id of the resource pool to recover the Pure SAN
          Volume to. This field must be specified if recoverToNewSource is true.
        source (RecoveryObjectIdentifier): Specifies the id of the new target parent source to
            recover the Pure SAN Volume to. This field must be specified if
            recoverToNewSource is true.
        rename_recovered_group_params (RecoverOrCloneVMsRenameConfigparams):
            Specifies params to rename the recovered SAN volumes. If not
            specified, the original names of the volumes are preserved.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "resource_pool":'resourcePool',
        "source":'source',
        "rename_recovered_group_params":'renameRecoveredGroupParams'
    }

    def __init__(self,
                 resource_pool=None,
                 source=None,
                 rename_recovered_group_params=None):
        """Constructor for the RecoverPuregroupNewSourceConfig class"""

        # Initialize members of the class
        self.resource_pool = resource_pool
        self.source = source
        self.rename_recovered_group_params = rename_recovered_group_params


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
        source = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None
        rename_recovered_group_params = cohesity_management_sdk.models_v2.recover_or_clone_vm_s_rename_config_params.RecoverOrCloneVMsRenameConfigparams.from_dictionary(dictionary.get('renameRecoveredGroupParams')) if dictionary.get('renameRecoveredGroupParams') else None

        # Return an object of this model
        return cls(resource_pool,
                   source,
                   rename_recovered_group_params)