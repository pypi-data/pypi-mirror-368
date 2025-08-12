# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_vmware_environment_params
import cohesity_management_sdk.models_v2.recover_aws_environment_params
import cohesity_management_sdk.models_v2.recover_universal_data_adapter_environment_params
import cohesity_management_sdk.models_v2.recover_gcp_environment_params
import cohesity_management_sdk.models_v2.recover_azure_environment_params
import cohesity_management_sdk.models_v2.recover_kvm_environment_params
import cohesity_management_sdk.models_v2.recover_vm_params
import cohesity_management_sdk.models_v2.recover_sql_environment_params
import cohesity_management_sdk.models_v2.recover_netapp_params
import cohesity_management_sdk.models_v2.recover_generic_nas_params
import cohesity_management_sdk.models_v2.recover_isilon_params
import cohesity_management_sdk.models_v2.recover_pure_params
import cohesity_management_sdk.models_v2.recover_flashblade_params
import cohesity_management_sdk.models_v2.recover_oracle_environment_params
import cohesity_management_sdk.models_v2.recover_elastifile_params
import cohesity_management_sdk.models_v2.recover_gpfs_params
import cohesity_management_sdk.models_v2.recover_salesforce_environment_params
import cohesity_management_sdk.models_v2.recover_physical_environment_params
import cohesity_management_sdk.models_v2.recover_hyperv_environment_params
import cohesity_management_sdk.models_v2.recover_exchange_environment_params
import cohesity_management_sdk.models_v2.recover_pure_params
import cohesity_management_sdk.models_v2.recover_kubernetes_environment_params
import cohesity_management_sdk.models_v2.recover_office_365_environment_params
import cohesity_management_sdk.models_v2.recover_cassandra_environment_params
import cohesity_management_sdk.models_v2.recover_couchbase_environment_params
import cohesity_management_sdk.models_v2.recover_hbase_environment_params
import cohesity_management_sdk.models_v2.recover_hdfs_environment_params
import cohesity_management_sdk.models_v2.recover_hive_environment_params
import cohesity_management_sdk.models_v2.recover_mongo_db_environment_params
import cohesity_management_sdk.models_v2.recover_view_environment_params

