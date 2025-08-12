# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.smb_permission

class AliasSmbConfig(object):

    """Implementation of the 'AliasSmbConfig' model.

    Message defining SMB config for IRIS. SMB config contains SMB encryption
    flags, SMB discoverable flag and Share level permissions.

    Attributes:
        discovery_enabled (bool): Whether the share is discoverable.
        encryption_enabled (bool): Whether SMB encryption is enabled for this
            share. Encryption is supported only by SMB 3.x dialects. Dialects
            that do not support would still access data in unencrypted
            format.
        encryption_required (bool): Whether to enforce encryption for all the
            sessions for this view. When enabled all unencrypted sessions are
            disallowed.
        permissions (list of SMBPermission): Share level permissions.
        caching_enabled (bool): Indicate if offline file caching is supported
        super_user_sids (list of string): Specifies a list of super user sids.
        is_share_level_permission_empty (bool): Indicate if share level
            permission is cleared by user.
        oplock_enabled (bool): Indicate the operation lock is enabled by this
            view.
        continuous_availability (bool): Whether file open handles are persited
            to scribe to survive bridge process crash. When set to false, open
            handles will be kept in memory untill the current node has
            exclusive ticket for the entity handle. When the entity is opened
            from another node, the exclusive ticket would be revoked from the
            node. In revoke control flow, the current node would persist the
            state to scribe. On acquiring the exclusive ticket,another node
            would read the file open handles from scribe and resume the
            handling of operation.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "discovery_enabled":'discoveryEnabled',
        "encryption_enabled":'encryptionEnabled',
        "encryption_required":'encryptionRequired',
        "permissions":'permissions',
        "caching_enabled":'cachingEnabled',
        "super_user_sids":'superUserSids',
        "is_share_level_permission_empty":'isShareLevelPermissionEmpty',
        "oplock_enabled":'oplockEnabled',
        "continuous_availability":'continuousAvailability'
    }

    def __init__(self,
                 discovery_enabled=None,
                 encryption_enabled=None,
                 encryption_required=None,
                 permissions=None,
                 caching_enabled=None,
                 super_user_sids=None,
                 is_share_level_permission_empty=None,
                 oplock_enabled=None,
                 continuous_availability=None):
        """Constructor for the AliasSmbConfig class"""

        # Initialize members of the class
        self.discovery_enabled = discovery_enabled
        self.encryption_enabled = encryption_enabled
        self.encryption_required = encryption_required
        self.permissions = permissions
        self.caching_enabled = caching_enabled
        self.super_user_sids = super_user_sids
        self.is_share_level_permission_empty = is_share_level_permission_empty
        self.oplock_enabled = oplock_enabled
        self.continuous_availability = continuous_availability


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
        discovery_enabled = dictionary.get('discoveryEnabled')
        encryption_enabled = dictionary.get('encryptionEnabled')
        encryption_required = dictionary.get('encryptionRequired')
        permissions = None
        if dictionary.get("permissions") is not None:
            permissions = list()
            for structure in dictionary.get('permissions'):
                permissions.append(cohesity_management_sdk.models_v2.smb_permission.SMBPermission.from_dictionary(structure))
        super_user_sids = dictionary.get('superUserSids')
        caching_enabled = dictionary.get('cachingEnabled')
        is_share_level_permission_empty = dictionary.get('isShareLevelPermissionEmpty')
        oplock_enabled = dictionary.get('oplockEnabled')
        continuous_availability = dictionary.get('continuousAvailability')

        # Return an object of this model
        return cls(discovery_enabled,
                   encryption_enabled,
                   encryption_required,
                   permissions,
                   caching_enabled,
                   super_user_sids,
                   is_share_level_permission_empty,
                   oplock_enabled,
                   continuous_availability)


