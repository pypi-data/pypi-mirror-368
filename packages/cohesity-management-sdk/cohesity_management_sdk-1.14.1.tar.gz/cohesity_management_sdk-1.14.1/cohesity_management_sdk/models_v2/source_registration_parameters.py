# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.vmware_source_registration_params
import cohesity_management_sdk.models_v2.object_information
import cohesity_management_sdk.models_v2.flashblade_protection_source
import cohesity_management_sdk.models_v2.generic_nas_protection_source
import cohesity_management_sdk.models_v2.key_value_pair
import cohesity_management_sdk.models_v2.register_physical_sever_request_parameters
import cohesity_management_sdk.models_v2.register_cassandra_source_request_parameters
import cohesity_management_sdk.models_v2.register_universal_data_adapter_source_registration_request_parameters
import cohesity_management_sdk.models_v2.register_sfdc_source_request_parameters
import cohesity_management_sdk.models_v2.office_365_source_registration_parameters
import cohesity_management_sdk.models_v2.netapp_protection_source
import cohesity_management_sdk.models_v2.aws_source_registration_params
import cohesity_management_sdk.models_v2.azure_source_registration_params
import cohesity_management_sdk.models_v2.elastifile_protection_source
import cohesity_management_sdk.models_v2.ews_exchange_source_registration_params
import cohesity_management_sdk.models_v2.gpfs_protection_source
import cohesity_management_sdk.models_v2.isilon_protection_source
import cohesity_management_sdk.models_v2.hyper_v_source_registration_params
import cohesity_management_sdk.models_v2.register_couchbase_source_request_parameters
import cohesity_management_sdk.models_v2.register_mongo_db_source_request_parameters
import cohesity_management_sdk.models_v2.register_couchbase_source_request_parameters
import cohesity_management_sdk.models_v2.register_hdfs_source_request_parameters
import cohesity_management_sdk.models_v2.register_h_base_source_request_parameters
import cohesity_management_sdk.models_v2.register_hive_source_request_parameters

