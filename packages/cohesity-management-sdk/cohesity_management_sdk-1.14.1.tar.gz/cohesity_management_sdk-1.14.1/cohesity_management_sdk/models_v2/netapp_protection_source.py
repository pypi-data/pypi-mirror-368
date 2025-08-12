# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.credentials
import cohesity_management_sdk.models_v2.smb_mount_credentials
import cohesity_management_sdk.models_v2.filter_ip_configuration
import cohesity_management_sdk.models_v2.nas_source_and_protection_throttling_configuration
import cohesity_management_sdk.models_v2.storage_snapshot_mgmtthrottling_policy_config

class NetappProtectionSource(object):

    """Implementation of the 'Netapp Protection Source.' model.

    Specifies parameters to register an Netapp Source.

    Attributes:
        source_type (SourceTypeEnum): Specifies the Netapp source type. Can be either
            kCluster or kVServer (SVM).
        endpoint (string): Specifies the Hostname or IP Address Endpoint for
            the Netapp Source.
        credentials (Credentials): Specifies the object to hold username and
            password.
        back_up_smb_volumes (bool): Specifies whether or not to back up SMB
            Volumes.
        storage_array_snapshot_config (StorageSnapshotMgmtthrottlingPolicyConfig): Specifies the storage array snapshot management configuration.
        storage_array_snapshot_enabled (bool): Specifies if storage array snapshot is enabled or not in the
          Source.
        smb_credentials (SMBMountCredentials): Specifies the credentials to
            mount a view.
        filter_ip_config (FilterIPConfiguration): Specifies the list of IP
            addresses that are allowed or denied during recovery. Allowed IPs
            and Denied IPs cannot be used together.
        throttling_config (NasSourceAndProtectionThrottlingConfiguration):
            Specifies the source throttling parameters to be used during full
            or incremental backup of the NAS source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source_type":'sourceType',
        "endpoint":'endpoint',
        "credentials":'credentials',
        "back_up_smb_volumes":'backUpSMBVolumes',
        "storage_array_snapshot_config":'storageArraySnapshotConfig',
        "storage_array_snapshot_enabled":'storageArraySnapshotEnabled',
        "smb_credentials":'smbCredentials',
        "filter_ip_config":'filterIpConfig',
        "throttling_config":'throttlingConfig'
    }

    def __init__(self,
                 source_type=None,
                 endpoint=None,
                 credentials=None,
                 back_up_smb_volumes=None,
                 storage_array_snapshot_config=None,
                 storage_array_snapshot_enabled=None,
                 smb_credentials=None,
                 filter_ip_config=None,
                 throttling_config=None):
        """Constructor for the NetappProtectionSource class"""

        # Initialize members of the class
        self.source_type = source_type
        self.endpoint = endpoint
        self.credentials = credentials
        self.back_up_smb_volumes = back_up_smb_volumes
        self.storage_array_snapshot_config = storage_array_snapshot_config
        self.storage_array_snapshot_enabled = storage_array_snapshot_enabled
        self.smb_credentials = smb_credentials
        self.filter_ip_config = filter_ip_config
        self.throttling_config = throttling_config


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
        source_type = dictionary.get('sourceType')
        endpoint = dictionary.get('endpoint')
        credentials = cohesity_management_sdk.models_v2.credentials.Credentials.from_dictionary(dictionary.get('credentials')) if dictionary.get('credentials') else None
        back_up_smb_volumes = dictionary.get('backUpSMBVolumes')
        storage_array_snapshot_config = cohesity_management_sdk.models_v2.storage_snapshot_mgmtthrottling_policy_config.StorageSnapshotMgmtthrottlingPolicyConfig.from_dictionary(
            dictionary.get('storageArraySnapshotConfig')) if dictionary.get('storageArraySnapshotConfig') else None
        storage_array_snapshot_enabled = dictionary.get('storageArraySnapshotEnabled')
        smb_credentials = cohesity_management_sdk.models_v2.smb_mount_credentials.SMBMountCredentials.from_dictionary(dictionary.get('smbCredentials')) if dictionary.get('smbCredentials') else None
        filter_ip_config = cohesity_management_sdk.models_v2.filter_ip_configuration.FilterIPConfiguration.from_dictionary(dictionary.get('filterIpConfig')) if dictionary.get('filterIpConfig') else None
        throttling_config = cohesity_management_sdk.models_v2.nas_source_and_protection_throttling_configuration.NasSourceAndProtectionThrottlingConfiguration.from_dictionary(dictionary.get('throttlingConfig')) if dictionary.get('throttlingConfig') else None

        # Return an object of this model
        return cls(source_type,
                   endpoint,
                   credentials,
                   back_up_smb_volumes,
                   storage_array_snapshot_config,
                   storage_array_snapshot_enabled,
                   smb_credentials,
                   filter_ip_config,
                   throttling_config)