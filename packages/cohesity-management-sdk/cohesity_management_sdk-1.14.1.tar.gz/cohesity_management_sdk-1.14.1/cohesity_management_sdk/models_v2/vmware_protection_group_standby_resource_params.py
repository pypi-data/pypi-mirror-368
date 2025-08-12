# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.rename_restored_object_params
import cohesity_management_sdk.models_v2.network_config_6

class VmwareProtectionGroupStandbyResourceParams(object):

    """Implementation of the 'VmwareProtectionGroupStandbyResourceParams' model.

    VMware protection group standby resource params which will be used to
    create standby VM entity for backup entity.

    Attributes:
        recovery_point_objective_secs (long|int): Specifies the recovery point
            objective time user expects for this standby resource.
        rename_restored_object_params (RenameRestoredObjectParams): Specifies
            params to rename the standby resource.
        parent_object_id (long|int): Specifies the object id for parent
            vCenter source where this standby resource should be created.
        target_folder_object_id (long|int): Specifies the object id for target
            vm folder where this standby resource should be created.
        target_datastore_folder_object_id (long|int): Specifies the object id
            for target datastore folder where disks for this standby resource
            should be placed.
        resource_pool_object_id (long|int): Specifies the object id for
            resource pool where this standby resource should be created.
        datastore_object_ids (list of long|int): Specifies the list of IDs of
            the datastore objects where this standby resource should be
            created.
        network_config (NetworkConfig6): Specifies the networking
            configuration to be applied to this standby resource.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_point_objective_secs":'recoveryPointObjectiveSecs',
        "rename_restored_object_params":'renameRestoredObjectParams',
        "parent_object_id":'parentObjectId',
        "target_folder_object_id":'targetFolderObjectId',
        "target_datastore_folder_object_id":'targetDatastoreFolderObjectId',
        "resource_pool_object_id":'resourcePoolObjectId',
        "datastore_object_ids":'datastoreObjectIds',
        "network_config":'networkConfig'
    }

    def __init__(self,
                 recovery_point_objective_secs=None,
                 rename_restored_object_params=None,
                 parent_object_id=None,
                 target_folder_object_id=None,
                 target_datastore_folder_object_id=None,
                 resource_pool_object_id=None,
                 datastore_object_ids=None,
                 network_config=None):
        """Constructor for the VmwareProtectionGroupStandbyResourceParams class"""

        # Initialize members of the class
        self.recovery_point_objective_secs = recovery_point_objective_secs
        self.rename_restored_object_params = rename_restored_object_params
        self.parent_object_id = parent_object_id
        self.target_folder_object_id = target_folder_object_id
        self.target_datastore_folder_object_id = target_datastore_folder_object_id
        self.resource_pool_object_id = resource_pool_object_id
        self.datastore_object_ids = datastore_object_ids
        self.network_config = network_config


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
        recovery_point_objective_secs = dictionary.get('recoveryPointObjectiveSecs')
        rename_restored_object_params = cohesity_management_sdk.models_v2.rename_restored_object_params.RenameRestoredObjectParams.from_dictionary(dictionary.get('renameRestoredObjectParams')) if dictionary.get('renameRestoredObjectParams') else None
        parent_object_id = dictionary.get('parentObjectId')
        target_folder_object_id = dictionary.get('targetFolderObjectId')
        target_datastore_folder_object_id = dictionary.get('targetDatastoreFolderObjectId')
        resource_pool_object_id = dictionary.get('resourcePoolObjectId')
        datastore_object_ids = dictionary.get('datastoreObjectIds')
        network_config = cohesity_management_sdk.models_v2.network_config_6.NetworkConfig6.from_dictionary(dictionary.get('networkConfig')) if dictionary.get('networkConfig') else None

        # Return an object of this model
        return cls(recovery_point_objective_secs,
                   rename_restored_object_params,
                   parent_object_id,
                   target_folder_object_id,
                   target_datastore_folder_object_id,
                   resource_pool_object_id,
                   datastore_object_ids,
                   network_config)


