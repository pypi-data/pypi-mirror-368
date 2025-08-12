# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.smb_permission
import cohesity_management_sdk.models_v2.subnet

class FilerAuditLogConfigs(object):

    """Implementation of the 'FilerAuditLogConfigs' model.

    Specifies the filer audit log configs.

    Attributes:
        share_permissions (list of SMBPermission): Specifies a list of share
            level permissions.
        subnet_whitelist (list of Subnet): Specifies a list of Subnets with IP
            addresses that have permissions to access a Cohesity View
            containing filer audit logs.
        override_global_subnet_whitelist (bool): Specifies whether view level
            client subnet whitelist overrides cluster and global setting.
        smb_mount_paths (list of string): Specifies a list of SMB mount paths
            of a Cohesity View containing filer audit logs.
        nfs_mount_path (string): Specifies a NFS mount path of a Cohesity View
            containing filer audit logs.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "share_permissions":'sharePermissions',
        "subnet_whitelist":'subnetWhitelist',
        "override_global_subnet_whitelist":'overrideGlobalSubnetWhitelist',
        "smb_mount_paths":'smbMountPaths',
        "nfs_mount_path":'nfsMountPath'
    }

    def __init__(self,
                 share_permissions=None,
                 subnet_whitelist=None,
                 override_global_subnet_whitelist=None,
                 smb_mount_paths=None,
                 nfs_mount_path=None):
        """Constructor for the FilerAuditLogConfigs class"""

        # Initialize members of the class
        self.share_permissions = share_permissions
        self.subnet_whitelist = subnet_whitelist
        self.override_global_subnet_whitelist = override_global_subnet_whitelist
        self.smb_mount_paths = smb_mount_paths
        self.nfs_mount_path = nfs_mount_path


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
        share_permissions = None
        if dictionary.get("sharePermissions") is not None:
            share_permissions = list()
            for structure in dictionary.get('sharePermissions'):
                share_permissions.append(cohesity_management_sdk.models_v2.smb_permission.SMBPermission.from_dictionary(structure))
        subnet_whitelist = None
        if dictionary.get("subnetWhitelist") is not None:
            subnet_whitelist = list()
            for structure in dictionary.get('subnetWhitelist'):
                subnet_whitelist.append(cohesity_management_sdk.models_v2.subnet.Subnet.from_dictionary(structure))
        override_global_subnet_whitelist = dictionary.get('overrideGlobalSubnetWhitelist')
        smb_mount_paths = dictionary.get('smbMountPaths')
        nfs_mount_path = dictionary.get('nfsMountPath')

        # Return an object of this model
        return cls(share_permissions,
                   subnet_whitelist,
                   override_global_subnet_whitelist,
                   smb_mount_paths,
                   nfs_mount_path)


