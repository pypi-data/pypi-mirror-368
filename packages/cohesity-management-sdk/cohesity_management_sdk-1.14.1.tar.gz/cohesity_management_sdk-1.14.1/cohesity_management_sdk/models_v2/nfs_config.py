# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.nfs_squash_specifies_the_squash_config_for_client_subnet_whitelist
import cohesity_management_sdk.models_v2.nfs_root_permissions

class NfsConfig(object):

    """Implementation of the 'NfsConfig' model.

    Specifies the NFS config settings for this View.

    Attributes:
        enable_nfs_view_discovery (bool): If set, it enables discovery of view
            for NFS.
        nfs_all_squash
            (NfsSquashSpecifiesTheSquashConfigForClientSubnetWhitelist): TODO:
            type description here.
        nfs_root_permissions (NfsRootPermissions): Specifies the config of NFS
            root permission of a view file system.
        nfs_root_squash
            (NfsSquashSpecifiesTheSquashConfigForClientSubnetWhitelist): TODO:
            type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "enable_nfs_view_discovery":'enableNfsViewDiscovery',
        "nfs_all_squash":'nfsAllSquash',
        "nfs_root_permissions":'nfsRootPermissions',
        "nfs_root_squash":'nfsRootSquash'
    }

    def __init__(self,
                 enable_nfs_view_discovery=None,
                 nfs_all_squash=None,
                 nfs_root_permissions=None,
                 nfs_root_squash=None):
        """Constructor for the NfsConfig class"""

        # Initialize members of the class
        self.enable_nfs_view_discovery = enable_nfs_view_discovery
        self.nfs_all_squash = nfs_all_squash
        self.nfs_root_permissions = nfs_root_permissions
        self.nfs_root_squash = nfs_root_squash


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
        enable_nfs_view_discovery = dictionary.get('enableNfsViewDiscovery')
        nfs_all_squash = cohesity_management_sdk.models_v2.nfs_squash_specifies_the_squash_config_for_client_subnet_whitelist.NfsSquashSpecifiesTheSquashConfigForClientSubnetWhitelist.from_dictionary(dictionary.get('nfsAllSquash')) if dictionary.get('nfsAllSquash') else None
        nfs_root_permissions = cohesity_management_sdk.models_v2.nfs_root_permissions.NfsRootPermissions.from_dictionary(dictionary.get('nfsRootPermissions')) if dictionary.get('nfsRootPermissions') else None
        nfs_root_squash = cohesity_management_sdk.models_v2.nfs_squash_specifies_the_squash_config_for_client_subnet_whitelist.NfsSquashSpecifiesTheSquashConfigForClientSubnetWhitelist.from_dictionary(dictionary.get('nfsRootSquash')) if dictionary.get('nfsRootSquash') else None

        # Return an object of this model
        return cls(enable_nfs_view_discovery,
                   nfs_all_squash,
                   nfs_root_permissions,
                   nfs_root_squash)


