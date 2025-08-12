# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.tenant
import cohesity_management_sdk.models_v2.cluster_identifier
import cohesity_management_sdk.models_v2.snapshot_run_information_for_an_object
import cohesity_management_sdk.models_v2.replication_run_information_for_an_object
import cohesity_management_sdk.models_v2.archival_run_information_for_an_object
import cohesity_management_sdk.models_v2.cloud_spin_run_information_for_an_object

class ObjectProtectionRunSummary(object):

    """Implementation of the 'Object Protection Run Summary.' model.

    Specifies the response body of the get object runs request.

    Attributes:
        id (long|int): Specifies object id.
        name (string): Specifies the name of the object.
        source_id (long|int): Specifies registered source id to which object
            belongs.
        source_name (string): Specifies registered source name to which object
            belongs.
        environment (EnvironmentEnum): Specifies the environment of the
            object.
        run_id (string): Specifies the ID of the protection run.
        run_type (RunType7Enum): Type of Protection run. 'kRegular' indicates
            an incremental (CBT) backup. Incremental backups utilizing CBT (if
            supported) are captured of the target protection objects. The
            first run of a kRegular schedule captures all the blocks. 'kFull'
            indicates a full (no CBT) backup. A complete backup (all blocks)
            of the target protection objects are always captured and Change
            Block Tracking (CBT) is not utilized. 'kLog' indicates a Database
            Log backup. Capture the database transaction logs to allow rolling
            back to a specific point in time. 'kSystem' indicates system
            volume backup. It produces an image for bare metal recovery.
        is_sla_violated (bool): Indicated if SLA has been violated for this
            run.
        protection_group_id (string): ProtectionGroupId to which this run
            belongs. This will only be populated if the object is protected by
            a protection group.
        protection_group_name (string): Name of the Protection Group to which
            this run belongs. This will only be populated if the object is
            protected by a protection group.
        is_local_snapshots_deleted (bool): Specifies if snapshots for this run
            has been deleted.
        is_replication_run (bool): Specifies if this protection run is a
            replication run.
        is_cloud_archival_direct (bool): Specifies whether the run is a CAD
            run if cloud archive direct feature is enabled. If this field is
            true, the primary backup copy will only be available at the given
            archived location.
        policy_id (string): Specifies the unique id of the Protection Policy
            associated with the Protection Run. The Policy provides retry
            settings Protection Schedules, Priority, SLA, etc.
        policy_name (string): Specifies Specifies the name of the Protection
            Policy.
        storage_domain_id (long|int): Specifies the Storage Domain (View Box)
            ID where this Protection Run writes data.
        permissions (list of Tenant): Specifies the list of tenants that have
            permissions for this protection group run.
        origin_cluster_identifier (ClusterIdentifier): Specifies the
            information about a cluster.
        origin_protection_group_id (string): ProtectionGroupId to which this
            run belongs on the primary cluster if this run is a replication
            run.
        local_snapshot_info (SnapshotRunInformationForAnObject): Specifies
            information about backup run for an object.
        original_backup_info (SnapshotRunInformationForAnObject): Specifies
            information about backup run for an object.
        replication_info (ReplicationRunInformationForAnObject): Specifies
            information about replication run for an object.
        archival_info (ArchivalRunInformationForAnObject): Specifies
            information about archival run for an object.
        cloud_spin_info (CloudSpinRunInformationForAnObject): Specifies
            information about Cloud Spin run for an object.
        on_legal_hold (bool): Specifies if object's snapshot is on legal
            hold.
        data_lock (DataLockEnum): Specifies WORM retention type for the local
            backeup. When a WORM retention type is specified, the snapshots of
            the Protection Groups using this policy will be kept until the
            maximum of the snapshot retention time. During that time, the
            snapshots cannot be deleted.  'Compliance' implies WORM retention
            is set for compliance reason.  'Administrative' implies WORM
            retention is set for administrative purposes.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "source_id":'sourceId',
        "source_name":'sourceName',
        "environment":'environment',
        "run_id":'runId',
        "run_type":'runType',
        "is_sla_violated":'isSlaViolated',
        "protection_group_id":'protectionGroupId',
        "protection_group_name":'protectionGroupName',
        "is_local_snapshots_deleted":'isLocalSnapshotsDeleted',
        "is_replication_run":'isReplicationRun',
        "is_cloud_archival_direct":'isCloudArchivalDirect',
        "policy_id":'policyId',
        "policy_name":'policyName',
        "storage_domain_id":'storageDomainId',
        "permissions":'permissions',
        "origin_cluster_identifier":'originClusterIdentifier',
        "origin_protection_group_id":'originProtectionGroupId',
        "local_snapshot_info":'localSnapshotInfo',
        "original_backup_info":'originalBackupInfo',
        "replication_info":'replicationInfo',
        "archival_info":'archivalInfo',
        "cloud_spin_info":'cloudSpinInfo',
        "on_legal_hold":'onLegalHold',
        "data_lock":'dataLock'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 source_id=None,
                 source_name=None,
                 environment=None,
                 run_id=None,
                 run_type=None,
                 is_sla_violated=None,
                 protection_group_id=None,
                 protection_group_name=None,
                 is_local_snapshots_deleted=None,
                 is_replication_run=None,
                 is_cloud_archival_direct=None,
                 policy_id=None,
                 policy_name=None,
                 storage_domain_id=None,
                 permissions=None,
                 origin_cluster_identifier=None,
                 origin_protection_group_id=None,
                 local_snapshot_info=None,
                 original_backup_info=None,
                 replication_info=None,
                 archival_info=None,
                 cloud_spin_info=None,
                 on_legal_hold=None,
                 data_lock=None):
        """Constructor for the ObjectProtectionRunSummary class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.source_id = source_id
        self.source_name = source_name
        self.environment = environment
        self.run_id = run_id
        self.run_type = run_type
        self.is_sla_violated = is_sla_violated
        self.protection_group_id = protection_group_id
        self.protection_group_name = protection_group_name
        self.is_local_snapshots_deleted = is_local_snapshots_deleted
        self.is_replication_run = is_replication_run
        self.is_cloud_archival_direct = is_cloud_archival_direct
        self.policy_id = policy_id
        self.policy_name = policy_name
        self.storage_domain_id = storage_domain_id
        self.permissions = permissions
        self.origin_cluster_identifier = origin_cluster_identifier
        self.origin_protection_group_id = origin_protection_group_id
        self.local_snapshot_info = local_snapshot_info
        self.original_backup_info = original_backup_info
        self.replication_info = replication_info
        self.archival_info = archival_info
        self.cloud_spin_info = cloud_spin_info
        self.on_legal_hold = on_legal_hold
        self.data_lock = data_lock


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
        name = dictionary.get('name')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        environment = dictionary.get('environment')
        run_id = dictionary.get('runId')
        run_type = dictionary.get('runType')
        is_sla_violated = dictionary.get('isSlaViolated')
        protection_group_id = dictionary.get('protectionGroupId')
        protection_group_name = dictionary.get('protectionGroupName')
        is_local_snapshots_deleted = dictionary.get('isLocalSnapshotsDeleted')
        is_replication_run = dictionary.get('isReplicationRun')
        is_cloud_archival_direct = dictionary.get('isCloudArchivalDirect')
        policy_id = dictionary.get('policyId')
        policy_name = dictionary.get('policyName')
        storage_domain_id = dictionary.get('storageDomainId')
        permissions = None
        if dictionary.get("permissions") is not None:
            permissions = list()
            for structure in dictionary.get('permissions'):
                permissions.append(cohesity_management_sdk.models_v2.tenant.Tenant.from_dictionary(structure))
        origin_cluster_identifier = cohesity_management_sdk.models_v2.cluster_identifier.ClusterIdentifier.from_dictionary(dictionary.get('originClusterIdentifier')) if dictionary.get('originClusterIdentifier') else None
        origin_protection_group_id = dictionary.get('originProtectionGroupId')
        local_snapshot_info = cohesity_management_sdk.models_v2.snapshot_run_information_for_an_object.SnapshotRunInformationForAnObject.from_dictionary(dictionary.get('localSnapshotInfo')) if dictionary.get('localSnapshotInfo') else None
        original_backup_info = cohesity_management_sdk.models_v2.snapshot_run_information_for_an_object.SnapshotRunInformationForAnObject.from_dictionary(dictionary.get('originalBackupInfo')) if dictionary.get('originalBackupInfo') else None
        replication_info = cohesity_management_sdk.models_v2.replication_run_information_for_an_object.ReplicationRunInformationForAnObject.from_dictionary(dictionary.get('replicationInfo')) if dictionary.get('replicationInfo') else None
        archival_info = cohesity_management_sdk.models_v2.archival_run_information_for_an_object.ArchivalRunInformationForAnObject.from_dictionary(dictionary.get('archivalInfo')) if dictionary.get('archivalInfo') else None
        cloud_spin_info = cohesity_management_sdk.models_v2.cloud_spin_run_information_for_an_object.CloudSpinRunInformationForAnObject.from_dictionary(dictionary.get('cloudSpinInfo')) if dictionary.get('cloudSpinInfo') else None
        on_legal_hold = dictionary.get('onLegalHold')
        data_lock = dictionary.get('dataLock')

        # Return an object of this model
        return cls(id,
                   name,
                   source_id,
                   source_name,
                   environment,
                   run_id,
                   run_type,
                   is_sla_violated,
                   protection_group_id,
                   protection_group_name,
                   is_local_snapshots_deleted,
                   is_replication_run,
                   is_cloud_archival_direct,
                   policy_id,
                   policy_name,
                   storage_domain_id,
                   permissions,
                   origin_cluster_identifier,
                   origin_protection_group_id,
                   local_snapshot_info,
                   original_backup_info,
                   replication_info,
                   archival_info,
                   cloud_spin_info,
                   on_legal_hold,
                   data_lock)


