# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.view_protection
import cohesity_management_sdk.models_v2.view_alias_information
import cohesity_management_sdk.models_v2.view_stats

class BaseView(object):

    """Implementation of the 'Base View.' model.

    Specifies base settings for a View.

    Attributes:
        category (Category1Enum): Specifies the category of the View.
        name (string): Specifies the name of the View.
        view_id (long|int): Specifies an id of the View assigned by the
            Cohesity Cluster.
        storage_domain_id (long|int): Specifies the id of the Storage Domain
            (View Box) where the View is stored.
        storage_domain_name (string): Specifies the name of the Storage Domain
            (View Box) where the View is stored.
        create_time_msecs (long|int): Specifies the time that the View was
            created in milliseconds.
        basic_mount_path (string): Specifies the NFS mount path of the View
            (without the hostname information). This path is used to support
            NFS mounting of the paths specified in the nfsExportPathList on
            Windows systems.
        nfs_mount_path (string): Specifies the path for mounting this View as
            an NFS share.
        smb_mount_paths (list of string): Array of SMB Paths. Specifies the
            possible paths that can be used to mount this View as a SMB share.
            If Active Directory has multiple account names; each machine
            account has its own path.
        case_insensitive_names_enabled (bool): Specifies whether to support
            case insensitive file/folder names. This parameter can only be set
            during create and cannot be changed.
        view_protection (ViewProtection): Specifies information about the
            Protection Groups that are protecting the View.
        data_lock_expiry_usecs (long|int): DataLock (Write Once Read Many)
            lock expiry epoch time in microseconds. If a view is marked as a
            DataLock view, only a Data Security Officer (a user having Data
            Security Privilege) can delete the view until the lock expiry
            time.
        aliases (list of ViewAliasInformation): Aliases created for the view.
            A view alias allows a directory path inside a view to be mounted
            using the alias name.
        is_target_for_migrated_data (bool): Specifies if a view contains
            migrated data.
        stats (ViewStats): Provides statistics about the View.
        object_services_mapping_config (ObjectServicesMappingConfigEnum):
            Specifies the Object Services key mapping config of the view. This
            parameter can only be set during create and cannot be changed.
            Configuration of Object Services key mapping. Specifies the type
            of Object Services key mapping config.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "category":'category',
        "name":'name',
        "view_id":'viewId',
        "storage_domain_id":'storageDomainId',
        "storage_domain_name":'storageDomainName',
        "create_time_msecs":'createTimeMsecs',
        "basic_mount_path":'basicMountPath',
        "nfs_mount_path":'nfsMountPath',
        "smb_mount_paths":'smbMountPaths',
        "case_insensitive_names_enabled":'caseInsensitiveNamesEnabled',
        "view_protection":'viewProtection',
        "data_lock_expiry_usecs":'dataLockExpiryUsecs',
        "aliases":'aliases',
        "is_target_for_migrated_data":'isTargetForMigratedData',
        "stats":'stats',
        "object_services_mapping_config":'objectServicesMappingConfig'
    }

    def __init__(self,
                 category=None,
                 name=None,
                 view_id=None,
                 storage_domain_id=None,
                 storage_domain_name=None,
                 create_time_msecs=None,
                 basic_mount_path=None,
                 nfs_mount_path=None,
                 smb_mount_paths=None,
                 case_insensitive_names_enabled=None,
                 view_protection=None,
                 data_lock_expiry_usecs=None,
                 aliases=None,
                 is_target_for_migrated_data=None,
                 stats=None,
                 object_services_mapping_config=None):
        """Constructor for the BaseView class"""

        # Initialize members of the class
        self.category = category
        self.name = name
        self.view_id = view_id
        self.storage_domain_id = storage_domain_id
        self.storage_domain_name = storage_domain_name
        self.create_time_msecs = create_time_msecs
        self.basic_mount_path = basic_mount_path
        self.nfs_mount_path = nfs_mount_path
        self.smb_mount_paths = smb_mount_paths
        self.case_insensitive_names_enabled = case_insensitive_names_enabled
        self.view_protection = view_protection
        self.data_lock_expiry_usecs = data_lock_expiry_usecs
        self.aliases = aliases
        self.is_target_for_migrated_data = is_target_for_migrated_data
        self.stats = stats
        self.object_services_mapping_config = object_services_mapping_config


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
        category = dictionary.get('category')
        name = dictionary.get('name')
        view_id = dictionary.get('viewId')
        storage_domain_id = dictionary.get('storageDomainId')
        storage_domain_name = dictionary.get('storageDomainName')
        create_time_msecs = dictionary.get('createTimeMsecs')
        basic_mount_path = dictionary.get('basicMountPath')
        nfs_mount_path = dictionary.get('nfsMountPath')
        smb_mount_paths = dictionary.get('smbMountPaths')
        case_insensitive_names_enabled = dictionary.get('caseInsensitiveNamesEnabled')
        view_protection = cohesity_management_sdk.models_v2.view_protection.ViewProtection.from_dictionary(dictionary.get('viewProtection')) if dictionary.get('viewProtection') else None
        data_lock_expiry_usecs = dictionary.get('dataLockExpiryUsecs')
        aliases = None
        if dictionary.get("aliases") is not None:
            aliases = list()
            for structure in dictionary.get('aliases'):
                aliases.append(cohesity_management_sdk.models_v2.view_alias_information.ViewAliasInformation.from_dictionary(structure))
        is_target_for_migrated_data = dictionary.get('isTargetForMigratedData')
        stats = cohesity_management_sdk.models_v2.view_stats.ViewStats.from_dictionary(dictionary.get('stats')) if dictionary.get('stats') else None
        object_services_mapping_config = dictionary.get('objectServicesMappingConfig')

        # Return an object of this model
        return cls(category,
                   name,
                   view_id,
                   storage_domain_id,
                   storage_domain_name,
                   create_time_msecs,
                   basic_mount_path,
                   nfs_mount_path,
                   smb_mount_paths,
                   case_insensitive_names_enabled,
                   view_protection,
                   data_lock_expiry_usecs,
                   aliases,
                   is_target_for_migrated_data,
                   stats,
                   object_services_mapping_config)


