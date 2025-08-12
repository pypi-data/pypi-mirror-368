# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.smb_mount_credentials
import cohesity_management_sdk.models_v2.universal_id
import cohesity_management_sdk.models_v2.nas_source_and_protection_throttling_configuration

class GenericNASProtectionSource(object):

    """Implementation of the 'Generic NAS Protection Source.' model.

    Specifies parameters to register GenericNas MountPoint.

    Attributes:
        mount_point (string): Specifies the MountPoint for Generic NAS
            Source.
        mode (Mode4Enum): Specifies the mode of the source. 'kNfs3' indicates
            NFS mode. 'kCifs1' indicates SMB mode.
        description (string): Specifies the Description for Generic NAS
            Source.
        skip_validation (bool): Specifies if validation has to be skipped
            while registering the mount point.
        smb_mount_credentials (SMBMountCredentials): Specifies the credentials
            to mount a view.
        throttling_config (NasSourceAndProtectionThrottlingConfiguration):
            Specifies the source throttling parameters to be used during full
            or incremental backup of the NAS source.
        uid (UniversalId): Specifies a distinct value that's unique to a source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mount_point":'mountPoint',
        "mode":'mode',
        "description":'description',
        "skip_validation":'skipValidation',
        "smb_mount_credentials":'smbMountCredentials',
        "throttling_config":'throttlingConfig',
        "uid":'uid'
    }

    def __init__(self,
                 mount_point=None,
                 mode=None,
                 description=None,
                 skip_validation=None,
                 smb_mount_credentials=None,
                 throttling_config=None,
                 uid=None):
        """Constructor for the GenericNASProtectionSource class"""

        # Initialize members of the class
        self.mount_point = mount_point
        self.mode = mode
        self.description = description
        self.skip_validation = skip_validation
        self.smb_mount_credentials = smb_mount_credentials
        self.throttling_config = throttling_config
        self.uid = uid


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
        mount_point = dictionary.get('mountPoint')
        mode = dictionary.get('mode')
        description = dictionary.get('description')
        skip_validation = dictionary.get('skipValidation')
        smb_mount_credentials = cohesity_management_sdk.models_v2.smb_mount_credentials.SMBMountCredentials.from_dictionary(dictionary.get('smbMountCredentials')) if dictionary.get('smbMountCredentials') else None
        throttling_config = cohesity_management_sdk.models_v2.nas_source_and_protection_throttling_configuration.NasSourceAndProtectionThrottlingConfiguration.from_dictionary(dictionary.get('throttlingConfig')) if dictionary.get('throttlingConfig') else None
        uid = cohesity_management_sdk.models_v2.universal_id.UniversalId.from_dictionary(dictionary.get('uid')) if dictionary.get('uid') else None

        # Return an object of this model
        return cls(mount_point,
                   mode,
                   description,
                   skip_validation,
                   smb_mount_credentials,
                   throttling_config,
                   uid)