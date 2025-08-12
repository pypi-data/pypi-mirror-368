# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class UdaThrottlingParams(object):

    """Implementation of the 'UdaThrottlingParams' model.

    Attributes:
        max_anyjob_resources (int): Max source specific resource to use for any
            job on source.
            Total resource usage should not exceed this for all jobs on source.'
        max_backup_resources (int): Max source specific resource to use for
            backup on source.
        max_log_backup_resources (int): Max source specific resource to use
            for log backup on source.
        max_restore_resources (int): Max source specific resource to use for
            restore on source.
    """


    # Create a mapping from Model property names to API property names
    _names = {
        "max_anyjob_resources":'maxAnyjobResources',
        "max_backup_resources":'maxBackupResources',
        "max_log_backup_resources":'maxLogBackupResources',
        "max_restore_resources":'maxRestoreResources',
    }
    def __init__(self,
                 max_anyjob_resources=None,
                 max_backup_resources=None,
                 max_log_backup_resources=None,
                 max_restore_resources=None,
            ):

        """Constructor for the UdaThrottlingParams class"""

        # Initialize members of the class
        self.max_anyjob_resources = max_anyjob_resources
        self.max_backup_resources = max_backup_resources
        self.max_log_backup_resources = max_log_backup_resources
        self.max_restore_resources = max_restore_resources

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
        max_anyjob_resources = dictionary.get('maxAnyjobResources')
        max_backup_resources = dictionary.get('maxBackupResources')
        max_log_backup_resources = dictionary.get('maxLogBackupResources')
        max_restore_resources = dictionary.get('maxRestoreResources')

        # Return an object of this model
        return cls(
            max_anyjob_resources,
            max_backup_resources,
            max_log_backup_resources,
            max_restore_resources
)