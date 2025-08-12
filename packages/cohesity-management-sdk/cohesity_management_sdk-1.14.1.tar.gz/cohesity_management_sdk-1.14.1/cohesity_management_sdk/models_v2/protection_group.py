# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.time_of_day
import cohesity_management_sdk.models_v2.protection_group_alerting_policy
import cohesity_management_sdk.models_v2.sla_rule
import cohesity_management_sdk.models_v2.protection_group_run
import cohesity_management_sdk.models_v2.tenant
import cohesity_management_sdk.models_v2.common_protection_group_run_response_parameters
import cohesity_management_sdk.models_v2.key_value_pair
import cohesity_management_sdk.models_v2.missing_entity_params
import cohesity_management_sdk.models_v2.vmware_protection_group_params
import cohesity_management_sdk.models_v2.sfdc_protection_group_parameters
import cohesity_management_sdk.models_v2.mongodb_protection_group_params
import cohesity_management_sdk.models_v2.acropolis_protection_group_params
import cohesity_management_sdk.models_v2.kubernetes_protection_group_params
import cohesity_management_sdk.models_v2.uda_protection_group_params
import cohesity_management_sdk.models_v2.ibm_flash_system_protection_group_params
import cohesity_management_sdk.models_v2.mssql_protection_group_params
import cohesity_management_sdk.models_v2.oracle_protection_group_parameters
import cohesity_management_sdk.models_v2.view_protection_group_parameters
import cohesity_management_sdk.models_v2.pure_protection_group_params
import cohesity_management_sdk.models_v2.nimble_protection_group_params
import cohesity_management_sdk.models_v2.hyperv_protection_group_request_params
import cohesity_management_sdk.models_v2.aws_protection_group_request_params
import cohesity_management_sdk.models_v2.azure_protection_group_request_params
import cohesity_management_sdk.models_v2.gcp_protection_group_request_params
import cohesity_management_sdk.models_v2.kvm_protection_group_params
import cohesity_management_sdk.models_v2.physical_protection_group_params
import cohesity_management_sdk.models_v2.active_directory_ad_protection_group_parameters
import cohesity_management_sdk.models_v2.office_365_o_365_protection_group_parameters
import cohesity_management_sdk.models_v2.netapp_protection_group_params
import cohesity_management_sdk.models_v2.generic_nas_protection_group_params
import cohesity_management_sdk.models_v2.isilon_protection_group_params
import cohesity_management_sdk.models_v2.flashblade_protection_group_params
import cohesity_management_sdk.models_v2.gpfs_protection_group_params
import cohesity_management_sdk.models_v2.elastifile_protection_group_params
import cohesity_management_sdk.models_v2.remote_adapter_protection_group_parameters
import cohesity_management_sdk.models_v2.exchange_protection_group_parameters
import cohesity_management_sdk.models_v2.cassandra_protection_group_params
import cohesity_management_sdk.models_v2.no_sql_protection_group_params
import cohesity_management_sdk.models_v2.hdfs_protection_group_params