class CreateRecoveryRequestParams(object):

    """Implementation of the 'Create Recovery request params.' model.

    Specifies the request parameters to create a Recovery.

    Attributes:
        name (string): Specifies the name of the Recovery.
        snapshot_environment (SnapshotEnvironmentEnum): Specifies the type of
            environment of snapshots for which the Recovery has to be
            performed.
        vmware_params (RecoverVmwareEnvironmentParams): Specifies the recovery
            options specific to VMware environment.
        aws_params (RecoverAWSEnvironmentParams): Specifies the recovery
            options specific to AWS environment.
        gcp_params (RecoverGCPEnvironmentParams): Specifies the recovery
            options specific to GCP environment.
        azure_params (RecoverAzureEnvironmentParams): Specifies the recovery
            options specific to Azure environment.
        kvm_params (RecoverKVMEnvironmentParams): Specifies the recovery
            options specific to KVM environment.
        acropolis_params (RecoverVMParams): Specifies Acropolis related
            recovery options.
        mssql_params (RecoverSqlEnvironmentParams): Specifies the recovery
            options specific to Sql environment.
        netapp_params (RecoverNetappParams): Specifies the recovery options
            specific to Netapp environment.
        generic_nas_params (RecoverGenericNASParams): Specifies the recovery
            options specific to Generic NAS environment.
        ibm_flash_system_params (RecoverPureParams): Specifies the parameters which are specific to Ibm FlashSystem
            related Recovery.
        isilon_params (RecoverIsilonParams): Specifies the recovery options
            specific to Isilon environment.
        flashblade_params (RecoverFlashbladeParams): Specifies the recovery
            options specific to Flashblade environment.
        elastifile_params (RecoverElastifileParams): Specifies the recovery
            options specific to Elastifile environment.
        gpfs_params (RecoverGPFSParams): Specifies the recovery options
            specific to GPFS environment.
        physical_params (RecoverPhysicalEnvironmentParams): Specifies the
            recovery options specific to Physical environment.
        hyperv_params (RecoverHypervEnvironmentParams): Specifies the recovery
            options specific to HyperV environment.
        exchange_params (RecoverExchangeEnvironmentParams): Specifies the
            recovery options specific to Exchange environment.
        pure_params (RecoverPureParams): Specifies the recovery options
            specific to Pure environment.
        kubernetes_params (RecoverKubernetesEnvironmentParams): Specifies the
            recovery options specific to Kubernetes environment.
        office_365_params (RecoverOffice365EnvironmentParams): Specifies the
            recovery options specific to Office 365 environment.
        cassandra_params (RecoverCassandraEnvironmentParams): Specifies the
            recovery options specific to Cassandra environment.
        couchbase_params (RecoverCouchbaseEnvironmentParams): Specifies the
            recovery options specific to Couchbase environment.
        hbase_params (RecoverHbaseEnvironmentParams): Specifies the recovery
            options specific to Hbase environment.
        hdfs_params (RecoverHDFSEnvironmentParams): Specifies the recovery
            options specific to HDFS environment.
        hive_params (RecoverHiveEnvironmentParams): Specifies the recovery
            options specific to Hive environment.
        mongodb_params (RecoverMongoDBEnvironmentParams): Specifies the
            recovery options specific to MongoDB environment.
        oracle_params (RecoverOracleEnvironmentParams): Specifies the parameters which are specific to Oracle related
            Recovery.
        sfdc_params (RecoverSalesforceEnvironmentParams): Specifies the recovery options specific to Salesforce environment.
        uda_params (RecoverUniversalDataAdapterEnvironmentParams): Specifies the recovery options specific to Universal Data Adapter
      environment.
        view_params (RecoverViewEnvironmentParams): Specifies the recovery options specific to View environment.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "snapshot_environment":'snapshotEnvironment',
        "vmware_params":'vmwareParams',
        "aws_params":'awsParams',
        "gcp_params":'gcpParams',
        "azure_params":'azureParams',
        "kvm_params":'kvmParams',
        "acropolis_params":'acropolisParams',
        "mssql_params":'mssqlParams',
        "netapp_params":'netappParams',
        "generic_nas_params":'genericNasParams',
        "isilon_params":'isilonParams',
        "ibm_flash_system_params":'ibmFlashSystemParams',
        "flashblade_params":'flashbladeParams',
        "elastifile_params":'elastifileParams',
        "gpfs_params":'gpfsParams',
        "physical_params":'physicalParams',
        "hyperv_params":'hypervParams',
        "exchange_params":'exchangeParams',
        "pure_params":'pureParams',
        "kubernetes_params":'kubernetesParams',
        "office_365_params":'office365Params',
        "cassandra_params":'cassandraParams',
        "couchbase_params":'couchbaseParams',
        "hbase_params":'hbaseParams',
        "hdfs_params":'hdfsParams',
        "hive_params":'hiveParams',
        "mongodb_params":'mongodbParams',
        "oracle_params":'oracleParams',
        "sfdc_params":'sfdcParams',
        "uda_params":'udaParams',
        "view_params":'viewParams'
    }

    def __init__(self,
                 name=None,
                 snapshot_environment=None,
                 vmware_params=None,
                 aws_params=None,
                 gcp_params=None,
                 azure_params=None,
                 kvm_params=None,
                 acropolis_params=None,
                 mssql_params=None,
                 netapp_params=None,
                 generic_nas_params=None,
                 isilon_params=None,
                 ibm_flash_system_params=None,
                 flashblade_params=None,
                 elastifile_params=None,
                 gpfs_params=None,
                 physical_params=None,
                 hyperv_params=None,
                 exchange_params=None,
                 pure_params=None,
                 kubernetes_params=None,
                 office_365_params=None,
                 cassandra_params=None,
                 couchbase_params=None,
                 hbase_params=None,
                 hdfs_params=None,
                 hive_params=None,
                 mongodb_params=None,
                 oracle_params=None,
                 sfdc_params=None,
                 uda_params=None,
                 view_params=None):
        """Constructor for the CreateRecoveryRequestParams class"""

        # Initialize members of the class
        self.name = name
        self.snapshot_environment = snapshot_environment
        self.vmware_params = vmware_params
        self.aws_params = aws_params
        self.gcp_params = gcp_params
        self.azure_params = azure_params
        self.kvm_params = kvm_params
        self.acropolis_params = acropolis_params
        self.mssql_params = mssql_params
        self.netapp_params = netapp_params
        self.generic_nas_params = generic_nas_params
        self.isilon_params = isilon_params
        self.ibm_flash_system_params = ibm_flash_system_params
        self.flashblade_params = flashblade_params
        self.elastifile_params = elastifile_params
        self.gpfs_params = gpfs_params
        self.physical_params = physical_params
        self.hyperv_params = hyperv_params
        self.exchange_params = exchange_params
        self.pure_params = pure_params
        self.kubernetes_params = kubernetes_params
        self.office_365_params = office_365_params
        self.cassandra_params = cassandra_params
        self.couchbase_params = couchbase_params
        self.hbase_params = hbase_params
        self.hdfs_params = hdfs_params
        self.hive_params = hive_params
        self.mongodb_params = mongodb_params
        self.oracle_params = oracle_params
        self.sfdc_params = sfdc_params
        self.uda_params = uda_params
        self.view_params = view_params


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
        name = dictionary.get('name')
        snapshot_environment = dictionary.get('snapshotEnvironment')
        vmware_params = cohesity_management_sdk.models_v2.recover_vmware_environment_params.RecoverVmwareEnvironmentParams.from_dictionary(dictionary.get('vmwareParams')) if dictionary.get('vmwareParams') else None
        aws_params = cohesity_management_sdk.models_v2.recover_aws_environment_params.RecoverAWSEnvironmentParams.from_dictionary(dictionary.get('awsParams')) if dictionary.get('awsParams') else None
        gcp_params = cohesity_management_sdk.models_v2.recover_gcp_environment_params.RecoverGCPEnvironmentParams.from_dictionary(dictionary.get('gcpParams')) if dictionary.get('gcpParams') else None
        azure_params = cohesity_management_sdk.models_v2.recover_azure_environment_params.RecoverAzureEnvironmentParams.from_dictionary(dictionary.get('azureParams')) if dictionary.get('azureParams') else None
        kvm_params = cohesity_management_sdk.models_v2.recover_kvm_environment_params.RecoverKVMEnvironmentParams.from_dictionary(dictionary.get('kvmParams')) if dictionary.get('kvmParams') else None
        acropolis_params = cohesity_management_sdk.models_v2.recover_vm_params.RecoverVMParams.from_dictionary(dictionary.get('acropolisParams')) if dictionary.get('acropolisParams') else None
        mssql_params = cohesity_management_sdk.models_v2.recover_sql_environment_params.RecoverSqlEnvironmentParams.from_dictionary(dictionary.get('mssqlParams')) if dictionary.get('mssqlParams') else None
        netapp_params = cohesity_management_sdk.models_v2.recover_netapp_params.RecoverNetappParams.from_dictionary(dictionary.get('netappParams')) if dictionary.get('netappParams') else None
        generic_nas_params = cohesity_management_sdk.models_v2.recover_generic_nas_params.RecoverGenericNASParams.from_dictionary(dictionary.get('genericNasParams')) if dictionary.get('genericNasParams') else None
        isilon_params = cohesity_management_sdk.models_v2.recover_isilon_params.RecoverIsilonParams.from_dictionary(dictionary.get('isilonParams')) if dictionary.get('isilonParams') else None
        ibm_flash_system_params = cohesity_management_sdk.models_v2.recover_pure_params.RecoverPureParams.from_dictionary(
            dictionary.get('ibmFlashSystemParams')) if dictionary.get('ibmFlashSystemParams') else None
        flashblade_params = cohesity_management_sdk.models_v2.recover_flashblade_params.RecoverFlashbladeParams.from_dictionary(dictionary.get('flashbladeParams')) if dictionary.get('flashbladeParams') else None
        elastifile_params = cohesity_management_sdk.models_v2.recover_elastifile_params.RecoverElastifileParams.from_dictionary(dictionary.get('elastifileParams')) if dictionary.get('elastifileParams') else None
        gpfs_params = cohesity_management_sdk.models_v2.recover_gpfs_params.RecoverGPFSParams.from_dictionary(dictionary.get('gpfsParams')) if dictionary.get('gpfsParams') else None
        physical_params = cohesity_management_sdk.models_v2.recover_physical_environment_params.RecoverPhysicalEnvironmentParams.from_dictionary(dictionary.get('physicalParams')) if dictionary.get('physicalParams') else None
        hyperv_params = cohesity_management_sdk.models_v2.recover_hyperv_environment_params.RecoverHypervEnvironmentParams.from_dictionary(dictionary.get('hypervParams')) if dictionary.get('hypervParams') else None
        exchange_params = cohesity_management_sdk.models_v2.recover_exchange_environment_params.RecoverExchangeEnvironmentParams.from_dictionary(dictionary.get('exchangeParams')) if dictionary.get('exchangeParams') else None
        pure_params = cohesity_management_sdk.models_v2.recover_pure_params.RecoverPureParams.from_dictionary(dictionary.get('pureParams')) if dictionary.get('pureParams') else None
        kubernetes_params = cohesity_management_sdk.models_v2.recover_kubernetes_environment_params.RecoverKubernetesEnvironmentParams.from_dictionary(dictionary.get('kubernetesParams')) if dictionary.get('kubernetesParams') else None
        office_365_params = cohesity_management_sdk.models_v2.recover_office_365_environment_params.RecoverOffice365EnvironmentParams.from_dictionary(dictionary.get('office365Params')) if dictionary.get('office365Params') else None
        cassandra_params = cohesity_management_sdk.models_v2.recover_cassandra_environment_params.RecoverCassandraEnvironmentParams.from_dictionary(dictionary.get('cassandraParams')) if dictionary.get('cassandraParams') else None
        couchbase_params = cohesity_management_sdk.models_v2.recover_couchbase_environment_params.RecoverCouchbaseEnvironmentParams.from_dictionary(dictionary.get('couchbaseParams')) if dictionary.get('couchbaseParams') else None
        hbase_params = cohesity_management_sdk.models_v2.recover_hbase_environment_params.RecoverHbaseEnvironmentParams.from_dictionary(dictionary.get('hbaseParams')) if dictionary.get('hbaseParams') else None
        hdfs_params = cohesity_management_sdk.models_v2.recover_hdfs_environment_params.RecoverHDFSEnvironmentParams.from_dictionary(dictionary.get('hdfsParams')) if dictionary.get('hdfsParams') else None
        hive_params = cohesity_management_sdk.models_v2.recover_hive_environment_params.RecoverHiveEnvironmentParams.from_dictionary(dictionary.get('hiveParams')) if dictionary.get('hiveParams') else None
        mongodb_params = cohesity_management_sdk.models_v2.recover_mongo_db_environment_params.RecoverMongoDBEnvironmentParams.from_dictionary(dictionary.get('mongodbParams')) if dictionary.get('mongodbParams') else None
        oracle_params = cohesity_management_sdk.models_v2.recover_oracle_environment_params.RecoverOracleEnvironmentParams.from_dictionary(dictionary.get('oracleParams')) if dictionary.get('oracleParams') else None
        sfdc_params = cohesity_management_sdk.models_v2.recover_salesforce_environment_params.RecoverSalesforceEnvironmentParams.from_dictionary(dictionary.get('sfdcParams')) if dictionary.get('sfdcParams') else None
        uda_params = cohesity_management_sdk.models_v2.recover_universal_data_adapter_environment_params.RecoverUniversalDataAdapterEnvironmentParams.from_dictionary(
            dictionary.get('udaParams')) if dictionary.get('udaParams') else None
        view_params = cohesity_management_sdk.models_v2.recover_view_environment_params.RecoverViewEnvironmentParams.from_dictionary(
            dictionary.get('viewParams')) if dictionary.get('viewParams') else None


        # Return an object of this model
        return cls(name,
                   snapshot_environment,
                   vmware_params,
                   aws_params,
                   gcp_params,
                   azure_params,
                   kvm_params,
                   acropolis_params,
                   mssql_params,
                   netapp_params,
                   generic_nas_params,
                   isilon_params,
                   ibm_flash_system_params,
                   flashblade_params,
                   elastifile_params,
                   gpfs_params,
                   physical_params,
                   hyperv_params,
                   exchange_params,
                   pure_params,
                   kubernetes_params,
                   office_365_params,
                   cassandra_params,
                   couchbase_params,
                   hbase_params,
                   hdfs_params,
                   hive_params,
                   mongodb_params,
                   oracle_params,
                   sfdc_params,
                   uda_params,
                   view_params)