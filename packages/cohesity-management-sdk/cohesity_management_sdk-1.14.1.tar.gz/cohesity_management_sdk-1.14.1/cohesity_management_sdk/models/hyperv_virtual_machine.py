# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.virtual_disk_basic_info

class HypervVirtualMachine(object):

    """Implementation of the 'HypervVirtualMachine' model.

    Specifies information about a VirtualMachine Object in HyperV
    environment.

    Attributes:
        is_highly_available (bool): Specifies whether the VM is Highly
            Available or not.
        version (string): Specifies the version of the VM. For example, 8.0,
            5.0 etc.
        virtual_disks (list of VirtualDiskBasicInfo): Specifies an array of
            virtual disks that are part of the Virtual Machine.
          This is populated for entities of type 'kVirtualMachine'
        vm_backup_status (VmBackupStatusEnum): Specifies the status of the VM
            for backup purpose. overrideDescription: true Specifies the backup
            status of a HyperV Virtual Machine object. 'kSupported' indicates
            the agent on the VM can do backup. 'kUnsupportedConfig' indicates
            the agent on the VM cannot do backup. 'kMissing' indicates the VM
            is not found in SCVMM.
        vm_backup_type (VmBackupTypeEnum): Specifies the type of backup
            supported by the VM. overrideDescription: true Specifies the type
            of an HyperV datastore object. 'kRctBackup' indicates backup is
            done using RCT/checkpoints. 'kVssBackup' indicates backup is done
            using VSS.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "is_highly_available":'isHighlyAvailable',
        "version":'version',
        "virtual_disks": 'virtualDisks',
        "vm_backup_status":'vmBackupStatus',
        "vm_backup_type":'vmBackupType'
    }

    def __init__(self,
                 is_highly_available=None,
                 version=None,
                 virtual_disks=None,
                 vm_backup_status=None,
                 vm_backup_type=None):
        """Constructor for the HypervVirtualMachine class"""

        # Initialize members of the class
        self.is_highly_available = is_highly_available
        self.version = version
        self.virtual_disks = virtual_disks
        self.vm_backup_status = vm_backup_status
        self.vm_backup_type = vm_backup_type


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
        is_highly_available = dictionary.get('isHighlyAvailable')
        version = dictionary.get('version')
        virtual_disks = None
        if dictionary.get("virtualDisks") is not None:
            virtual_disks = list()
            for structure in dictionary.get('virtualDisks'):
                virtual_disks.append(cohesity_management_sdk.models.virtual_disk_basic_info.VirtualDiskBasicInfo.from_dictionary(structure))
        vm_backup_status = dictionary.get('vmBackupStatus')
        vm_backup_type = dictionary.get('vmBackupType')

        # Return an object of this model
        return cls(is_highly_available,
                   version,
                   virtual_disks,
                   vm_backup_status,
                   vm_backup_type)


