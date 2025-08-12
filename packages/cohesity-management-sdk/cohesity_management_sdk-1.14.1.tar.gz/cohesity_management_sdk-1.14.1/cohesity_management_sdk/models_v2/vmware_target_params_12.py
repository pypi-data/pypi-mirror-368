# -*- coding: utf-8 -*-


class VmwareTargetParams12(object):

    """Implementation of the 'VmwareTargetParams11' model.

    Specifies the params for recovering to a VMware target.

    Attributes:
        datastore_ids (long|int):  Specifies Datastore Ids, if the restore is to alternate location.
        attempt_differential_restore (bool): Specifies whether to attempt differential restore.
        enable_copy_recovery (bool): Specifies whether to perform copy recovery or not.
        is_on_prem_deploy (bool): Specifies whether a task in on prem deploy or not.
        overwrite_existing_vm (bool): Specifies whether to overwrite the VM at the target location.
        power_off_and_rename_existing_vm (bool): Specifies whether to power off and mark the VM at the target
          location as deprecated.
        resource_pool_id (long|int): Specifies if the restore is to alternate location.
        preserve_tags_during_clone (bool): Whether to preserve tags for the
            clone op.
        target_data_store_id (long|int): Specifies the folder where the restore datastore should be created.
        target_vm_folder_id (long|int):  Specifies the folder ID where the VMs should be created.
    """


    # Create a mapping from Model property names to API property names
    _names = {
        "datastore_ids":'datastoreIds',
        "attempt_differential_restore":'attemptDifferentialRestore',
        "enable_copy_recovery":'enableCopyRecovery',
        "is_on_prem_deploy":'isOnPremDeploy',
        "overwrite_existing_vm":'overwriteExistingVm',
        "power_off_and_rename_existing_vm":'powerOffAndRenameExistingVm',
        "resource_pool_id":'resourcePoolId',
        "preserve_tags_during_clone":'preserveTagsDuringClone',
        "target_data_store_id":'targetDataStoreId',
        "target_vm_folder_id":'targetVMFolderId'
    }
    def __init__(self,
                 datastore_ids=None,
                 attempt_differential_restore=None,
                 enable_copy_recovery=None,
                 is_on_prem_deploy=None,
                 overwrite_existing_vm=None,
                 power_off_and_rename_existing_vm=None,
                 resource_pool_id=None,
                 preserve_tags_during_clone=None,
                 target_data_store_id=None,
                 target_vm_folder_id=None
            ):

        """Constructor for the VMwareTargetParams12 class"""

        # Initialize members of the class
        self.datastore_ids = datastore_ids
        self.attempt_differential_restore = attempt_differential_restore
        self.enable_copy_recovery = enable_copy_recovery
        self.is_on_prem_deploy = is_on_prem_deploy
        self.overwrite_existing_vm = overwrite_existing_vm
        self.power_off_and_rename_existing_vm = power_off_and_rename_existing_vm
        self.resource_pool_id = resource_pool_id
        self.preserve_tags_during_clone = preserve_tags_during_clone
        self.target_data_store_id = target_data_store_id
        self.target_vm_folder_id = target_vm_folder_id


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
        datastore_ids = dictionary.get('datastoreIds')
        attempt_differential_restore = dictionary.get('attemptDifferentialRestore')
        enable_copy_recovery = dictionary.get('enableCopyRecovery')
        is_on_prem_deploy = dictionary.get('isOnPremDeploy')
        overwrite_existing_vm = dictionary.get('overwriteExistingVm')
        power_off_and_rename_existing_vm = dictionary.get('powerOffAndRenameExistingVm')
        resource_pool_id = dictionary.get('resourcePoolId')
        preserve_tags_during_clone = dictionary.get('preserveTagsDuringClone')
        target_data_store_id = dictionary.get('targetDataStoreId')
        target_vm_folder_id = dictionary.get('targetVMFolderId')


        # Return an object of this model
        return cls(datastore_ids,
                   attempt_differential_restore,
                   enable_copy_recovery,
                   is_on_prem_deploy,
                   overwrite_existing_vm,
                   power_off_and_rename_existing_vm,
                   resource_pool_id,
                   preserve_tags_during_clone,
                   target_data_store_id,
                   target_vm_folder_id)