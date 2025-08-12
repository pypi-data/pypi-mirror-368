# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.external_target_info
import cohesity_management_sdk.models_v2.physical_params
import cohesity_management_sdk.models_v2.hyperv_params
import cohesity_management_sdk.models_v2.aws_params
import cohesity_management_sdk.models_v2.azure_params
import cohesity_management_sdk.models_v2.netapp_params
import cohesity_management_sdk.models_v2.isilon_params
import cohesity_management_sdk.models_v2.gpfs_params
import cohesity_management_sdk.models_v2.flashblade_params_3
import cohesity_management_sdk.models_v2.generic_nas_params
import cohesity_management_sdk.models_v2.elastifile_params

class ObjectSnapshot(object):

    """Implementation of the 'Object Snapshot.' model.

    Specifies an Object Snapshot.

    Attributes:
        id (string): Specifies the id of the snapshot.
        snapshot_target_type (SnapshotTargetType1Enum): Specifies the target
            type where the Object's snapshot resides.
        indexing_status (IndexingStatusEnum): Specifies the indexing status of
            objects in this snapshot.<br> 'InProgress' indicates the indexing
            is in progress.<br> 'Done' indicates indexing is done.<br>
            'NoIndex' indicates indexing is not applicable.<br> 'Error'
            indicates indexing failed with error.
        protection_group_id (string): Specifies id of the Protection Group.
        protection_group_name (string): Specifies name of the Protection
            Group.
        protection_group_run_id (string): Specifies id of the Protection Group
            Run.
        run_instance_id (long|int): Specifies the instance id of the
            protection run which create the snapshot.
        run_start_time_usecs (long|int): Specifies the start time of the run
            in micro seconds.
        source_group_id (string): Specifies the source protection group id in
            case of replication.
        run_type (RunType1Enum): Specifies the type of protection run created
            this snapshot.
        environment (Environment11Enum): Specifies the snapshot environment.
        snapshot_timestamp_usecs (long|int): Specifies the timestamp in Unix
            time epoch in microseconds when the snapshot is taken for the
            specified Object.
        expiry_time_usecs (long|int): Specifies the expiry time of the
            snapshot in Unix timestamp epoch in microseconds. If the snapshot
            has no expiry, this property will not be set.
        external_target_info (ExternalTargetInfo): Specifies the external
            target information if this is an archival snapshot.
        storage_domain_id (long|int): Specifies the Storage Domain id where
            the snapshot of object is present.
        has_data_lock (bool): Specifies if this snapshot has datalock.
        on_legal_hold (bool): Specifies if this snapshot is on legalhold.
        object_id (long|int): Specifies the object id which the snapshot is
            taken from.
        object_name (string): Specifies the object name which the snapshot is
            taken from.
        source_id (long|int): Specifies the object source id which the
            snapshot is taken from.
        physical_params (PhysicalParams): Specifies the parameters specific to
            Physical type snapshot.
        hyperv_params (HypervParams): Specifies the parameters specific to
            HyperV type snapshot.
        aws_params (AwsParams): Specifies the parameters specific to AWS type
            snapshot.
        azure_params (AzureParams): Specifies the parameters specific to Azure
            type snapshot.
        netapp_params (NetappParams): Specifies the parameters specific to
            NetApp type snapshot.
        isilon_params (IsilonParams): Specifies the parameters specific to
            Isilon type snapshot.
        gpfs_params (GpfsParams): Specifies the parameters specific to GPFS
            type snapshot.
        flashblade_params (FlashbladeParams3): Specifies the parameters
            specific to Flashblade type snapshot.
        generic_nas_params (GenericNasParams): Specifies the parameters
            specific to Generic NAS type snapshot.
        elastifile_params (ElastifileParams): Specifies the parameters
            specific to NetApp type snapshot.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "snapshot_target_type":'snapshotTargetType',
        "indexing_status":'indexingStatus',
        "protection_group_id":'protectionGroupId',
        "protection_group_name":'protectionGroupName',
        "protection_group_run_id":'protectionGroupRunId',
        "run_instance_id":'runInstanceId',
        "run_start_time_usecs":'runStartTimeUsecs',
        "source_group_id":'sourceGroupId',
        "run_type":'runType',
        "environment":'environment',
        "snapshot_timestamp_usecs":'snapshotTimestampUsecs',
        "expiry_time_usecs":'expiryTimeUsecs',
        "external_target_info":'externalTargetInfo',
        "storage_domain_id":'storageDomainId',
        "has_data_lock":'hasDataLock',
        "on_legal_hold":'onLegalHold',
        "object_id":'objectId',
        "object_name":'objectName',
        "source_id":'sourceId',
        "physical_params":'physicalParams',
        "hyperv_params":'hypervParams',
        "aws_params":'awsParams',
        "azure_params":'azureParams',
        "netapp_params":'netappParams',
        "isilon_params":'isilonParams',
        "gpfs_params":'gpfsParams',
        "flashblade_params":'flashbladeParams',
        "generic_nas_params":'genericNasParams',
        "elastifile_params":'elastifileParams'
    }

    def __init__(self,
                 id=None,
                 snapshot_target_type=None,
                 indexing_status=None,
                 protection_group_id=None,
                 protection_group_name=None,
                 protection_group_run_id=None,
                 run_instance_id=None,
                 run_start_time_usecs=None,
                 source_group_id=None,
                 run_type=None,
                 environment=None,
                 snapshot_timestamp_usecs=None,
                 expiry_time_usecs=None,
                 external_target_info=None,
                 storage_domain_id=None,
                 has_data_lock=None,
                 on_legal_hold=None,
                 object_id=None,
                 object_name=None,
                 source_id=None,
                 physical_params=None,
                 hyperv_params=None,
                 aws_params=None,
                 azure_params=None,
                 netapp_params=None,
                 isilon_params=None,
                 gpfs_params=None,
                 flashblade_params=None,
                 generic_nas_params=None,
                 elastifile_params=None):
        """Constructor for the ObjectSnapshot class"""

        # Initialize members of the class
        self.id = id
        self.snapshot_target_type = snapshot_target_type
        self.indexing_status = indexing_status
        self.protection_group_id = protection_group_id
        self.protection_group_name = protection_group_name
        self.protection_group_run_id = protection_group_run_id
        self.run_instance_id = run_instance_id
        self.run_start_time_usecs = run_start_time_usecs
        self.source_group_id = source_group_id
        self.run_type = run_type
        self.environment = environment
        self.snapshot_timestamp_usecs = snapshot_timestamp_usecs
        self.expiry_time_usecs = expiry_time_usecs
        self.external_target_info = external_target_info
        self.storage_domain_id = storage_domain_id
        self.has_data_lock = has_data_lock
        self.on_legal_hold = on_legal_hold
        self.object_id = object_id
        self.object_name = object_name
        self.source_id = source_id
        self.physical_params = physical_params
        self.hyperv_params = hyperv_params
        self.aws_params = aws_params
        self.azure_params = azure_params
        self.netapp_params = netapp_params
        self.isilon_params = isilon_params
        self.gpfs_params = gpfs_params
        self.flashblade_params = flashblade_params
        self.generic_nas_params = generic_nas_params
        self.elastifile_params = elastifile_params


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
        snapshot_target_type = dictionary.get('snapshotTargetType')
        indexing_status = dictionary.get('indexingStatus')
        protection_group_id = dictionary.get('protectionGroupId')
        protection_group_name = dictionary.get('protectionGroupName')
        protection_group_run_id = dictionary.get('protectionGroupRunId')
        run_instance_id = dictionary.get('runInstanceId')
        run_start_time_usecs = dictionary.get('runStartTimeUsecs')
        source_group_id = dictionary.get('sourceGroupId')
        run_type = dictionary.get('runType')
        environment = dictionary.get('environment')
        snapshot_timestamp_usecs = dictionary.get('snapshotTimestampUsecs')
        expiry_time_usecs = dictionary.get('expiryTimeUsecs')
        external_target_info = cohesity_management_sdk.models_v2.external_target_info.ExternalTargetInfo.from_dictionary(dictionary.get('externalTargetInfo')) if dictionary.get('externalTargetInfo') else None
        storage_domain_id = dictionary.get('storageDomainId')
        has_data_lock = dictionary.get('hasDataLock')
        on_legal_hold = dictionary.get('onLegalHold')
        object_id = dictionary.get('objectId')
        object_name = dictionary.get('objectName')
        source_id = dictionary.get('sourceId')
        physical_params = cohesity_management_sdk.models_v2.physical_params.PhysicalParams.from_dictionary(dictionary.get('physicalParams')) if dictionary.get('physicalParams') else None
        hyperv_params = cohesity_management_sdk.models_v2.hyperv_params.HypervParams.from_dictionary(dictionary.get('hypervParams')) if dictionary.get('hypervParams') else None
        aws_params = cohesity_management_sdk.models_v2.aws_params.AwsParams.from_dictionary(dictionary.get('awsParams')) if dictionary.get('awsParams') else None
        azure_params = cohesity_management_sdk.models_v2.azure_params.AzureParams.from_dictionary(dictionary.get('azureParams')) if dictionary.get('azureParams') else None
        netapp_params = cohesity_management_sdk.models_v2.netapp_params.NetappParams.from_dictionary(dictionary.get('netappParams')) if dictionary.get('netappParams') else None
        isilon_params = cohesity_management_sdk.models_v2.isilon_params.IsilonParams.from_dictionary(dictionary.get('isilonParams')) if dictionary.get('isilonParams') else None
        gpfs_params = cohesity_management_sdk.models_v2.gpfs_params.GpfsParams.from_dictionary(dictionary.get('gpfsParams')) if dictionary.get('gpfsParams') else None
        flashblade_params = cohesity_management_sdk.models_v2.flashblade_params_3.FlashbladeParams3.from_dictionary(dictionary.get('flashbladeParams')) if dictionary.get('flashbladeParams') else None
        generic_nas_params = cohesity_management_sdk.models_v2.generic_nas_params.GenericNasParams.from_dictionary(dictionary.get('genericNasParams')) if dictionary.get('genericNasParams') else None
        elastifile_params = cohesity_management_sdk.models_v2.elastifile_params.ElastifileParams.from_dictionary(dictionary.get('elastifileParams')) if dictionary.get('elastifileParams') else None

        # Return an object of this model
        return cls(id,
                   snapshot_target_type,
                   indexing_status,
                   protection_group_id,
                   protection_group_name,
                   protection_group_run_id,
                   run_instance_id,
                   run_start_time_usecs,
                   source_group_id,
                   run_type,
                   environment,
                   snapshot_timestamp_usecs,
                   expiry_time_usecs,
                   external_target_info,
                   storage_domain_id,
                   has_data_lock,
                   on_legal_hold,
                   object_id,
                   object_name,
                   source_id,
                   physical_params,
                   hyperv_params,
                   aws_params,
                   azure_params,
                   netapp_params,
                   isilon_params,
                   gpfs_params,
                   flashblade_params,
                   generic_nas_params,
                   elastifile_params)