class SourceRegistrationParameters(object):

    """Implementation of the 'Source Registration parameters.' model.

    Specifies the Source Registration parameters.

    Attributes:
        id (long|int): Source Registration ID. This can be used to retrieve,
            edit or delete the source registration.
        source_id (long|int): ID of top level source object discovered after
            the registration.
        source_info (ObjectInformation): Specifies detailed info about the source.
        environment (Environment8Enum): Specifies the environment type of the
            Protection Source.
        advanced_configs (list of KeyValuePair): Specifies the advanced configuration
            for a protection source.
        connection_id (long|int): Specifies the id of the connection from where this source is
            reachable. This should only be set for a source being registered by a
            tenant user. This field will be depricated in future. Use connections
            field.
        encryption_key (string): Specifies the key that user has encrypted the credential with.
        is_internal_encrypted (bool): Specifies if credentials are encrypted by internal key.
        connections (list of ConnectionConfig): Specfies the list of connections for the source.
        connector_group_id (long|int): Specifies the connector group id of connector groups.
        name (string): A user specified name for this source.
        vmware_params (VmwareSourceRegistrationParams): Specifies the
            paramaters to register a VMware source.
        uda_params (RegisterUniversalDataAdapterSourceRegistrationRequestParameters): Specifies the parameters to register a Universal Data Adapter
            Protection Source.
        sfdc_params (RegisterSFDCSourceRequestParameters): Specifies the parameters to register a SFDC Adapter Protection
            Source.
        office_365_params (Office365SourceRegistrationParameters): Specifies the parameters to register an office 365 Source.
        netapp_params (NetappProtectionSource): Specifies parameters to register an Netapp Source.
        aws_params (AwsSourceRegistrationParams): Specifies the parameters to register an AWS source.
        azure_params (AzureSourceRegistrationParams): Specifies the parameters to register an Azure source.
        elastifile_params (ElastifileProtectionSource): Specifies the parameters to register an Elastifile Source.
        ews_exchange_params (EwsExchangeSourceRegistrationParams): Specifies the parameters to register an EWS Exchange source.
        flashblade_params (FlashbladeRegistrationParams): Specifies the parameters to register an Flashblade Source.
        generic_nas_params (GenericNASProtectionSource): Specifies the parameters to register a Generic Nas Source.
        gpfs_params (GPFSProtectionSource): Specifies the parameters to register an GPFS Source.
        isilon_params (IsilonProtectionSource): Specifies parameters to register an Isilon Source.
        physical_params (RegisterPhysicalSeverRequestParameters): Specifies
            parameters to register physical server.
        cassandra_params (RegisterCassandraSourceRequestParameters): Specifies
            parameters to register cassandra source.
        mongodb_params (RegisterMongoDBSourceRequestParameters): Specifies
            parameters to register MongoDB source.
        couchbase_params (RegisterCouchbaseSourceRequestParameters): Specifies
            parameters to register Couchbase source.
        hdfs_params (RegisterHDFSSourceRequestParameters): Specifies
            parameters to register an HDFS source.
        hbase_params (RegisterHBaseSourceRequestParameters): Specifies
            parameters to register an HBase source.
        hive_params (RegisterHiveSourceRequestParameters): Specifies
            parameters to register Hive source.
        hyperv_params (HyperVSourceRegistrationParams): Specifies the parameters to register a HyperV Protection Source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "source_id":'sourceId',
        "source_info":'sourceInfo',
        "environment":'environment',
        "advanced_configs":'advancedConfigs',
        "connection_id":'connectionId',
        "encryption_key":'encryptionKey',
        "is_internal_encrypted":'isInternalEncrypted',
        "connections":'connections',
        "connector_group_id":'connectorGroupId',
        "name":'name',
        "vmware_params":'vmwareParams',
        "uda_params" : 'udaParams' ,
        "sfdc_params":'sfdcParams',
        "office_365_params":"office365Params",
        "netapp_params":'netappParams',
        "aws_params":'awsParams',
        "azure_params":'azureParams',
        "elastifile_params":'elastifileParams',
        "ews_exchange_params":'ewsExchangeParams',
        "flashblade_params":'flashbladeParams',
        "generic_nas_params":'genericNasParams',
        "gpfs_params":'gpfsParams',
        "isilon_params":'isilonParams',
        "physical_params":'physicalParams',
        "cassandra_params":'cassandraParams',
        "mongodb_params":'mongodbParams',
        "couchbase_params":'couchbaseParams',
        "hdfs_params":'hdfsParams',
        "hbase_params":'hbaseParams',
        "hive_params":'hiveParams',
        "hyperv_params":'hypervParams'
    }

    def __init__(self,
                 id=None ,
                 source_id=None ,
                 source_info=None ,
                 environment=None ,
                 advanced_configs=None ,
                 connection_id=None,
                 encryption_key=None,
                 is_internal_encrypted=None,
                 connections=None ,
                 connector_group_id=None ,
                 name=None,
                 vmware_params=None,
                 uda_params=None ,
                 sfdc_params = None,
                 office_365_params=None,
                 netapp_params=None,
                 aws_params=None,
                 azure_params=None,
                 elastifile_params=None,
                 ews_exchange_params=None,
                 flashblade_params=None,
                 generic_nas_params=None,
                 gpfs_params=None ,
                 isilon_params=None ,
                 physical_params=None,
                 cassandra_params=None,
                 mongodb_params=None,
                 couchbase_params=None,
                 hdfs_params=None,
                 hbase_params=None,
                 hive_params=None,
                 hyperv_params=None):
        """Constructor for the SourceRegistrationParameters class"""

        # Initialize members of the class
        self.id = id
        self.source_id = source_id
        self.source_info = source_info
        self.environment = environment
        self.advanced_configs = advanced_configs
        self.connection_id = connection_id
        self.encryption_key = encryption_key
        self.is_internal_encrypted = is_internal_encrypted
        self.connections = connections
        self.connector_group_id = connector_group_id
        self.environment = environment
        self.name = name
        self.vmware_params = vmware_params
        self.uda_params = uda_params
        self.sfdc_params = sfdc_params
        self.office_365_params = office_365_params
        self.netapp_params = netapp_params
        self.aws_params = aws_params
        self.azure_params = azure_params
        self.elastifile_params = elastifile_params
        self.ews_exchange_params = ews_exchange_params
        self.flashblade_params = flashblade_params
        self.generic_nas_params = generic_nas_params
        self.gpfs_params = gpfs_params
        self.isilon_params = isilon_params
        self.physical_params = physical_params
        self.cassandra_params = cassandra_params
        self.mongodb_params = mongodb_params
        self.couchbase_params = couchbase_params
        self.hdfs_params = hdfs_params
        self.hbase_params = hbase_params
        self.hive_params = hive_params
        self.hyperv_params = hyperv_params


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
        source_id = dictionary.get('sourceId')
        source_info = cohesity_management_sdk.models_v2.object_information.Object.from_dictionary(
            dictionary.get('sourceInfo'))
        environment = dictionary.get('environment')
        advanced_configs = None
        if dictionary.get('advancedConfigs') is not None :
            advanced_configs = list()
            for structure in dictionary.get('advancedConfigs') :
                advanced_configs.append(
                    cohesity_management_sdk.models_v2.key_value_pair.KeyValuePair.from_dictionary(structure))
        connection_id = dictionary.get('connectionId')
        encryption_key = dictionary.get('encryptionKey')
        is_internal_encrypted = dictionary.get('isInternalEncrypted')
        connections = dictionary.get('connections')
        connector_group_id = dictionary.get('connectorGroupId')
        name = dictionary.get('name')
        vmware_params = cohesity_management_sdk.models_v2.vmware_source_registration_params.VmwareSourceRegistrationParams.from_dictionary(dictionary.get('vmwareParams')) if dictionary.get('vmwareParams') else None
        uda_params = cohesity_management_sdk.models_v2.register_universal_data_adapter_source_registration_request_parameters.RegisterUniversalDataAdapterSourceRegistrationRequestParameters.from_dictionary(
            dictionary.get('udaParams')) if dictionary.get('udaParams') else None
        sfdc_params = cohesity_management_sdk.models_v2.register_sfdc_source_request_parameters.RegisterSFDCSourceRequestParameters.from_dictionary(
            dictionary.get('sfdcParams')) if dictionary.get('sfdcParams') else None
        office_365_params = cohesity_management_sdk.models_v2.office_365_source_registration_parameters.Office365SourceRegistrationParameters.from_dictionary(
            dictionary.get('office365Params')) if dictionary.get('office365Params') else None
        netapp_params = cohesity_management_sdk.models_v2.netapp_protection_source.NetappProtectionSource.from_dictionary(
            dictionary.get('netappParams')) if dictionary.get('netappParams') else None
        aws_params = cohesity_management_sdk.models_v2.aws_source_registration_params.AwsSourceRegistrationParams.from_dictionary(
            dictionary.get('awsParams'))
        azure_params = cohesity_management_sdk.models_v2.azure_source_registration_params.AzureSourceRegistrationParams.from_dictionary(
            dictionary.get('azureParams')) if dictionary.get('azureParams') else None
        elastifile_params = cohesity_management_sdk.models_v2.elastifile_protection_source.ElastifileProtectionSource.from_dictionary(
            dictionary.get('elastifileParams')) if dictionary.get('elastifileParams') else None
        ews_exchange_params = cohesity_management_sdk.models_v2.ews_exchange_source_registration_params.EwsExchangeSourceRegistrationParams.from_dictionary(
            dictionary.get('ewsExchangeParams')) if dictionary.get('ewsExchangeParams') else None
        flashblade_params = cohesity_management_sdk.models_v2.flashblade_protection_source.FlashbladeProtectionSource.from_dictionary(
            dictionary.get('flashbladeParams')) if dictionary.get('flashbladeParams') else None
        generic_nas_params = cohesity_management_sdk.models_v2.generic_nas_protection_source.GenericNASProtectionSource.from_dictionary(
            dictionary.get('genericNasParams')) if dictionary.get('genericNasParams') else None
        gpfs_params = cohesity_management_sdk.models_v2.gpfs_protection_source.GPFSProtectionSource.from_dictionary(
            dictionary.get('gpfsParams')) if dictionary.get('gpfsParams') else None
        isilon_params = cohesity_management_sdk.models_v2.isilon_protection_source.IsilonProtectionSource.from_dictionary(
            dictionary.get('isilonParams')) if dictionary.get('isilonParams') else None
        physical_params = cohesity_management_sdk.models_v2.register_physical_sever_request_parameters.RegisterPhysicalSeverRequestParameters.from_dictionary(dictionary.get('physicalParams')) if dictionary.get('physicalParams') else None
        cassandra_params = cohesity_management_sdk.models_v2.register_cassandra_source_request_parameters.RegisterCassandraSourceRequestParameters.from_dictionary(dictionary.get('cassandraParams')) if dictionary.get('cassandraParams') else None
        mongodb_params = cohesity_management_sdk.models_v2.register_mongo_db_source_request_parameters.RegisterMongoDBSourceRequestParameters.from_dictionary(dictionary.get('mongodbParams')) if dictionary.get('mongodbParams') else None
        couchbase_params = cohesity_management_sdk.models_v2.register_couchbase_source_request_parameters.RegisterCouchbaseSourceRequestParameters.from_dictionary(dictionary.get('couchbaseParams')) if dictionary.get('couchbaseParams') else None
        hdfs_params = cohesity_management_sdk.models_v2.register_hdfs_source_request_parameters.RegisterHDFSSourceRequestParameters.from_dictionary(dictionary.get('hdfsParams')) if dictionary.get('hdfsParams') else None
        hbase_params = cohesity_management_sdk.models_v2.register_h_base_source_request_parameters.RegisterHBaseSourceRequestParameters.from_dictionary(dictionary.get('hbaseParams')) if dictionary.get('hbaseParams') else None
        hive_params = cohesity_management_sdk.models_v2.register_hive_source_request_parameters.RegisterHiveSourceRequestParameters.from_dictionary(dictionary.get('hiveParams')) if dictionary.get('hiveParams') else None
        hyperv_params = cohesity_management_sdk.models_v2.hyper_v_source_registration_params.HyperVSourceRegistrationParams.from_dictionary(
            dictionary.get('hypervParams')) if dictionary.get('hypervParams') else None

        # Return an object of this model
        return cls(id,
                   source_id,
                   source_info,
                   environment,
                   advanced_configs,
                   connection_id,
                   encryption_key,
                   is_internal_encrypted,
                   connections,
                   connector_group_id,
                   name,
                   vmware_params,
                   uda_params,
                   sfdc_params,
                   office_365_params,
                   netapp_params,
                   aws_params ,
                   azure_params ,
                   elastifile_params ,
                   ews_exchange_params ,
                   flashblade_params,
                   generic_nas_params,
                   gpfs_params,
                   isilon_params,
                   physical_params,
                   cassandra_params,
                   mongodb_params,
                   couchbase_params,
                   hdfs_params,
                   hbase_params,
                   hive_params,
                   hyperv_params)