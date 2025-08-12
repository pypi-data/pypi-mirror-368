# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.failover_objects

class FailoverRunConfiguration(object):

    """Implementation of the 'FailoverRunConfiguration' model.

    Specifies the configuration required for execting special run as a part of
    failover workflow. This special run is triggered during palnned failover
    to sync the source cluster to replication cluster with minimum possible
    delta. Please note that if this object is passed then this special run
    will ignore the other archivals and retention settings.

    Attributes:
        replication_cluster_id (long|int): Specifies the replication cluster
            Id where planned run will replicate objects.
        objects (list of FailoverObjects): Specifies the list of all local
            entity ids of all the objects being failed from the source
            cluster.
        protection_group_id (string): Specifies the active protection group id
            on the source cluster from where the objects are being failed
            over.
        run_type (RunType5Enum): Specifies the type of the backup run to be
            triggered by this request. If this is not set defaults to
            incremental backup.
        view_id (long|int): If failover is initiated by view based
            orchastrator, then this field specifies the local view id of
            source cluster which is being failed over.
        cancel_non_failover_runs (bool): If set to true, other ongoing runs
            backing up the same set of entities being failed over will be
            initiated for cancellation. Non conflicting run operations such as
            replications to other clusters, archivals will not be cancelled.
            If set to false, then new run will wait for all the pending
            operations to finish normally before scheduling a new
            backup/replication.
        pause_next_runs (bool): If this is set to true then unless failover
            operation is completed, all the next runs will be pasued.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "replication_cluster_id":'replicationClusterId',
        "objects":'objects',
        "protection_group_id":'protectionGroupId',
        "run_type":'runType',
        "view_id":'viewId',
        "cancel_non_failover_runs":'cancelNonFailoverRuns',
        "pause_next_runs":'pauseNextRuns'
    }

    def __init__(self,
                 replication_cluster_id=None,
                 objects=None,
                 protection_group_id=None,
                 run_type=None,
                 view_id=None,
                 cancel_non_failover_runs=None,
                 pause_next_runs=None):
        """Constructor for the FailoverRunConfiguration class"""

        # Initialize members of the class
        self.replication_cluster_id = replication_cluster_id
        self.objects = objects
        self.protection_group_id = protection_group_id
        self.run_type = run_type
        self.view_id = view_id
        self.cancel_non_failover_runs = cancel_non_failover_runs
        self.pause_next_runs = pause_next_runs


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
        replication_cluster_id = dictionary.get('replicationClusterId')
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.failover_objects.FailoverObjects.from_dictionary(structure))
        protection_group_id = dictionary.get('protectionGroupId')
        run_type = dictionary.get('runType')
        view_id = dictionary.get('viewId')
        cancel_non_failover_runs = dictionary.get('cancelNonFailoverRuns')
        pause_next_runs = dictionary.get('pauseNextRuns')

        # Return an object of this model
        return cls(replication_cluster_id,
                   objects,
                   protection_group_id,
                   run_type,
                   view_id,
                   cancel_non_failover_runs,
                   pause_next_runs)


