# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.cloud_down_water_fall_params
import cohesity_management_sdk.models_v2.quota_policy
import cohesity_management_sdk.models_v2.file_count
import cohesity_management_sdk.models_v2.schema
import cohesity_management_sdk.models_v2.data_usage_statistics
import cohesity_management_sdk.models_v2.subnet
import cohesity_management_sdk.models_v2.storage_policy


class StorageDomain(object):

    """Implementation of the 'StorageDomain' model.

    Specifies the Storage Domain where the VM's disk should be restored to.

    Attributes:
        ad_domain_name (string): Specifies the Active Directory domain name that this Storage
          Domain is mapped to.
        blob_brick_size_bytes (long|int): Specifies the brick size used for blobs in this Storage Domain.
        cloud_domain_id (long|int):Specifies the cloud domain Id.
        cloud_down_water_fall_params (CloudDownWaterFallParams): Specifies the cloud down water fall parameters for this Storage
          Domain.
        cluster_partition_id (long|int): Specifies the cluster partition id of the Storage Domain.
        cluster_partition_name (string): Specifies the cluster partition name of the Storage Domain.
        default_user_quota (QuotaPolicy): Specifies a default logical quota limit for all views in this
          Storage Domain. This quota can be overwritten by a view level quota.
        default_view_quota (QuotaPolicy): Specifies a default logical quota limit for all views in this
          Storage Domain. This quota can be overwritten by a view level quota.
        dek_rotation_enabled (bool): Specifies whether DEK(Data Encryption Key) rotation is enabled
          for this Storage Domain. This is applicable only when the Storage Domain
          uses AWS or similar KMS in which the KEK (Key Encryption Key) is not created
          and maintained by Cohesity. For Internal KMS and keys stored in Safenet
          servers, DEK rotation will not be performed.
        direct_archive_enabled (bool): Specifies whether to enable driect archive on this Storage Domain.
          If enabled, this Storage Domain can be used as a staging area while copying
          a large dataset that can't fit on the cluster to an external target.
        file_count_by_size (FileCount): Specifies the file count by size for the View.
        id (long|int): Specifies the Storage Domain id.
        kerberos_realm_name (string): Specifies the Kerberos realm name that this Storage Domain is
          mapped to.
        kms_server_id (long|int): Specifies the associated KMS server id.
        last_key_rotation_timestamp_msecs (long|int): Last key rotation timestamp in msecs for storage domain.
        ldap_provider_id (long|int): Specifies the LDAP provider id that this Storage Domain is mapped
          to.
        name (string): Specifies the name of the object.
        nis_domain_names (string): Specifies the NIS domain names that this Storage Domain is mapped
          to.
        physical_quota (QuotaPolicy): Specifies a quota limit for physical usage of this Storage Domain.
          This quota defines a limit of data that can be physically (after data size
          is reduced by block tracking, compression and deduplication) stored on this
          storage domain. A new write will not be allowed when the storage domain
          usage will exceeds the specified quota. Due to the latency of calculating
          usage across all nodes, the actual storage domain usage may exceed the quota
          limit by a little bit.
        recommended (bool): Specifies whether Storage Domain is recommended for the specified
          View template.
        removal_state (removalStateEnum): Specifies the current removal state of the Storage Domain. 'DontRemove'
          means the state of object is functional and it is not being removed. 'MarkedForRemoval'
          means the object is being removed. 'OkToRemove' means the object has been
          removed on the Cohesity Cluster and if the object is physical, it can be
          removed from the Cohesity Cluster.
        s_3_buckets_enabled (bool): Specifies whether to enable creation of S3 bucket on this Storage
          Domain.
        schemas (list of Schema): Specifies the Storage Domain schemas.
        stats (DataUsageStats): Specifies the Storage Domain stats.
        storage_policy (StoragePolicy): Specifies the storage policy for this Storage Domain.
        subnet_whitelist (list of Subnet): Specifies a list of Subnets with IP addresses that have permissions
          to access the Storage Domain.
        tenant_ids (string): Specifies a list of tenant ids that that Storage Domain belongs.
          There can only be one tenant id in this field unless Storage Domain sharing
          between tenants is allowed on this cluster.
        treat_file_sync_as_data_sync (bool): If 'true', when the Cohesity Cluster is writing to a file, the
          file modification time is not persisted synchronously during the file write,
          so the modification time may not be accurate. (Typically the file modification
          time is off by 30 seconds but it can be longer.)
        vault_id (long|int): Specifies the vault Id associated with cloud domain ID.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "ad_domain_name":'adDomainName',
        "blob_brick_size_bytes":'blobBrickSizeBytes',
        "cloud_domain_id":'cloudDomainId',
        "cloud_down_water_fall_params":'cloudDownWaterFallParams',
        "cluster_partition_id":'clusterPartitionId',
        "cluster_partition_name":'clusterPartitionName',
        "default_user_quota":'defaultUserQuota',
        "default_view_quota":'defaultViewQuota',
        "dek_rotation_enabled":'dekRotationEnabled',
        "direct_archive_enabled":'directArchiveEnabled',
        "file_count_by_size":'fileCountBySize',
        "id":'id',
        "kerberos_realm_name":'kerberosRealmName',
        "kms_server_id":'kmsServerId',
        "last_key_rotation_timestamp_msecs":'lastKeyRotationTimestampMsecs',
        "ldap_provider_id":'ldapProviderId',
        "name":'name',
        "nis_domain_names":'nisDomainNames',
        "physical_quota":'physicalQuota',
        "recommended":'recommended',
        "removal_state":'removalState',
        "s_3_buckets_enabled":'s3BucketsEnabled',
        "schemas":'schemas',
        "stats":'stats',
        "storage_policy":'storagePolicy',
        "subnet_whitelist":'subnetWhitelist',
        "tenant_ids":'tenantIds',
        "treat_file_sync_as_data_sync":'treatFileSyncAsDataSync',
        "vault_id":'vaultId'
    }

    def __init__(self,
                 ad_domain_name=None,
                 blob_brick_size_bytes=None,
                 cloud_domain_id=None,
                 cloud_down_water_fall_params=None,
                 cluster_partition_id=None,
                 cluster_partition_name=None,
                 default_user_quota=None,
                 default_view_quota=None,
                 dek_rotation_enabled=None,
                 direct_archive_enabled=None,
                 file_count_by_size=None,
                 id=None,
                 kerberos_realm_name=None,
                 kms_server_id=None,
                 last_key_rotation_timestamp_msecs=None,
                 ldap_provider_id=None,
                 name=None,
                 nis_domain_names=None,
                 physical_quota=None,
                 recommended=None,
                 removal_state=None,
                 s_3_buckets_enabled=None,
                 schemas=None,
                 stats=None,
                 storage_policy=None,
                 subnet_whitelist=None,
                 tenant_ids=None,
                 treat_file_sync_as_data_sync=None,
                 vault_id=None):
        """Constructor for the StorageDomain class"""

        # Initialize members of the class
        self.ad_domain_name = ad_domain_name
        self.blob_brick_size_bytes = blob_brick_size_bytes
        self.cloud_domain_id = cloud_domain_id
        self.cloud_down_water_fall_params = cloud_down_water_fall_params
        self.cluster_partition_id = cluster_partition_id
        self.cluster_partition_name = cluster_partition_name
        self.default_user_quota = default_user_quota
        self.default_view_quota = default_view_quota
        self.dek_rotation_enabled = dek_rotation_enabled
        self.direct_archive_enabled = direct_archive_enabled
        self.file_count_by_size = file_count_by_size
        self.id = id
        self.kerberos_realm_name = kerberos_realm_name
        self.kms_server_id = kms_server_id
        self.last_key_rotation_timestamp_msecs = last_key_rotation_timestamp_msecs
        self.ldap_provider_id = ldap_provider_id
        self.name = name
        self.nis_domain_names = nis_domain_names
        self.physical_quota = physical_quota
        self.recommended = recommended
        self.removal_state = removal_state
        self.s_3_buckets_enabled = s_3_buckets_enabled
        self.schemas = schemas
        self.stats = stats
        self.storage_policy = storage_policy
        self.subnet_whitelist = subnet_whitelist
        self.tenant_ids = tenant_ids
        self.treat_file_sync_as_data_sync = treat_file_sync_as_data_sync
        self.vault_id = vault_id


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
        ad_domain_name = dictionary.get('adDomainName')
        blob_brick_size_bytes = dictionary.get('blobBrickSizeBytes')
        cloud_domain_id = dictionary.get('cloudDomainId')
        cloud_down_water_fall_params = cohesity_management_sdk.models_v2.cloud_down_water_fall_params.CloudDownWaterFallParams.from_dictionary(dictionary.get('cloudDownWaterFallParams')) if dictionary.get('cloudDownWaterFallParams') else None
        cluster_partition_id = dictionary.get('clusterPartitionId')
        cluster_partition_name = dictionary.get('clusterPartitionName')
        default_user_quota = cohesity_management_sdk.models_v2.quota_policy.QuotaPolicy.from_dictionary(dictionary.get('defaultUserQuota')) if dictionary.get('defaultUserQuota') else None
        default_view_quota = cohesity_management_sdk.models_v2.quota_policy.QuotaPolicy.from_dictionary(dictionary.get('defaultViewQuota')) if dictionary.get('defaultViewQuota') else None
        dek_rotation_enabled = dictionary.get('dekRotationEnabled')
        direct_archive_enabled = dictionary.get('directArchiveEnabled')
        file_count_by_size = None
        if dictionary.get("fileCountBySize") is not None:
            file_count_by_size = list()
            for structure in dictionary.get('fileCountBySize'):
                file_count_by_size.append(cohesity_management_sdk.models_v2.file_count.FileCount.from_dictionary(structure))
        id = dictionary.get('id')
        kerberos_realm_name = dictionary.get('kerberosRealmName')
        kms_server_id = dictionary.get('kmsServerId')
        last_key_rotation_timestamp_msecs = dictionary.get('lastKeyRotationTimestampMsecs')
        ldap_provider_id = dictionary.get('ldapProviderId')
        name = dictionary.get('name')
        nis_domain_names = dictionary.get('nisDomainNames')
        physical_quota = cohesity_management_sdk.models_v2.quota_policy.QuotaPolicy.from_dictionary(dictionary.get('physicalQuota')) if dictionary.get('physicalQuota') else None
        recommended = dictionary.get('recommended')
        removal_state = dictionary.get('removalState')
        s_3_buckets_enabled = dictionary.get('s3BucketsEnabled')
        schemas = None
        if dictionary.get("schemas") is not None:
            schemas = list()
            for structure in dictionary.get('schemas'):
                schemas.append(cohesity_management_sdk.models_v2.schema.Schema.from_dictionary(structure))
        stats = cohesity_management_sdk.models_v2.data_usage_statistics.DataUsageStatistics.from_dictionary(dictionary.get('stats')) if dictionary.get('stats') else None
        storage_policy = cohesity_management_sdk.models_v2.storage_policy.StoragePolicy.from_dictionary(dictionary.get('storagePolicy')) if dictionary.get('storagePolicy') else None
        subnet_whitelist = None
        if dictionary.get("subnetWhitelist") is not None:
            subnet_whitelist = list()
            for structure in dictionary.get('subnetWhitelist'):
                subnet_whitelist.append(cohesity_management_sdk.models_v2.subnet.Subnet.from_dictionary(structure))
        tenant_ids = dictionary.get('tenantIds')
        treat_file_sync_as_data_sync = dictionary.get('treatFileSyncAsDataSync')
        vault_id = dictionary.get('vaultId')

        # Return an object of this model
        return cls(ad_domain_name,
                   blob_brick_size_bytes,
                   cloud_domain_id,
                   cloud_down_water_fall_params,
                   cluster_partition_id,
                   cluster_partition_name,
                   default_user_quota,
                   default_view_quota,
                   dek_rotation_enabled,
                   direct_archive_enabled,
                   file_count_by_size,
                   id,
                   kerberos_realm_name,
                   kms_server_id,
                   last_key_rotation_timestamp_msecs,
                   ldap_provider_id,
                   name,
                   nis_domain_names,
                   physical_quota,
                   recommended,
                   removal_state,
                   s_3_buckets_enabled,
                   schemas,
                   stats,
                   storage_policy,
                   subnet_whitelist,
                   tenant_ids,
                   treat_file_sync_as_data_sync,
                   vault_id
                   )