# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.file_path_filter

class PhysicalEnvJobParameters(object):

    """Implementation of the 'PhysicalEnvJobParameters' model.

    Protection Job parameters applicable to 'kPhysical' Environment type.
    Specifies job parameters applicable for all 'kPhysical' Environment type
    Protection Sources in a Protection Job.

    Attributes:
        cobmr_backup (bool): Whether CoBMR backup is enabled. If true,
            Cristie executables will be run
            in agent so that bare metal restore can be performed
        file_path_filters (FilePathFilter): Specifies filters to match files
            and directories on a Server. Two kinds of filters are supported.
            a) prefix which always starts with '/'. b) posix which always
            starts with '*' (cannot be "*" only). Regular expressions are not
            supported. If a directory is matched, the action is applicable to
            all of its descendants. File paths not matching any protectFilters
            are not backed up.  An example is: Protect Filters: "/" Exclude
            Filters: "/tmp", "*.mp4" Using such a policy will include
            everything under the root directory except the /tmp directory and
            all the mp4 files.
        incremental_snapshot_upon_restart (bool): If true, performs an
            incremental backup after server restarts. Otherwise a full backup
            is done. NOTE: This is applicable only to Windows servers. If not
            set, default value is false.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cobmr_backup": 'CobmrBackup',
        "file_path_filters":'filePathFilters',
        "incremental_snapshot_upon_restart":'incrementalSnapshotUponRestart'
    }

    def __init__(self,
                 cobmr_backup=None,
                 file_path_filters=None,
                 incremental_snapshot_upon_restart=None):
        """Constructor for the PhysicalEnvJobParameters class"""

        # Initialize members of the class
        self.cobmr_backup = cobmr_backup
        self.file_path_filters = file_path_filters
        self.incremental_snapshot_upon_restart = incremental_snapshot_upon_restart


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
        cobmr_backup = dictionary.get('CobmrBackup')
        file_path_filters = cohesity_management_sdk.models.file_path_filter.FilePathFilter.from_dictionary(dictionary.get('filePathFilters')) if dictionary.get('filePathFilters') else None
        incremental_snapshot_upon_restart = dictionary.get('incrementalSnapshotUponRestart')

        # Return an object of this model
        return cls(cobmr_backup,
                   file_path_filters,
                   incremental_snapshot_upon_restart)


