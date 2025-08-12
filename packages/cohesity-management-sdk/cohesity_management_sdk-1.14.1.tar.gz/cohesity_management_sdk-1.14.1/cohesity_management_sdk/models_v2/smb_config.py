# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.smb_permissions_information
import cohesity_management_sdk.models_v2.smb_permission
import cohesity_management_sdk.models_v2.view_share_permissions

class SmbConfig(object):

    """Implementation of the 'SmbConfig' model.

    Specifies the SMB config settings for this View.

    Attributes:
        enable_smb_view_discovery (bool): If set, it enables discovery of view
            for SMB.
        enable_smb_access_based_enumeration (bool): Specifies if access-based
            enumeration should be enabled. If 'true', only files and folders
            that the user has permissions to access are visible on the SMB
            share for that user.
        enable_smb_encryption (bool): Specifies the SMB encryption for the
            View. If set, it enables the SMB encryption for the View.
            Encryption is supported only by SMB 3.x dialects. Dialects that do
            not support would still access data in unencrypted format.
        enforce_smb_encryption (bool): Specifies the SMB encryption for all
            the sessions for the View. If set, encryption is enforced for all
            the sessions for the View. When enabled all future and existing
            unencrypted sessions are disallowed.
        enable_fast_durable_handle (bool): Specifies whether fast durable
            handle is enabled. If enabled, view open handle will be kept in
            memory, which results in a higher performance. But the handles
            cannot be recovered if node or service crashes.
        enable_smb_oplock (bool): Specifies whether SMB opportunistic lock is
            enabled.
        smb_permissions_info (SMBPermissionsInformation): Specifies
            information about SMB permissions.
        share_permissions (ViewSharePermissions): Specifies share level
            permissions of the view.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "enable_smb_view_discovery":'enableSmbViewDiscovery',
        "enable_smb_access_based_enumeration":'enableSmbAccessBasedEnumeration',
        "enable_smb_encryption":'enableSmbEncryption',
        "enforce_smb_encryption":'enforceSmbEncryption',
        "enable_fast_durable_handle":'enableFastDurableHandle',
        "enable_smb_oplock":'enableSmbOplock',
        "smb_permissions_info":'smbPermissionsInfo',
        "share_permissions":'sharePermissions'
    }

    def __init__(self,
                 enable_smb_view_discovery=None,
                 enable_smb_access_based_enumeration=None,
                 enable_smb_encryption=None,
                 enforce_smb_encryption=None,
                 enable_fast_durable_handle=None,
                 enable_smb_oplock=None,
                 smb_permissions_info=None,
                 share_permissions=None):
        """Constructor for the SmbConfig class"""

        # Initialize members of the class
        self.enable_smb_view_discovery = enable_smb_view_discovery
        self.enable_smb_access_based_enumeration = enable_smb_access_based_enumeration
        self.enable_smb_encryption = enable_smb_encryption
        self.enforce_smb_encryption = enforce_smb_encryption
        self.enable_fast_durable_handle = enable_fast_durable_handle
        self.enable_smb_oplock = enable_smb_oplock
        self.smb_permissions_info = smb_permissions_info
        self.share_permissions = share_permissions


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
        enable_smb_view_discovery = dictionary.get('enableSmbViewDiscovery')
        enable_smb_access_based_enumeration = dictionary.get('enableSmbAccessBasedEnumeration')
        enable_smb_encryption = dictionary.get('enableSmbEncryption')
        enforce_smb_encryption = dictionary.get('enforceSmbEncryption')
        enable_fast_durable_handle = dictionary.get('enableFastDurableHandle')
        enable_smb_oplock = dictionary.get('enableSmbOplock')
        smb_permissions_info = cohesity_management_sdk.models_v2.smb_permissions_information.SMBPermissionsInformation.from_dictionary(dictionary.get('smbPermissionsInfo')) if dictionary.get('smbPermissionsInfo') else None
        share_permissions = cohesity_management_sdk.models_v2.view_share_permissions.ViewSharePermissions.from_dictionary(dictionary.get('sharePermissions')) if dictionary.get('sharePermissions') else None

        # Return an object of this model
        return cls(enable_smb_view_discovery,
                   enable_smb_access_based_enumeration,
                   enable_smb_encryption,
                   enforce_smb_encryption,
                   enable_fast_durable_handle,
                   enable_smb_oplock,
                   smb_permissions_info,
                   share_permissions)


