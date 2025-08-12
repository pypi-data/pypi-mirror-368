# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.summary_information_for_archival_run
import cohesity_management_sdk.models_v2.summary_information_for_cloud_spin_run
import cohesity_management_sdk.models_v2.object_summary
import cohesity_management_sdk.models_v2.snapshot_run_information_for_an_object
import cohesity_management_sdk.models_v2.summary_information_for_replication_run

class SnapshotReplicationArchivalResultsForAnObject(object):

    """Implementation of the 'ObjectRunResult' model.

    Snapshot, replication, archival results for an object.

    Attributes:
        archival_info (SummaryInformationForArchivalRun.): Information about archival run for this object.
        cloud_spin_info (SummaryInformationForCloudSpinRun): Information about Cloud Spin run for this object.
        local_snapshot_info (SnapshotRunInformationForAnObject): Information about local snapshot run for this object.
        object (ObjectSummary): Summary information about the object.
        on_legal_hold (bool): Specifies if object's snapshot is on legal hold.
        original_backup_info (list of SnapshotRunInformationForAnObject): Information about snapshot run on the original cluster. This
          only applies to replication run.
        replication_info (list of SummaryInformationForReplicationRun): Information about replication run for this object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "archival_info":'archivalInfo',
        "cloud_spin_info":'cloudSpinInfo',
        "local_snapshot_info":'localSnapshotInfo',
        "object":'object',
        "on_legal_hold":'onLegalHold',
        "original_backup_info":'originalBackupInfo',
        "replication_info":'replicationInfo'
    }

    def __init__(self,
                 archival_info=None,
                 cloud_spin_info=None,
                 local_snapshot_info=None,
                 object=None,
                 on_legal_hold=None,
                 original_backup_info=None,
                 replication_info=None):
        """Constructor for the SnapshotReplicationArchivalResultsForAnObject class"""

        # Initialize members of the class
        self.archival_info = archival_info
        self.cloud_spin_info = cloud_spin_info
        self.local_snapshot_info = local_snapshot_info
        self.object = object
        self.on_legal_hold = on_legal_hold
        self.original_backup_info = original_backup_info
        self.replication_info = replication_info


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
        archival_info = cohesity_management_sdk.models_v2.summary_information_for_archival_run.SummaryInformationForArchivalRun.from_dictionary(dictionary.get('archivalInfo')) if dictionary.get('archivalInfo') else None
        cloud_spin_info = cohesity_management_sdk.models_v2.summary_information_for_cloud_spin_run.SummaryInformationForCloudSpinRun.from_dictionary(dictionary.get('cloudSpinInfo')) if dictionary.get('cloudSpinInfo') else None
        object = cohesity_management_sdk.models_v2.object_summary.ObjectSummary.from_dictionary(dictionary.get('object')) if dictionary.get('object') else None
        local_snapshot_info = cohesity_management_sdk.models_v2.snapshot_run_information_for_an_object.SnapshotRunInformationForAnObject.from_dictionary(dictionary.get('localSnapshotInfo')) if dictionary.get('localSnapshotInfo') else None
        original_backup_info = cohesity_management_sdk.models_v2.snapshot_run_information_for_an_object.SnapshotRunInformationForAnObject.from_dictionary(dictionary.get('originalBackupInfo')) if dictionary.get('originalBackupInfo') else None
        on_legal_hold = dictionary.get('onLegalHold')
        replication_info = cohesity_management_sdk.models_v2.summary_information_for_replication_run.SummaryInformationForReplicationRun.from_dictionary(dictionary.get('replicationInfo')) if dictionary.get('replicationInfo') else None

        # Return an object of this model
        return cls(archival_info,
                   cloud_spin_info,
                   local_snapshot_info,
                   object,
                   on_legal_hold,
                   original_backup_info,
                   replication_info)