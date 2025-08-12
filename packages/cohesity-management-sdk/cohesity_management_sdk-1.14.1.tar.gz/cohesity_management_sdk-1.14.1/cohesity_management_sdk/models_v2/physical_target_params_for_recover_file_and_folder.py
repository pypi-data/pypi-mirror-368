# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_target
import cohesity_management_sdk.models_v2.vlan_config_1

class PhysicalTargetParamsForRecoverFileAndFolder(object):

    """Implementation of the 'Physical Target Params for Recover File And Folder' model.

    Specifies the parameters for a Physical recovery target.

    Attributes:
        recover_target (RecoverTarget): Specifies the target entity where the
            volumes are being mounted.
        restore_to_original_paths (bool): If this is true, then files will be
            restored to original paths.
        overwrite_existing (bool): Specifies whether to overwrite existing
            file/folder during recovery.
        alternate_restore_directory (string): Specifies the directory path
            where restore should happen if restore_to_original_paths is set to
            false.
        preserve_attributes (bool): Specifies whether to preserve file/folder
            attributes during recovery.
        preserve_timestamps (bool): Whether to preserve the original time
            stamps.
        preserve_acls (bool): Whether to preserve the ACLs of the original
            file.
        continue_on_error (bool): Specifies whether to continue recovering
            other volumes if one of the volumes fails to recover. Default
            value is false.
        vlan_config (VlanConfig1): Specifies VLAN Params associated with the
            recovered. If this is not specified, then the VLAN settings will
            be automatically selected from one of the below options: a. If
            VLANs are configured on Cohesity, then the VLAN host/VIP will be
            automatically based on the client's (e.g. ESXI host) IP address.
            b. If VLANs are not configured on Cohesity, then the partition
            hostname or VIPs will be used for Recovery.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recover_target":'recoverTarget',
        "restore_to_original_paths":'restoreToOriginalPaths',
        "overwrite_existing":'overwriteExisting',
        "alternate_restore_directory":'alternateRestoreDirectory',
        "preserve_attributes":'preserveAttributes',
        "preserve_timestamps":'preserveTimestamps',
        "preserve_acls":'preserveAcls',
        "continue_on_error":'continueOnError',
        "vlan_config":'vlanConfig'
    }

    def __init__(self,
                 recover_target=None,
                 restore_to_original_paths=None,
                 overwrite_existing=None,
                 alternate_restore_directory=None,
                 preserve_attributes=None,
                 preserve_timestamps=None,
                 preserve_acls=None,
                 continue_on_error=None,
                 vlan_config=None):
        """Constructor for the PhysicalTargetParamsForRecoverFileAndFolder class"""

        # Initialize members of the class
        self.recover_target = recover_target
        self.restore_to_original_paths = restore_to_original_paths
        self.overwrite_existing = overwrite_existing
        self.alternate_restore_directory = alternate_restore_directory
        self.preserve_attributes = preserve_attributes
        self.preserve_timestamps = preserve_timestamps
        self.preserve_acls = preserve_acls
        self.continue_on_error = continue_on_error
        self.vlan_config = vlan_config


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
        recover_target = cohesity_management_sdk.models_v2.recover_target.RecoverTarget.from_dictionary(dictionary.get('recoverTarget')) if dictionary.get('recoverTarget') else None
        restore_to_original_paths = dictionary.get('restoreToOriginalPaths')
        overwrite_existing = dictionary.get('overwriteExisting')
        alternate_restore_directory = dictionary.get('alternateRestoreDirectory')
        preserve_attributes = dictionary.get('preserveAttributes')
        preserve_timestamps = dictionary.get('preserveTimestamps')
        preserve_acls = dictionary.get('preserveAcls')
        continue_on_error = dictionary.get('continueOnError')
        vlan_config = cohesity_management_sdk.models_v2.vlan_config_1.VlanConfig1.from_dictionary(dictionary.get('vlanConfig')) if dictionary.get('vlanConfig') else None

        # Return an object of this model
        return cls(recover_target,
                   restore_to_original_paths,
                   overwrite_existing,
                   alternate_restore_directory,
                   preserve_attributes,
                   preserve_timestamps,
                   preserve_acls,
                   continue_on_error,
                   vlan_config)


