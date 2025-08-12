# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.uda_protection_group_object_params
import cohesity_management_sdk.models_v2.key_value_pair

class UdaProtectionGroupParams(object):

    """Implementation of the 'UdaProtectionGroupParams' model.

    Specifies parameters related to the Universal Data Adapter Protection
    job.

    Attributes:
        backup_job_arguments (list of KeyValuePair): Specifies the map of custom arguments to be supplied to the various
          backup scripts.
        et_log_backup (bool): Specifies whether this Protection Group is created from a source
          having externally triggered log backup support.
        source_id (long|int): Specifies the source Id of the objects to be
            protected.
        exclude_object_ids (list of long|int): Specifies the objects to be excluded in the Protection Group.
        objects (list of UdaProtectionGroupObjectParams): Specifies a list of
            fully qualified names of the objects to be protected.
        full_backup_args (string): Specifies the custom arguments to be
            supplied to the full backup script when a full backup is enabled
            in the policy.
        incr_backup_args (string): Specifies the custom arguments to be
            supplied to the incremental backup script when an incremental
            backup is enabled in the policy.
        log_backup_args (string): Specifies the custom arguments to be
            supplied to the log backup script when a log backup is enabled in
            the policy.
        concurrency (int): Specifies the maximum number of concurrent IO
            Streams that will be created to exchange data with the cluster. If
            not specified, the default value is taken as 1.
        mounts (int): Specifies the maximum number of view mounts per host. If
            not specified, the default value is taken as 1.
        has_entity_support (bool): Specifies whether this Protection Group is created from a source
          having entity support.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "backup_job_arguments":'backupJobArguments',
        "et_log_backup":'etLogBackup',
        "source_id":'sourceId',
        "exclude_object_ids":'excludeObjectIds',
        "objects":'objects',
        "full_backup_args":'fullBackupArgs',
        "incr_backup_args":'incrBackupArgs',
        "log_backup_args":'logBackupArgs',
        "concurrency":'concurrency',
        "mounts":'mounts',
        "has_entity_support":'hasEntitySupport'
    }

    def __init__(self,
                 backup_job_arguments=None,
                 et_log_backup=None,
                 source_id=None,
                 exclude_object_ids=None,
                 objects=None,
                 full_backup_args=None,
                 incr_backup_args=None,
                 log_backup_args=None,
                 concurrency=1,
                 mounts=1,
                 has_entity_support=None):
        """Constructor for the UdaProtectionGroupParams class"""

        # Initialize members of the class
        self.backup_job_arguments = backup_job_arguments
        self.et_log_backup = et_log_backup
        self.source_id = source_id
        self.exclude_object_ids = exclude_object_ids
        self.objects = objects
        self.full_backup_args = full_backup_args
        self.incr_backup_args = incr_backup_args
        self.log_backup_args = log_backup_args
        self.concurrency = concurrency
        self.mounts = mounts
        self.has_entity_support = has_entity_support


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
        backup_job_arguments = None
        if dictionary.get("backupJobArguments") is not None:
            backup_job_arguments = list()
            for structure in dictionary.get('backupJobArguments'):
                backup_job_arguments.append(cohesity_management_sdk.models_v2.key_value_pair.KeyValuePair.from_dictionary(structure))
        et_log_backup = dictionary.get('etLogBackup')
        source_id = dictionary.get('sourceId')
        exclude_object_ids = dictionary.get('excludeObjectIds')
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.uda_protection_group_object_params.UdaProtectionGroupObjectParams.from_dictionary(structure))
        full_backup_args = dictionary.get('fullBackupArgs')
        incr_backup_args = dictionary.get('incrBackupArgs')
        log_backup_args = dictionary.get('logBackupArgs')
        concurrency = dictionary.get("concurrency") if dictionary.get("concurrency") else 1
        mounts = dictionary.get("mounts") if dictionary.get("mounts") else 1
        has_entity_support = dictionary.get('hasEntitySupport')

        # Return an object of this model
        return cls(
                   backup_job_arguments,
            et_log_backup,
                   source_id,
            exclude_object_ids,
                   objects,
                   full_backup_args,
                   incr_backup_args,
                   log_backup_args,
                   concurrency,
                   mounts,
        has_entity_support)