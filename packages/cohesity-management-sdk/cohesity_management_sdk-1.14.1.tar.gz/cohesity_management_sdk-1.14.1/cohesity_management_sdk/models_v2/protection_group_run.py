# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.cluster_identifier
import cohesity_management_sdk.models_v2.snapshot_replication_archival_results_for_an_object
import cohesity_management_sdk.models_v2.summary_information_for_local_snapshot_run
import cohesity_management_sdk.models_v2.summary_information_for_replication_run
import cohesity_management_sdk.models_v2.summary_information_for_archival_run
import cohesity_management_sdk.models_v2.summary_information_for_cloud_spin_run
import cohesity_management_sdk.models_v2.snapshot_replication_archival_results_for_an_object
import cohesity_management_sdk.models_v2.tenant

class ProtectionGroupRun(object):

    """Implementation of the 'Protection Group run.' model.

    Specifies the parameters which are common between Protection Group
      runs of all Protection Groups.

    Attributes:
        archival_info (ArchivalRunSummary): Summary information about archival run.
        cloud_spin_info (CloudSpinRunSummary): Summary information about cloud spin run.
        environment (string): Specifies the environment of the Protection Group.
        externally_triggered_backup_tag (string): The tag of externally triggered backup job.
        has_local_snapshot (bool): Specifies whether the run has a local snapshot. For cloud retrieved
          runs there may not be local snapshots.
        id (string): Specifies the ID of the Protection Group run.
        is_cloud_archival_direct (bool): Specifies whether the run is a CAD run if cloud archive direct
          feature is enabled. If this field is true, the primary backup copy will
          only be available at the given archived location.
        is_local_snapshots_deleted (bool): Specifies if snapshots for this run has been deleted.
        is_replication_run (bool): Specifies if this protection run is a replication run.
        local_backup_info (SummaryInformationForLocalSnapshotRun): Summary information about local snapshot run across all objects.
        objects (list of SnapshotReplicationArchivalResultsForAnObject): Snapshot, replication, archival results for each object.
        on_legal_hold (bool): Specifies if the Protection Run is on legal hold.
        origin_cluster_identifier (ClusterIdentifier): Specifies the information of the primary cluster if this run
          is a replication run.
        origin_protection_group_id (string): ProtectionGroupId to which this run belongs on the primary cluster
          if this run is a replication run.
        original_backup_info (SummaryInformationForLocalSnapshotRun): Summary information about snapshot run on the original cluster.
          This only applies to replication run.
        permissions (list of Tenant): Specifies the list of tenants that have permissions for this
          protection group run.
        protection_group_id (string): ProtectionGroupId to which this run belongs.
        protection_group_instance_id (long|int): Protection Group instance Id.
            This field will be removed later.
        protection_group_name (string): Name of the Protection Group to which this run belongs.
        replication_info (SummaryInformationForReplicationRun): Summary information about replication run across all objects.
        is_cloud_archival_direct (bool): Specifies whether the run is a CAD run if cloud archive direct
          feature is enabled. If this field is true, the primary backup copy will
          only be available at the given archived location.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "protection_group_instance_id":'protectionGroupInstanceId',
        "protection_group_id":'protectionGroupId',
        "is_replication_run":'isReplicationRun',
        "origin_cluster_identifier":'originClusterIdentifier',
        "origin_protection_group_id":'originProtectionGroupId',
        "protection_group_name":'protectionGroupName',
        "is_local_snapshots_deleted":'isLocalSnapshotsDeleted',
        "objects":'objects',
        "local_backup_info":'localBackupInfo',
        "original_backup_info":'originalBackupInfo',
        "replication_info":'replicationInfo',
        "archival_info":'archivalInfo',
        "cloud_spin_info":'cloudSpinInfo',
        "on_legal_hold":'onLegalHold',
        "permissions":'permissions',
        "has_local_snapshot":'hasLocalSnapshot',
        "environment":'environment',
        "externally_triggered_backup_tag":'externallyTriggeredBackupTag',
        "is_cloud_archival_direct":'isCloudArchivalDirect'
    }

    def __init__(self,
                 id=None,
                 protection_group_instance_id=None,
                 protection_group_id=None,
                 is_replication_run=None,
                 origin_cluster_identifier=None,
                 origin_protection_group_id=None,
                 protection_group_name=None,
                 is_local_snapshots_deleted=None,
                 objects=None,
                 local_backup_info=None,
                 original_backup_info=None,
                 replication_info=None,
                 archival_info=None,
                 cloud_spin_info=None,
                 on_legal_hold=None,
                 permissions=None,
                 has_local_snapshot=None,
                 environment=None,
                 externally_triggered_backup_tag=None,
                 is_cloud_archival_direct=None):
        """Constructor for the CommonProtectionGroupRunResponseParameters class"""

        # Initialize members of the class
        self.id = id
        self.protection_group_instance_id = protection_group_instance_id
        self.protection_group_id = protection_group_id
        self.is_replication_run = is_replication_run
        self.origin_cluster_identifier = origin_cluster_identifier
        self.origin_protection_group_id = origin_protection_group_id
        self.protection_group_name = protection_group_name
        self.is_local_snapshots_deleted = is_local_snapshots_deleted
        self.objects = objects
        self.local_backup_info = local_backup_info
        self.original_backup_info = original_backup_info
        self.replication_info = replication_info
        self.archival_info = archival_info
        self.cloud_spin_info = cloud_spin_info
        self.on_legal_hold = on_legal_hold
        self.permissions = permissions
        self.has_local_snapshot = has_local_snapshot
        self.environment = environment
        self.externally_triggered_backup_tag = externally_triggered_backup_tag
        self.is_cloud_archival_direct = is_cloud_archival_direct

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
        id = dictionary.get('id')
        protection_group_instance_id = dictionary.get('protectionGroupInstanceId')
        protection_group_id = dictionary.get('protectionGroupId')
        is_replication_run = dictionary.get('isReplicationRun')
        origin_cluster_identifier = cohesity_management_sdk.models_v2.cluster_identifier.ClusterIdentifier.from_dictionary(dictionary.get('originClusterIdentifier')) if dictionary.get('originClusterIdentifier') else None
        origin_protection_group_id = dictionary.get('originProtectionGroupId')
        protection_group_name = dictionary.get('protectionGroupName')
        is_local_snapshots_deleted = dictionary.get('isLocalSnapshotsDeleted')
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.snapshot_replication_archival_results_for_an_object.SnapshotReplicationArchivalResultsForAnObject.from_dictionary(structure))
        local_backup_info = cohesity_management_sdk.models_v2.summary_information_for_local_snapshot_run.SummaryInformationForLocalSnapshotRun.from_dictionary(dictionary.get('localBackupInfo')) if dictionary.get('localBackupInfo') else None
        original_backup_info = cohesity_management_sdk.models_v2.summary_information_for_local_snapshot_run.SummaryInformationForLocalSnapshotRun.from_dictionary(dictionary.get('originalBackupInfo')) if dictionary.get('originalBackupInfo') else None
        replication_info = cohesity_management_sdk.models_v2.summary_information_for_replication_run.SummaryInformationForReplicationRun.from_dictionary(dictionary.get('replicationInfo')) if dictionary.get('replicationInfo') else None
        archival_info = cohesity_management_sdk.models_v2.summary_information_for_archival_run.SummaryInformationForArchivalRun.from_dictionary(dictionary.get('archivalInfo')) if dictionary.get('archivalInfo') else None
        cloud_spin_info = cohesity_management_sdk.models_v2.summary_information_for_cloud_spin_run.SummaryInformationForCloudSpinRun.from_dictionary(dictionary.get('cloudSpinInfo')) if dictionary.get('cloudSpinInfo') else None
        on_legal_hold = dictionary.get('onLegalHold')
        permissions = None
        if dictionary.get("permissions") is not None:
            permissions = list()
            for structure in dictionary.get('permissions'):
                permissions.append(cohesity_management_sdk.models_v2.tenant.Tenant.from_dictionary(structure))
        has_local_snapshot = dictionary.get('hasLocalSnapshot')
        environment = dictionary.get('environment')
        externally_triggered_backup_tag = dictionary.get('externallyTriggeredBackupTag')
        is_cloud_archival_direct = dictionary.get('isCloudArchivalDirect')

        # Return an object of this model
        return cls(id,
                   protection_group_instance_id,
                   protection_group_id,
                   is_replication_run,
                   origin_cluster_identifier,
                   origin_protection_group_id,
                   protection_group_name,
                   is_local_snapshots_deleted,
                   objects,
                   local_backup_info,
                   original_backup_info,
                   replication_info,
                   archival_info,
                   cloud_spin_info,
                   on_legal_hold,
                   permissions,
                   has_local_snapshot,
                   environment,
                   externally_triggered_backup_tag,
                   is_cloud_archival_direct)