class ProtectionGroup(object):

    """Implementation of the 'ProtectionGroup' model.

    Protection Group  response.

    Attributes:
        advanced_configs (list of KeyValuePair): Specifies the advanced configuration for a protection job.
        cluster_id (string): Specifies the cluster ID.
        id (string): Specifies the ID of the Protection Group.
        name (string): Specifies the name of the Protection Group.
        policy_id (string): Specifies the unique id of the Protection Policy
            associated with the Protection Group. The Policy provides retry
            settings Protection Schedules, Priority, SLA, etc.
        priority (PriorityEnum): Specifies the priority of the Protection
            Group.
        storage_domain_id (long|int): Specifies the Storage Domain (View Box)
            ID where this Protection Group writes data.
        description (string): Specifies a description of the Protection
            Group.
        invalid_entities (list of MissingEntityParams): Specifies the Information about invalid entities. An entity will
          be considered invalid if it is part of an active protection group but has
          lost compatibility for the given backup type.
        start_time (TimeOfDay): Specifies the time of day. Used for scheduling
            purposes.
        end_time_usecs (long|int): Specifies the end time in micro seconds for
            this Protection Group. If this is not specified, the Protection
            Group won't be ended.
        last_modified_timestamp_usecs (long|int): Specifies the last time this
            protection group was updated. If this is passed into a PUT request,
            then the backend will validate that the timestamp passed in matches
            the time that the protection group was actually last modified. If
            the two timestamps do not match, then the request will be rejected
            with a stale error.
        alert_policy (ProtectionGroupAlertingPolicy): Specifies a policy for
            alerting users of the status of a Protection Group.
        sla (list of SlaRule): Specifies the SLA parameters for this
            Protection Group.
        pause_in_blackouts (bool): Specifies whether currently executing jobs should be paused if
          a blackout period specified by a policy starts. Available only if the selected
          policy has at least one blackout period. Default value is false. This field
          should not be set to true if 'abortInBlackouts' is sent as true.
        qos_policy (QosPolicy1Enum): Specifies whether the Protection Group
            will be written to HDD or SSD.
        abort_in_blackouts (bool): Specifies whether currently executing jobs
            should abort if a blackout period specified by a policy starts.
            Available only if the selected policy has at least one blackout
            period. Default value is false.
        is_active (bool): Specifies if the Protection Group is active or not.
        is_deleted (bool): Specifies if the Protection Group has been
            deleted.
        is_paused (bool): Specifies if the the Protection Group is paused. New
            runs are not scheduled for the paused Protection Groups. Active
            run if any is not impacted.
        environment (Environment7Enum): Specifies the environment of the
            Protection Group.
        last_run (ProtectionGroupRun): Specifies information about the last run for this Protection
          Group.
        num_protected_objects (long|int): Specifies the number of protected objects of the Protection Group.
        permissions (list of Tenant): Specifies the list of tenants that have
            permissions for this protection group.
        region_id (string): Specifies the region ID.
        is_protect_once (bool): Specifies if the the Protection Group is using
            a protect once type of policy. This field is helpful to identify
            run happen for this group.
        missing_entities (list of MissingEntityParams): Specifies the
            Information about missing entities.
        vmware_params (VmwareProtectionGroupParams): Specifies the parameters
            which are specific to VMware related Protection Groups.
        acropolis_params (AcropolisProtectionGroupParams): Specifies the
            parameters which are related to Acropolis Protection Groups.
        kubernetes_params (KubernetesProtectionGroupParams): Specifies the
            parameters which are related to Kubernetes Protection Groups.
        ibm_flash_system_params (IbmFlashSystemProtectionGroupParams):
            Specifies the parameters which are specific to IBM FlashSystem
            related Protection Groups.
        mssql_params (MSSQLProtectionGroupParams): Specifies the parameters
            specific to MSSQL Protection Group.
        oracle_params (OracleProtectionGroupParameters): Specifies the
            parameters to create Oracle Protection Group.
        view_params (ViewProtectionGroupParameters): Specifies the parameters
            which are specific to view related Protection Groups.
        pure_params (PureProtectionGroupParams): Specifies the parameters
            which are specific to Pure related Protection Groups.
        nimble_params (NimbleProtectionGroupParams): Specifies the parameters
            which are specific to Nimble related Protection Groups.
        hyperv_params (HypervProtectionGroupRequestParams): Specifies the
            parameters which are specific to HyperV related Protection
            Groups.
        aws_params (AWSProtectionGroupRequestParams): Specifies the parameters
            which are specific to AWS related Protection Groups.
        azure_params (AzureProtectionGroupRequestParams): Specifies the
            parameters which are specific to Azure related Protection Groups.
        gcp_params (GCPProtectionGroupRequestParams): Specifies the parameters
            which are specific to GCP related Protection Groups.
        kvm_params (KvmProtectionGroupParams): Specifies the parameters which
            are specific to Kvm related Protection Groups.
        physical_params (PhysicalProtectionGroupParams): Specifies the
            parameters specific to Physical Protection Group.
        ad_params (ActiveDirectoryADProtectionGroupParameters): Specifies the
            parameters which are specific to Active directory related
            Protection Groups.
        office_365_params (Office365O365ProtectionGroupParameters): Specifies
            the parameters which are specific to Office 365 related Protection
            Groups.
        netapp_params (NetappProtectionGroupParams): Specifies the parameters
            which are specific to Netapp related Protection Groups.
        generic_nas_params (GenericNasProtectionGroupParams): Specifies the
            parameters which are specific to NAS related Protection Groups.
        isilon_params (IsilonProtectionGroupParams): Specifies the parameters
            which are specific to Isilon related Protection Groups.
        flashblade_params (FlashbladeProtectionGroupParams): Specifies the
            parameters which are specific to Flashblade related Protection
            Groups.
        gpfs_params (GpfsProtectionGroupParams): Specifies the parameters
            which are specific to GPFS related Protection Groups.
        elastifile_params (ElastifileProtectionGroupParams): Specifies the
            parameters which are specific to Elastifile related Protection
            Groups.
        remote_adapter_params (RemoteAdapterProtectionGroupParameters):
            Specifies the parameters which are specific to Remote Adapter
            related Protection Groups.
        exchange_params (ExchangeProtectionGroupParameters): Specifies the
            parameters which are specific to Exchange related Protection
            Groups.
        cassandra_params (CassandraProtectionGroupParams): Specifies the
            parameters for Cassandra Protection Group.
        couchbase_params (NoSqlProtectionGroupParams): Specifies the source
            specific parameters for this Protection Group.
        mongodb_params (NoSqlProtectionGroupParams): Specifies the source
            specific parameters for this Protection Group.
        hive_params (NoSqlProtectionGroupParams): Specifies the source
            specific parameters for this Protection Group.
        hdfs_params (HdfsProtectionGroupParams): Specifies the parameters for
            HDFS Protection Group.
        hbase_params (NoSqlProtectionGroupParams): Specifies the source
            specific parameters for this Protection Group.
        sfdc_params (SfdcProtectionGroupParams): Specifies the parameters which are specific to SFDC Adapter
            related Protection Groups.
        uda_params (UdaProtectionGroupParams): Specifies parameters related to the Universal Data Adapter Protection
      job.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "advanced_configs": 'advancedConfigs',
        "cluster_id":'clusterId',
        "id":'id',
        "name":'name',
        "policy_id":'policyId',
        "priority":'priority',
        "storage_domain_id":'storageDomainId',
        "description":'description',
        "invalid_entities":'invalidEntities',
        "start_time":'startTime',
        "end_time_usecs":'endTimeUsecs',
        "last_modified_timestamp_usecs":'lastModifiedTimestampUsecs',
        "alert_policy":'alertPolicy',
        "sla":'sla',
        "pause_in_blackouts":'pauseInBlackouts',
        "qos_policy":'qosPolicy',
        "abort_in_blackouts":'abortInBlackouts',
        "is_active":'isActive',
        "is_deleted":'isDeleted',
        "is_paused":'isPaused',
        "environment":'environment',
        "last_run":'lastRun',
        "num_protected_objects":'numProtectedObjects',
        "permissions":'permissions',
        "region_id":'regionId',
        "is_protect_once":'isProtectOnce',
        "missing_entities":'missingEntities',
        "vmware_params":'vmwareParams',
        "acropolis_params":'acropolisParams',
        "kubernetes_params":'kubernetesParams',
        "ibm_flash_system_params":'ibmFlashSystemParams',
        "mssql_params":'mssqlParams',
        "oracle_params":'oracleParams',
        "view_params":'viewParams',
        "pure_params":'pureParams',
        "nimble_params":'nimbleParams',
        "hyperv_params":'hypervParams',
        "aws_params":'awsParams',
        "azure_params":'azureParams',
        "gcp_params":'gcpParams',
        "kvm_params":'kvmParams',
        "physical_params":'physicalParams',
        "ad_params":'adParams',
        "office_365_params":'office365Params',
        "netapp_params":'netappParams',
        "generic_nas_params":'genericNasParams',
        "isilon_params":'isilonParams',
        "flashblade_params":'flashbladeParams',
        "gpfs_params":'gpfsParams',
        "elastifile_params":'elastifileParams',
        "remote_adapter_params":'remoteAdapterParams',
        "exchange_params":'exchangeParams',
        "cassandra_params":'cassandraParams',
        "couchbase_params":'couchbaseParams',
        "mongodb_params":'mongodbParams',
        "hive_params":'hiveParams',
        "hdfs_params":'hdfsParams',
        "hbase_params":'hbaseParams',
        "sfdc_params":'sfdcParams',
        "uda_params":'udaParams'
    }

    def __init__(self,
                 advanced_configs=None,
                 cluster_id=None,
                 id=None,
                 name=None,
                 policy_id=None,
                 priority=None,
                 storage_domain_id=None,
                 description=None,
                 invalid_entities=None,
                 start_time=None,
                 end_time_usecs=None,
                 last_modified_timestamp_usecs=None,
                 alert_policy=None,
                 sla=None,
                 pause_in_blackouts=None,
                 qos_policy=None,
                 abort_in_blackouts=None,
                 is_active=None,
                 is_deleted=None,
                 is_paused=None,
                 environment=None,
                 last_run=None,
                 num_protected_objects=None,
                 permissions=None,
                 region_id=None,
                 is_protect_once=None,
                 missing_entities=None,
                 vmware_params=None,
                 acropolis_params=None,
                 kubernetes_params=None,
                 ibm_flash_system_params=None,
                 mssql_params=None,
                 oracle_params=None,
                 view_params=None,
                 pure_params=None,
                 nimble_params=None,
                 hyperv_params=None,
                 aws_params=None,
                 azure_params=None,
                 gcp_params=None,
                 kvm_params=None,
                 physical_params=None,
                 ad_params=None,
                 office_365_params=None,
                 netapp_params=None,
                 generic_nas_params=None,
                 isilon_params=None,
                 flashblade_params=None,
                 gpfs_params=None,
                 elastifile_params=None,
                 remote_adapter_params=None,
                 exchange_params=None,
                 cassandra_params=None,
                 couchbase_params=None,
                 mongodb_params=None,
                 hive_params=None,
                 hdfs_params=None,
                 hbase_params=None,
                 sfdc_params=None,
                 uda_params=None):
        """Constructor for the ProtectionGroup class"""

        # Initialize members of the class
        self.advanced_configs = advanced_configs
        self.cluster_id = cluster_id
        self.id = id
        self.name = name
        self.policy_id = policy_id
        self.priority = priority
        self.storage_domain_id = storage_domain_id
        self.description = description
        self.invalid_entities = invalid_entities
        self.start_time = start_time
        self.end_time_usecs = end_time_usecs
        self.last_modified_timestamp_usecs = last_modified_timestamp_usecs
        self.alert_policy = alert_policy
        self.sla = sla
        self.pause_in_blackouts = pause_in_blackouts
        self.qos_policy = qos_policy
        self.abort_in_blackouts = abort_in_blackouts
        self.is_active = is_active
        self.is_deleted = is_deleted
        self.is_paused = is_paused
        self.environment = environment
        self.last_run = last_run
        self.num_protected_objects = num_protected_objects
        self.permissions = permissions
        self.region_id = region_id
        self.is_protect_once = is_protect_once
        self.missing_entities = missing_entities
        self.vmware_params = vmware_params
        self.acropolis_params = acropolis_params
        self.kubernetes_params = kubernetes_params
        self.ibm_flash_system_params = ibm_flash_system_params
        self.mssql_params = mssql_params
        self.oracle_params = oracle_params
        self.view_params = view_params
        self.pure_params = pure_params
        self.nimble_params = nimble_params
        self.hyperv_params = hyperv_params
        self.aws_params = aws_params
        self.azure_params = azure_params
        self.gcp_params = gcp_params
        self.kvm_params = kvm_params
        self.physical_params = physical_params
        self.ad_params = ad_params
        self.office_365_params = office_365_params
        self.netapp_params = netapp_params
        self.generic_nas_params = generic_nas_params
        self.isilon_params = isilon_params
        self.flashblade_params = flashblade_params
        self.gpfs_params = gpfs_params
        self.elastifile_params = elastifile_params
        self.remote_adapter_params = remote_adapter_params
        self.exchange_params = exchange_params
        self.cassandra_params = cassandra_params
        self.couchbase_params = couchbase_params
        self.mongodb_params = mongodb_params
        self.hive_params = hive_params
        self.hdfs_params = hdfs_params
        self.hbase_params = hbase_params
        self.sfdc_params = sfdc_params
        self.uda_params = uda_params


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
        advanced_configs = None
        if dictionary.get("advancedConfigs") is not None:
            advanced_configs = list()
            for structure in dictionary.get('advancedConfigs'):
                advanced_configs.append(cohesity_management_sdk.models_v2.key_value_pair.KeyValuePair.from_dictionary(structure))
        cluster_id = dictionary.get('clusterId')
        id = dictionary.get('id')
        name = dictionary.get('name')
        policy_id = dictionary.get('policyId')
        priority = dictionary.get('priority')
        storage_domain_id = dictionary.get('storageDomainId')
        description = dictionary.get('description')
        invalid_entities = None
        if dictionary.get("invalidEntities") is not None:
            invalid_entities = list()
            for structure in dictionary.get('invalidEntities'):
                invalid_entities.append(cohesity_management_sdk.models_v2.missing_entity_params.MissingEntityParams.from_dictionary(structure))
        start_time = cohesity_management_sdk.models_v2.time_of_day.TimeOfDay.from_dictionary(dictionary.get('startTime')) if dictionary.get('startTime') else None
        end_time_usecs = dictionary.get('endTimeUsecs')
        last_modified_timestamp_usecs = dictionary.get('lastModifiedTimestampUsecs')
        alert_policy = cohesity_management_sdk.models_v2.protection_group_alerting_policy.ProtectionGroupAlertingPolicy.from_dictionary(dictionary.get('alertPolicy')) if dictionary.get('alertPolicy') else None
        pause_in_blackouts = dictionary.get('pauseInBlackouts')
        sla = None
        if dictionary.get("sla") is not None:
            sla = list()
            for structure in dictionary.get('sla'):
                sla.append(cohesity_management_sdk.models_v2.sla_rule.SlaRule.from_dictionary(structure))
        qos_policy = dictionary.get('qosPolicy')
        abort_in_blackouts = dictionary.get('abortInBlackouts')
        is_active = dictionary.get('isActive')
        is_deleted = dictionary.get('isDeleted')
        is_paused = dictionary.get('isPaused')
        environment = dictionary.get('environment')
        last_run = cohesity_management_sdk.models_v2.common_protection_group_run_response_parameters.CommonProtectionGroupRunResponseParameters.from_dictionary(dictionary.get('lastRun')) if dictionary.get('lastRun') else None
        num_protected_objects = dictionary.get('numProtectedObjects')
        permissions = None
        if dictionary.get("permissions") is not None:
            permissions = list()
            for structure in dictionary.get('permissions'):
                permissions.append(cohesity_management_sdk.models_v2.tenant.Tenant.from_dictionary(structure))
        region_id = dictionary.get('regionId')
        is_protect_once = dictionary.get('isProtectOnce')
        missing_entities = None
        if dictionary.get("missingEntities") is not None:
            missing_entities = list()
            for structure in dictionary.get('missingEntities'):
                missing_entities.append(cohesity_management_sdk.models_v2.missing_entity_params.MissingEntityParams.from_dictionary(structure))
        vmware_params = cohesity_management_sdk.models_v2.vmware_protection_group_params.VmwareProtectionGroupParams.from_dictionary(dictionary.get('vmwareParams')) if dictionary.get('vmwareParams') else None
        acropolis_params = cohesity_management_sdk.models_v2.acropolis_protection_group_params.AcropolisProtectionGroupParams.from_dictionary(dictionary.get('acropolisParams')) if dictionary.get('acropolisParams') else None
        kubernetes_params = cohesity_management_sdk.models_v2.kubernetes_protection_group_params.KubernetesProtectionGroupParams.from_dictionary(dictionary.get('kubernetesParams')) if dictionary.get('kubernetesParams') else None
        ibm_flash_system_params = cohesity_management_sdk.models_v2.ibm_flash_system_protection_group_params.IbmFlashSystemProtectionGroupParams.from_dictionary(dictionary.get('ibmFlashSystemParams')) if dictionary.get('ibmFlashSystemParams') else None
        mssql_params = cohesity_management_sdk.models_v2.mssql_protection_group_params.MSSQLProtectionGroupParams.from_dictionary(dictionary.get('mssqlParams')) if dictionary.get('mssqlParams') else None
        oracle_params = cohesity_management_sdk.models_v2.oracle_protection_group_parameters.OracleProtectionGroupParameters.from_dictionary(dictionary.get('oracleParams')) if dictionary.get('oracleParams') else None
        view_params = cohesity_management_sdk.models_v2.view_protection_group_parameters.ViewProtectionGroupParameters.from_dictionary(dictionary.get('viewParams')) if dictionary.get('viewParams') else None
        pure_params = cohesity_management_sdk.models_v2.pure_protection_group_params.PureProtectionGroupParams.from_dictionary(dictionary.get('pureParams')) if dictionary.get('pureParams') else None
        nimble_params = cohesity_management_sdk.models_v2.nimble_protection_group_params.NimbleProtectionGroupParams.from_dictionary(dictionary.get('nimbleParams')) if dictionary.get('nimbleParams') else None
        hyperv_params = cohesity_management_sdk.models_v2.hyperv_protection_group_request_params.HypervProtectionGroupRequestParams.from_dictionary(dictionary.get('hypervParams')) if dictionary.get('hypervParams') else None
        aws_params = cohesity_management_sdk.models_v2.aws_protection_group_request_params.AWSProtectionGroupRequestParams.from_dictionary(dictionary.get('awsParams')) if dictionary.get('awsParams') else None
        azure_params = cohesity_management_sdk.models_v2.azure_protection_group_request_params.AzureProtectionGroupRequestParams.from_dictionary(dictionary.get('azureParams')) if dictionary.get('azureParams') else None
        gcp_params = cohesity_management_sdk.models_v2.gcp_protection_group_request_params.GCPProtectionGroupRequestParams.from_dictionary(dictionary.get('gcpParams')) if dictionary.get('gcpParams') else None
        kvm_params = cohesity_management_sdk.models_v2.kvm_protection_group_params.KvmProtectionGroupParams.from_dictionary(dictionary.get('kvmParams')) if dictionary.get('kvmParams') else None
        physical_params = cohesity_management_sdk.models_v2.physical_protection_group_params.PhysicalProtectionGroupParams.from_dictionary(dictionary.get('physicalParams')) if dictionary.get('physicalParams') else None
        ad_params = cohesity_management_sdk.models_v2.active_directory_ad_protection_group_parameters.ActiveDirectoryADProtectionGroupParameters.from_dictionary(dictionary.get('adParams')) if dictionary.get('adParams') else None
        office_365_params = cohesity_management_sdk.models_v2.office_365_o_365_protection_group_parameters.Office365O365ProtectionGroupParameters.from_dictionary(dictionary.get('office365Params')) if dictionary.get('office365Params') else None
        netapp_params = cohesity_management_sdk.models_v2.netapp_protection_group_params.NetappProtectionGroupParams.from_dictionary(dictionary.get('netappParams')) if dictionary.get('netappParams') else None
        generic_nas_params = cohesity_management_sdk.models_v2.generic_nas_protection_group_params.GenericNasProtectionGroupParams.from_dictionary(dictionary.get('genericNasParams')) if dictionary.get('genericNasParams') else None
        isilon_params = cohesity_management_sdk.models_v2.isilon_protection_group_params.IsilonProtectionGroupParams.from_dictionary(dictionary.get('isilonParams')) if dictionary.get('isilonParams') else None
        flashblade_params = cohesity_management_sdk.models_v2.flashblade_protection_group_params.FlashbladeProtectionGroupParams.from_dictionary(dictionary.get('flashbladeParams')) if dictionary.get('flashbladeParams') else None
        gpfs_params = cohesity_management_sdk.models_v2.gpfs_protection_group_params.GpfsProtectionGroupParams.from_dictionary(dictionary.get('gpfsParams')) if dictionary.get('gpfsParams') else None
        elastifile_params = cohesity_management_sdk.models_v2.elastifile_protection_group_params.ElastifileProtectionGroupParams.from_dictionary(dictionary.get('elastifileParams')) if dictionary.get('elastifileParams') else None
        remote_adapter_params = cohesity_management_sdk.models_v2.remote_adapter_protection_group_parameters.RemoteAdapterProtectionGroupParameters.from_dictionary(dictionary.get('remoteAdapterParams')) if dictionary.get('remoteAdapterParams') else None
        exchange_params = cohesity_management_sdk.models_v2.exchange_protection_group_parameters.ExchangeProtectionGroupParameters.from_dictionary(dictionary.get('exchangeParams')) if dictionary.get('exchangeParams') else None
        cassandra_params = cohesity_management_sdk.models_v2.cassandra_protection_group_params.CassandraProtectionGroupParams.from_dictionary(dictionary.get('cassandraParams')) if dictionary.get('cassandraParams') else None
        couchbase_params = cohesity_management_sdk.models_v2.no_sql_protection_group_params.NoSqlProtectionGroupParams.from_dictionary(dictionary.get('couchbaseParams')) if dictionary.get('couchbaseParams') else None
        mongodb_params = cohesity_management_sdk.models_v2.mongodb_protection_group_params.MongoDBProtectionGroupParams.from_dictionary(dictionary.get('mongodbParams')) if dictionary.get('mongodbParams') else None
        hive_params = cohesity_management_sdk.models_v2.no_sql_protection_group_params.NoSqlProtectionGroupParams.from_dictionary(dictionary.get('hiveParams')) if dictionary.get('hiveParams') else None
        hdfs_params = cohesity_management_sdk.models_v2.hdfs_protection_group_params.HdfsProtectionGroupParams.from_dictionary(dictionary.get('hdfsParams')) if dictionary.get('hdfsParams') else None
        hbase_params = cohesity_management_sdk.models_v2.no_sql_protection_group_params.NoSqlProtectionGroupParams.from_dictionary(dictionary.get('hbaseParams')) if dictionary.get('hbaseParams') else None
        sfdc_params = cohesity_management_sdk.models_v2.sfdc_protection_group_parameters.SFDCProtectionGroupParameters.from_dictionary(dictionary.get('sfdcParams')) if dictionary.get('sfdcParams') else None
        uda_params = cohesity_management_sdk.models_v2.uda_protection_group_params.UdaProtectionGroupParams.from_dictionary(dictionary.get('udaParams')) if dictionary.get('udaParams') else None

        # Return an object of this model
        return cls(advanced_configs,
                   cluster_id,
                   id,
                   name,
                   policy_id,
                   priority,
                   storage_domain_id,
                   description,
                   invalid_entities,
                   start_time,
                   end_time_usecs,
                   last_modified_timestamp_usecs,
                   alert_policy,
                   sla,
                   pause_in_blackouts,
                   qos_policy,
                   abort_in_blackouts,
                   is_active,
                   is_deleted,
                   is_paused,
                   environment,
                   last_run,
                   num_protected_objects,
                   permissions,
                   region_id,
                   is_protect_once,
                   missing_entities,
                   vmware_params,
                   acropolis_params,
                   kubernetes_params,
                   ibm_flash_system_params,
                   mssql_params,
                   oracle_params,
                   view_params,
                   pure_params,
                   nimble_params,
                   hyperv_params,
                   aws_params,
                   azure_params,
                   gcp_params,
                   kvm_params,
                   physical_params,
                   ad_params,
                   office_365_params,
                   netapp_params,
                   generic_nas_params,
                   isilon_params,
                   flashblade_params,
                   gpfs_params,
                   elastifile_params,
                   remote_adapter_params,
                   exchange_params,
                   cassandra_params,
                   couchbase_params,
                   mongodb_params,
                   hive_params,
                   hdfs_params,
                   hbase_params,
                   sfdc_params,
                   uda_params)