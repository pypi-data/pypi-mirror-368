# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.hyper_vdisk_filter_proto

class HyperVBackupEnvParams(object):

    """Implementation of the 'HyperVBackupEnvParams' model.

    Message to capture any additional backup params for a HyperV environment.

    Attributes:
        allow_crash_consistent_snapshot (bool): Whether to fallback to take a
            crash-consistent snapshot incase taking an app-consistent snapshot
            fails.
        backup_job_type (int): The type of backup job to use. Default is to
            auto-detect the best type to use based on the VMs to backup. End
            user may select RCT or VSS also.
        hyperv_disk_exclusion_info (list of HyperVDiskFilterProto): List of
            Virtual Disk(s) to be excluded from the backup job. These disks
            will be excluded for all VMs in this environment unless overriden by the
            disk exclusion list from BackupSourceParams.HyperVBackupSourceParams.
        hyperv_disk_inclusion_info (list of HyperVDiskFilterProto): List of
            Virtual Disk(s) to be included in the backup job for the source.
            These disks will be included for all VMs in this environment and all other
            disks will be excluded.
            It can be overriden by the disk exclusion/inclusion list from
            BackupSourceParams.HyperVBackupSourceParams
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "allow_crash_consistent_snapshot":'allowCrashConsistentSnapshot',
        "backup_job_type":'backupJobType',
        "hyperv_disk_exclusion_info": 'hypervDiskExclusionInfo',
        "hyperv_disk_inclusion_info": 'hypervDiskInclusionInfo'
    }

    def __init__(self,
                 allow_crash_consistent_snapshot=None,
                 backup_job_type=None,
                 hyperv_disk_exclusion_info=None,
                 hyperv_disk_inclusion_info=None):
        """Constructor for the HyperVBackupEnvParams class"""

        # Initialize members of the class
        self.allow_crash_consistent_snapshot = allow_crash_consistent_snapshot
        self.backup_job_type = backup_job_type
        self.hyperv_disk_exclusion_info = hyperv_disk_exclusion_info
        self.hyperv_disk_inclusion_info = hyperv_disk_inclusion_info


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
        allow_crash_consistent_snapshot = dictionary.get('allowCrashConsistentSnapshot')
        backup_job_type = dictionary.get('backupJobType')
        hyperv_disk_exclusion_info = None
        if dictionary.get("hypervDiskExclusionInfo") is not None:
            hyperv_disk_exclusion_info = list()
            for structure in dictionary.get('hypervDiskExclusionInfo'):
                hyperv_disk_exclusion_info.append(cohesity_management_sdk.models.hyper_vdisk_filter_proto.HyperVDiskFilterProto.from_dictionary(structure))

        hyperv_disk_inclusion_info = None
        if dictionary.get("hypervDiskInclusionInfo") is not None:
            hyperv_disk_inclusion_info = list()
            for structure in dictionary.get('hypervDiskInclusionInfo'):
                hyperv_disk_inclusion_info.append(cohesity_management_sdk.models.hyper_vdisk_filter_proto.HyperVDiskFilterProto.from_dictionary(structure))

        # Return an object of this model
        return cls(allow_crash_consistent_snapshot,
                   backup_job_type,
                   hyperv_disk_exclusion_info,
                   hyperv_disk_inclusion_info)


