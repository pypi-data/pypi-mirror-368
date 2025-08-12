# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.oracle_protection_group_object_identifier
import cohesity_management_sdk.models_v2.vlan_params_for_backup_restore_operation
import cohesity_management_sdk.models_v2.pre_and_post_script_params

class OracleProtectionGroupParameters(object):

    """Implementation of the 'Oracle Protection Group Parameters.' model.

    Specifies the parameters to create Oracle Protection Group.

    Attributes:
        full_auto_kill_timeout_secs (long|int): Time in seconds after which the full backup of the database in
          given backup job should be auto-killed.
        incr_auto_kill_timeout_secs (long|int): Time in seconds after which the incremental backup of the database
          in given backup job should be auto-killed.
        log_auto_kill_timeout_secs (long|int): Time in seconds after which the log backup of the database in
          given backup job should be auto-killed.
        objects (list of OracleProtectionGroupObjectIdentifier): Specifies the
            list of object ids to be protected.
        persist_mountpoints (bool): Specifies whether the mountpoints created
            while backing up Oracle DBs should be persisted.
        pre_post_script (PrePostScriptParams): Specifies the pre and post script parameters associated with
          a protection group.
        vlan_params (VlanParamsForBackupRestoreOperation): Specifies VLAN
            params associated with the backup/restore operation.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "full_auto_kill_timeout_secs":'fullAutoKillTimeoutSecs',
        "incr_auto_kill_timeout_secs":'incrAutoKillTimeoutSecs',
        "log_auto_kill_timeout_secs":'logAutoKillTimeoutSecs',
        "objects":'objects',
        "persist_mountpoints":'persistMountpoints',
        "pre_post_script":'prePostScript',
        "vlan_params":'vlanParams'
    }

    def __init__(self,
                 full_auto_kill_timeout_secs=None,
                 incr_auto_kill_timeout_secs=None,
                 log_auto_kill_timeout_secs=None,
                 objects=None,
                 persist_mountpoints=None,
                 pre_post_script=None,
                 vlan_params=None):
        """Constructor for the OracleProtectionGroupParameters class"""

        # Initialize members of the class
        self.full_auto_kill_timeout_secs = full_auto_kill_timeout_secs
        self.incr_auto_kill_timeout_secs = incr_auto_kill_timeout_secs
        self.log_auto_kill_timeout_secs = log_auto_kill_timeout_secs
        self.objects = objects
        self.persist_mountpoints = persist_mountpoints
        self.pre_post_script = pre_post_script
        self.vlan_params = vlan_params


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
        full_auto_kill_timeout_secs = dictionary.get('fullAutoKillTimeoutSecs')
        incr_auto_kill_timeout_secs = dictionary.get('incrAutoKillTimeoutSecs')
        log_auto_kill_timeout_secs = dictionary.get('logAutoKillTimeoutSecs')
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.oracle_protection_group_object_identifier.OracleProtectionGroupObjectIdentifier.from_dictionary(structure))
        persist_mountpoints = dictionary.get('persistMountpoints')
        pre_post_script_params = cohesity_management_sdk.models_v2.pre_and_post_script_params.PreAndPostScriptParams.from_dictionary(dictionary.get('prePostScript')) if dictionary.get('prePostScript') else None
        vlan_params = cohesity_management_sdk.models_v2.vlan_params_for_backup_restore_operation.VlanParamsForBackupRestoreOperation.from_dictionary(dictionary.get('vlanParams')) if dictionary.get('vlanParams') else None

        # Return an object of this model
        return cls(full_auto_kill_timeout_secs,
                   incr_auto_kill_timeout_secs,
                   log_auto_kill_timeout_secs,
                    objects,
                   persist_mountpoints,
                   pre_post_script_params,
                   vlan_params)