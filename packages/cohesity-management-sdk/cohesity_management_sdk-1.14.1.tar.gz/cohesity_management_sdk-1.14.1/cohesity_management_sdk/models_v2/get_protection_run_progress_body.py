# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.backup_run_progress_info
import cohesity_management_sdk.models_v2.archival_target_progress_info
import cohesity_management_sdk.models_v2.replication_target_progress_info

class GetProtectionRunProgressBody(object):

    """Implementation of the 'GetProtectionRunProgressBody' model.

    Specifies the progress of a protection run.

    Attributes:
        local_run (BackupRunProgressInfo): Specifies the progress of a local
            backup run.
        archival_run (list of ArchivalTargetProgressInfo): Progress for the
            archival run.
        replication_run (list of ReplicationTargetProgressInfo): Progress for
            the replication run.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "local_run":'localRun',
        "archival_run":'archivalRun',
        "replication_run":'replicationRun'
    }

    def __init__(self,
                 local_run=None,
                 archival_run=None,
                 replication_run=None):
        """Constructor for the GetProtectionRunProgressBody class"""

        # Initialize members of the class
        self.local_run = local_run
        self.archival_run = archival_run
        self.replication_run = replication_run


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
        local_run = cohesity_management_sdk.models_v2.backup_run_progress_info.BackupRunProgressInfo.from_dictionary(dictionary.get('localRun')) if dictionary.get('localRun') else None
        archival_run = None
        if dictionary.get("archivalRun") is not None:
            archival_run = list()
            for structure in dictionary.get('archivalRun'):
                archival_run.append(cohesity_management_sdk.models_v2.archival_target_progress_info.ArchivalTargetProgressInfo.from_dictionary(structure))
        replication_run = None
        if dictionary.get("replicationRun") is not None:
            replication_run = list()
            for structure in dictionary.get('replicationRun'):
                replication_run.append(cohesity_management_sdk.models_v2.replication_target_progress_info.ReplicationTargetProgressInfo.from_dictionary(structure))

        # Return an object of this model
        return cls(local_run,
                   archival_run,
                   replication_run)


