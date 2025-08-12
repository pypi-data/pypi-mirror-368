# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.credentials
import cohesity_management_sdk.models_v2.smb_mount_credentials
import cohesity_management_sdk.models_v2.filter_ip_configuration
import cohesity_management_sdk.models_v2.nas_source_and_protection_throttling_configuration

class IsilonProtectionSource(object):

    """Implementation of the 'Isilon Protection Source.' model.

    Specifies parameters to register an Isilon Source.

    Attributes:
        endpoint (string): Specifies the IP Address Endpoint for the Isilon
            Source.
        credentials (Credentials): Specifies the object to hold username and
            password.
        back_up_smb_volumes (bool): Specifies whether or not to back up SMB
            Volumes.
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
        "endpoint":'endpoint',
        "credentials":'credentials',
        "back_up_smb_volumes":'backUpSMBVolumes',
        "smb_credentials":'smbCredentials',
        "filter_ip_config":'filterIpConfig',
        "throttling_config":'throttlingConfig'
    }

    def __init__(self,
                 endpoint=None,
                 credentials=None,
                 back_up_smb_volumes=None,
                 smb_credentials=None,
                 filter_ip_config=None,
                 throttling_config=None):
        """Constructor for the IsilonProtectionSource class"""

        # Initialize members of the class
        self.endpoint = endpoint
        self.credentials = credentials
        self.back_up_smb_volumes = back_up_smb_volumes
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
        endpoint = dictionary.get('endpoint')
        credentials = cohesity_management_sdk.models_v2.credentials.Credentials.from_dictionary(dictionary.get('credentials')) if dictionary.get('credentials') else None
        back_up_smb_volumes = dictionary.get('backUpSMBVolumes')
        smb_credentials = cohesity_management_sdk.models_v2.smb_mount_credentials.SMBMountCredentials.from_dictionary(dictionary.get('smbCredentials')) if dictionary.get('smbCredentials') else None
        filter_ip_config = cohesity_management_sdk.models_v2.filter_ip_configuration.FilterIPConfiguration.from_dictionary(dictionary.get('filterIpConfig')) if dictionary.get('filterIpConfig') else None
        throttling_config = cohesity_management_sdk.models_v2.nas_source_and_protection_throttling_configuration.NasSourceAndProtectionThrottlingConfiguration.from_dictionary(dictionary.get('throttlingConfig')) if dictionary.get('throttlingConfig') else None

        # Return an object of this model
        return cls(endpoint,
                   credentials,
                   back_up_smb_volumes,
                   smb_credentials,
                   filter_ip_config,
                   throttling_config)


