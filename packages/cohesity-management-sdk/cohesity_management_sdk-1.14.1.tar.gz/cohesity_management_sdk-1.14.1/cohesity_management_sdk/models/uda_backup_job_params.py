# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.uda_backup_job_params_backup_job_arguments_map_entry
import cohesity_management_sdk.models.uda_objects
import cohesity_management_sdk.models.uda_s3_view_backup_properties


class UdaBackupJobParams(object):

    """Implementation of the 'UdaBackupJobParams' model.

    Contains backup params at the job level applicable for uda environment.
    These are sent from iris to magneto.


    Attributes:

        backup_job_arguments_map (list of
            UdaBackupJobParams_BackupJobArgumentsMapEntry): Map to store custom
            arguments which will be provided to the backup job scripts.
        concurrency (int): Max concurrency for the backup job.
        entity_support (bool): Indicates if backup job was created after source
            acquired entity support capability.
        et_log_backup (bool): Indicates if backup job was created after source
            acquired externally triggered log backup capability.
        external_disk_size_gb (int): If using external disks, this parameter
            will contain the user-requested disk size for the slave to consume
            when requesting a disk from heimdall.
        external_disk_sku (string): If using external disks, this parameter
            will contain the user-requested disk SKU for the slave to consume
            when requesting a disk from heimdall.
        full_backup_args (string): Custom arguments for full backup scripts.
        incremental_backup_args (string): Custom arguments for incremental
            backup scripts.
        log_backup_args (string): Custom arguments for log backup scripts.
        mounts (int): Max number of view mounts per host.
        source_id (long|int): Id of the source to which the objects being
            protected belong to. This can be removed once entity hierarchy
            support is added to UDA and protected objects can be specified by
            their Ids instead of their names.
        uda_objects (list of UdaObjects): List of objects to be backed up.
        uda_s3_view_backup_properties (UdaS3ViewBackupProperties): This message
            captures all the details needed by UDA Backup to create S3 views
            and to access the S3 bucket.
    """


    # Create a mapping from Model property names to API property names
    _names = {
        "backup_job_arguments_map":'backupJobArgumentsMap',
        "concurrency":'concurrency',
        "entity_support":'entitySupport',
        "et_log_backup": 'etLogBackup',
        "external_disk_size_gb": 'externalDiskSizeGb',
        "external_disk_sku": 'externalDiskSku',
        "full_backup_args":'fullBackupArgs',
        "incremental_backup_args":'incrementalBackupArgs',
        "log_backup_args":'logBackupArgs',
        "mounts":'mounts',
        "source_id":'sourceId',
        "uda_objects":'udaObjects',
        "uda_s3_view_backup_properties":'udaS3ViewBackupProperties',
    }
    def __init__(self,
                 backup_job_arguments_map=None,
                 concurrency=None,
                 entity_support=None,
                 et_log_backup=None,
                 external_disk_size_gb=None,
                 external_disk_sku=None,
                 full_backup_args=None,
                 incremental_backup_args=None,
                 log_backup_args=None,
                 mounts=None,
                 source_id=None,
                 uda_objects=None,
                 uda_s3_view_backup_properties=None,
            ):

        """Constructor for the UdaBackupJobParams class"""

        # Initialize members of the class
        self.backup_job_arguments_map = backup_job_arguments_map
        self.concurrency = concurrency
        self.entity_support = entity_support
        self.et_log_backup = et_log_backup
        self.external_disk_size_gb = external_disk_size_gb
        self.external_disk_sku = external_disk_sku
        self.full_backup_args = full_backup_args
        self.incremental_backup_args = incremental_backup_args
        self.log_backup_args = log_backup_args
        self.mounts = mounts
        self.source_id = source_id
        self.uda_objects = uda_objects
        self.uda_s3_view_backup_properties = uda_s3_view_backup_properties

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
        backup_job_arguments_map = None
        if dictionary.get("backupJobArgumentsMap") is not None:
            backup_job_arguments_map = list()
            for structure in dictionary.get('backupJobArgumentsMap'):
                backup_job_arguments_map.append(cohesity_management_sdk.models.uda_backup_job_params_backup_job_arguments_map_entry.UdaBackupJobParams_BackupJobArgumentsMapEntry.from_dictionary(structure))
        concurrency = dictionary.get('concurrency')
        entity_support = dictionary.get('entitySupport')
        et_log_backup = dictionary.get('etLogBackup')
        external_disk_size_gb = dictionary.get('externalDiskSizeGb')
        external_disk_sku = dictionary.get('externalDiskSku')
        full_backup_args = dictionary.get('fullBackupArgs')
        incremental_backup_args = dictionary.get('incrementalBackupArgs')
        log_backup_args = dictionary.get('logBackupArgs')
        mounts = dictionary.get('mounts')
        source_id = dictionary.get('sourceId')
        uda_objects = None
        if dictionary.get("udaObjects") is not None:
            uda_objects = list()
            for structure in dictionary.get('udaObjects'):
                uda_objects.append(cohesity_management_sdk.models.uda_objects.UdaObjects.from_dictionary(structure))
        uda_s3_view_backup_properties = cohesity_management_sdk.models.uda_s3_view_backup_properties.UdaS3ViewBackupProperties.from_dictionary(dictionary.get('udaS3ViewBackupProperties')) if dictionary.get('udaS3ViewBackupProperties') else None

        # Return an object of this model
        return cls(
            backup_job_arguments_map,
            concurrency,
            entity_support,
            et_log_backup,
            external_disk_size_gb,
            external_disk_sku,
            full_backup_args,
            incremental_backup_args,
            log_backup_args,
            mounts,
            source_id,
            uda_objects,
            uda_s3_view_backup_properties
)