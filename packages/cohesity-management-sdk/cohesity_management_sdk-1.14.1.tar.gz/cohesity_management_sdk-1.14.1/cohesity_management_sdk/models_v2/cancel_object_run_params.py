# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.cluster_identifier

class CancelObjectRunParams(object):

    """Implementation of the 'CancelObjectRunParams' model.

    One object run to cancel.

    Attributes:
        run_id (string): Specifies the id of the run to cancel.
        cancel_local_run (bool): Specifies whether to cancel the local backup
            run. Default is false.
        archival_target_ids (list of long|int): Specifies the archival target
            ids where the tasks run. If specified, the archival target ids
            must be present within the run specified by the runId above.
        replication_targets (list of ClusterIdentifier): Specifies the cluster
            identifiers where the tasks run. If specified, the archival target
            ids must be present within the run specified by the runId above.
        cloud_spin_target_ids (list of long|int): Specifies the cloud spin
            target ids where the tasks run. If specified, the archival target
            ids must be present within the run specified by the runId above.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "run_id":'runId',
        "cancel_local_run":'cancelLocalRun',
        "archival_target_ids":'archivalTargetIds',
        "replication_targets":'replicationTargets',
        "cloud_spin_target_ids":'cloudSpinTargetIds'
    }

    def __init__(self,
                 run_id=None,
                 cancel_local_run=None,
                 archival_target_ids=None,
                 replication_targets=None,
                 cloud_spin_target_ids=None):
        """Constructor for the CancelObjectRunParams class"""

        # Initialize members of the class
        self.run_id = run_id
        self.cancel_local_run = cancel_local_run
        self.archival_target_ids = archival_target_ids
        self.replication_targets = replication_targets
        self.cloud_spin_target_ids = cloud_spin_target_ids


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
        run_id = dictionary.get('runId')
        cancel_local_run = dictionary.get('cancelLocalRun')
        archival_target_ids = dictionary.get('archivalTargetIds')
        replication_targets = None
        if dictionary.get("replicationTargets") is not None:
            replication_targets = list()
            for structure in dictionary.get('replicationTargets'):
                replication_targets.append(cohesity_management_sdk.models_v2.cluster_identifier.ClusterIdentifier.from_dictionary(structure))
        cloud_spin_target_ids = dictionary.get('cloudSpinTargetIds')

        # Return an object of this model
        return cls(run_id,
                   cancel_local_run,
                   archival_target_ids,
                   replication_targets,
                   cloud_spin_target_ids)


