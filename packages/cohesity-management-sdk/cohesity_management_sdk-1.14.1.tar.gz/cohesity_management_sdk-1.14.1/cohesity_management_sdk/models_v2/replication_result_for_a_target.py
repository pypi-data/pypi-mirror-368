# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.aws_target_configuration
import cohesity_management_sdk.models_v2.azure_target_configuration
import cohesity_management_sdk.models_v2.replication_data_statistics
import cohesity_management_sdk.models_v2.data_lock_constraints

class ReplicationResultForATarget(object):

    """Implementation of the 'Replication result for a target.' model.

    Replication result for a target.

    Attributes:
        cluster_id (long|int): Specifies the id of the cluster.
        cluster_incarnation_id (long|int): Specifies the incarnation id of the
            cluster.
        cluster_name (string): Specifies the name of the cluster.
        aws_target_config (AWSTargetConfiguration): Specifies the
            configuration for adding AWS as repilcation target
        azure_target_config (AzureTargetConfiguration): Specifies the
            configuration for adding Azure as replication target
        start_time_usecs (long|int): Specifies the start time of replication
            in Unix epoch Timestamp(in microseconds) for a target.
        end_time_usecs (long|int): Specifies the end time of replication in
            Unix epoch Timestamp(in microseconds) for a target.
        multi_object_replication (bool): Specifies whether view based replication was used. In this
            case, the view containing all objects is replicated as a whole instead
            of replicating on a per object basis.
        queued_time_usecs (long|int): Specifies the time when the replication
            is queued for schedule in Unix epoch Timestamp(in microseconds)
            for a target.
        status (Status9Enum): Status of the replication for a target.
            'Running' indicates that the run is still running. 'Canceled'
            indicates that the run has been canceled. 'Canceling' indicates
            that the run is in the process of being canceled. 'Failed'
            indicates that the run has failed. 'Missed' indicates that the run
            was unable to take place at the scheduled time because the
            previous run was still happening. 'Succeeded' indicates that the
            run has finished successfully. 'SucceededWithWarning' indicates
            that the run finished successfully, but there were some warning
            messages.
        message (string): Message about the replication run.
        on_legal_hold (bool): Specifies the legal hold status for a replication target.
        percentage_completed (int): Specifies the progress in percentage.
        stats (ReplicationDataStatistics): Specifies statistics about
            replication data.
        is_manually_deleted (bool): Specifies whether the snapshot is deleted
            manually.
        expiry_time_usecs (long|int): Specifies the expiry time of attempt in
            Unix epoch Timestamp (in microseconds) for an object.
        replication_task_id (string): Task UID for a replication protection
            run. This is for tasks that are replicated from another cluster.
        entries_changed (int): Specifies the number of metadata actions
            completed during the protection run.
        is_in_bound (bool): Specifies the direction of the replication. If the
            snapshot is replicated to this cluster, then isInBound is true. If
            the snapshot is replicated from this cluster to another cluster,
            then isInBound is false.
        data_lock_constraints (DataLockConstraints): Specifies the dataLock
            constraints for local or target snapshot.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cluster_id":'clusterId',
        "cluster_incarnation_id":'clusterIncarnationId',
        "cluster_name":'clusterName',
        "aws_target_config":'awsTargetConfig',
        "azure_target_config":'azureTargetConfig',
        "start_time_usecs":'startTimeUsecs',
        "end_time_usecs":'endTimeUsecs',
        "multi_object_replication":'multiObjectReplication',
        "queued_time_usecs":'queuedTimeUsecs',
        "status":'status',
        "message":'message',
        "on_legal_hold":'onLegalHold',
        "percentage_completed":'percentageCompleted',
        "stats":'stats',
        "is_manually_deleted":'isManuallyDeleted',
        "expiry_time_usecs":'expiryTimeUsecs',
        "replication_task_id":'replicationTaskId',
        "entries_changed":'entriesChanged',
        "is_in_bound":'isInBound',
        "data_lock_constraints":'dataLockConstraints'
    }

    def __init__(self,
                 cluster_id=None,
                 cluster_incarnation_id=None,
                 cluster_name=None,
                 aws_target_config=None,
                 azure_target_config=None,
                 start_time_usecs=None,
                 end_time_usecs=None,
                 multi_object_replication=None,
                 queued_time_usecs=None,
                 status=None,
                 message=None,
                 on_legal_hold=None,
                 percentage_completed=None,
                 stats=None,
                 is_manually_deleted=None,
                 expiry_time_usecs=None,
                 replication_task_id=None,
                 entries_changed=None,
                 is_in_bound=None,
                 data_lock_constraints=None):
        """Constructor for the ReplicationResultForATarget class"""

        # Initialize members of the class
        self.cluster_id = cluster_id
        self.cluster_incarnation_id = cluster_incarnation_id
        self.cluster_name = cluster_name
        self.aws_target_config = aws_target_config
        self.azure_target_config = azure_target_config
        self.start_time_usecs = start_time_usecs
        self.end_time_usecs = end_time_usecs
        self.multi_object_replication = multi_object_replication
        self.queued_time_usecs = queued_time_usecs
        self.status = status
        self.message = message
        self.on_legal_hold = on_legal_hold
        self.percentage_completed = percentage_completed
        self.stats = stats
        self.is_manually_deleted = is_manually_deleted
        self.expiry_time_usecs = expiry_time_usecs
        self.replication_task_id = replication_task_id
        self.entries_changed = entries_changed
        self.is_in_bound = is_in_bound
        self.data_lock_constraints = data_lock_constraints


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
        cluster_id = dictionary.get('clusterId')
        cluster_incarnation_id = dictionary.get('clusterIncarnationId')
        cluster_name = dictionary.get('clusterName')
        aws_target_config = cohesity_management_sdk.models_v2.aws_target_configuration.AWSTargetConfiguration.from_dictionary(dictionary.get('awsTargetConfig')) if dictionary.get('awsTargetConfig') else None
        azure_target_config = cohesity_management_sdk.models_v2.azure_target_configuration.AzureTargetConfiguration.from_dictionary(dictionary.get('azureTargetConfig')) if dictionary.get('azureTargetConfig') else None
        start_time_usecs = dictionary.get('startTimeUsecs')
        end_time_usecs = dictionary.get('endTimeUsecs')
        multi_object_replication = dictionary.get('multiObjectReplication')
        queued_time_usecs = dictionary.get('queuedTimeUsecs')
        status = dictionary.get('status')
        message = dictionary.get('message')
        on_legal_hold = dictionary.get('onLegalHold')
        percentage_completed = dictionary.get('percentageCompleted')
        stats = cohesity_management_sdk.models_v2.replication_data_statistics.ReplicationDataStatistics.from_dictionary(dictionary.get('stats')) if dictionary.get('stats') else None
        is_manually_deleted = dictionary.get('isManuallyDeleted')
        expiry_time_usecs = dictionary.get('expiryTimeUsecs')
        replication_task_id = dictionary.get('replicationTaskId')
        entries_changed = dictionary.get('entriesChanged')
        is_in_bound = dictionary.get('isInBound')
        data_lock_constraints = cohesity_management_sdk.models_v2.data_lock_constraints.DataLockConstraints.from_dictionary(dictionary.get('dataLockConstraints')) if dictionary.get('dataLockConstraints') else None

        # Return an object of this model
        return cls(cluster_id,
                   cluster_incarnation_id,
                   cluster_name,
                   aws_target_config,
                   azure_target_config,
                   start_time_usecs,
                   end_time_usecs,
                   multi_object_replication,
                   queued_time_usecs,
                   status,
                   message,
                   on_legal_hold,
                   percentage_completed,
                   stats,
                   is_manually_deleted,
                   expiry_time_usecs,
                   replication_task_id,
                   entries_changed,
                   is_in_bound,
                   data_lock_constraints)