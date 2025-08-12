# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.hyper_vdisk_filter_proto
import cohesity_management_sdk.models.source_app_params


class HyperVBackupSourceParams(object):

    """Implementation of the 'HyperVBackupSourceParams' model.

    Message to capture additional backup params for a Hyper-V type source.


    Attributes:
        hyperv_disk_exclusion_info (list of HyperVDiskFilterProto): List of Virtual Disk(s) to be excluded from the backup job for the source.
          Overrides the exclusion list requested (if any) through
          EnvBackupParams.HyperVBackupEnvParams.
        hyperv_disk_inclusion_info (list of HyperVDiskFilterProto): List of Virtual Disk(s) to be included in the backup job for the source.
          All other disks except these would be excluded.
          Overrides the inclusion/exclusion list requested (if any) through
          EnvBackupParams.HyperVBackupEnvParams.
        source_app_params (SourceAppParams): This message will capture params
            for applications that are running as part of the server.
    """


    # Create a mapping from Model property names to API property names
    _names = {
        "hyperv_disk_exclusion_info": 'hypervDiskExclusionInfo',
        "hyperv_disk_inclusion_info": 'hypervDiskInclusionInfo',
        "source_app_params":'sourceAppParams',
    }
    def __init__(self,
                 hyperv_disk_exclusion_info=None,
                 hyperv_disk_inclusion_info=None,
                 source_app_params=None,
            ):

        """Constructor for the HyperVBackupSourceParams class"""

        # Initialize members of the class
        self.hyperv_disk_exclusion_info = hyperv_disk_exclusion_info
        self.hyperv_disk_inclusion_info = hyperv_disk_inclusion_info
        self.source_app_params = source_app_params

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
        hyperv_disk_exclusion_info = None
        if dictionary.get('hypervDiskExclusionInfo') is not None:
            hyperv_disk_exclusion_info = list()
            for structure in dictionary.get('hypervDiskExclusionInfo'):
                hyperv_disk_exclusion_info.append(cohesity_management_sdk.models.hyper_vdisk_filter_proto.HyperVDiskFilterProto.from_dictionary(structure))
        hyperv_disk_inclusion_info = None
        if dictionary.get('hypervDiskInclusionInfo') is not None :
            hyperv_disk_inclusion_info = list()
            for structure in dictionary.get('hypervDiskInclusionInfo') :
                hyperv_disk_inclusion_info.append(
                    cohesity_management_sdk.models.hyper_vdisk_filter_proto.HyperVDiskFilterProto.from_dictionary(
                        structure))
        source_app_params = cohesity_management_sdk.models.source_app_params.SourceAppParams.from_dictionary(dictionary.get('sourceAppParams')) if dictionary.get('sourceAppParams') else None

        # Return an object of this model
        return cls(
            hyperv_disk_exclusion_info,
            hyperv_disk_inclusion_info,
            source_app_params
)