# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models_v2.hyperv_disk_information

class HypervEnvJobParams(object):
    """Implementation of the 'HypervEnvJobParams' model.

    Specifies job parameters applicable for all 'kHyperV' Environment type Protection Sources in a Protection Job.

    Attributes:
        exclude_disks (list of HypervDiskInformation): Specifies a list of disks to exclude from being protected for the object/vm.
        fallback_to_crash_consistent (bool): If true, takes a crash-consistent snapshot when app-consistent snapshot fails. Otherwise, the snapshot attempt is marked failed.
        include_disks (list of HypervDiskInformation): Specifies a list of disks to included in the protection for the object/vm.
        protection_type (ProtectionType5Enum): Specifies the Protection Group type. If not specified, then backup method is auto determined. Specifying RCT will forcibly use RCT backup for all VMs in this Protection Group. Available only for VMs with hardware version 8.0 and above, but is more efficient. Specifying VSS will forcibly use VSS backup for all VMs in this Protection Group. Available for VMs with hardware version 5.0 and above, but is slower than RCT backup.
    """

    _names = {
        "exclude_disks":"excludeDisks",
        "fallback_to_crash_consistent":"fallbackToCrashConsistent",
        "include_disks":"includeDisks",
        "protection_type":"protectionType",
    }

    def __init__(self,
                 exclude_disks=None,
                 fallback_to_crash_consistent=None,
                 include_disks=None,
                 protection_type=None):
        """Constructor for the HypervEnvJobParams class"""

        self.exclude_disks = exclude_disks
        self.fallback_to_crash_consistent = fallback_to_crash_consistent
        self.include_disks = include_disks
        self.protection_type = protection_type


    @classmethod
    def from_dictionary(cls, dictionary):
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

        exclude_disks = None
        if dictionary.get('excludeDisks') is not None:
            exclude_disks = list()
            for structure in dictionary.get('excludeDisks'):
                exclude_disks.append(cohesity_management_sdk.models_v2.hyperv_disk_information.HypervDiskInformation.from_dictionary(structure))
        fallback_to_crash_consistent = dictionary.get('fallbackToCrashConsistent')
        include_disks = None
        if dictionary.get('includeDisks') is not None:
            include_disks = list()
            for structure in dictionary.get('includeDisks'):
                include_disks.append(cohesity_management_sdk.models_v2.hyperv_disk_information.HypervDiskInformation.from_dictionary(structure))
        protection_type = dictionary.get('protectionType')

        return cls(
            exclude_disks,
            fallback_to_crash_consistent,
            include_disks,
            protection_type
        )