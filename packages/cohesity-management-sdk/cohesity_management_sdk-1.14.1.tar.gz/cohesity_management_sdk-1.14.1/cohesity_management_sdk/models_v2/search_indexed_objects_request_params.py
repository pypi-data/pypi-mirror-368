# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.search_emails_request_params
import cohesity_management_sdk.models_v2.search_files_request_params
import cohesity_management_sdk.models_v2.cassandra_params
import cohesity_management_sdk.models_v2.couchbase_params
import cohesity_management_sdk.models_v2.hbase_params
import cohesity_management_sdk.models_v2.hive_params
import cohesity_management_sdk.models_v2.mongodb_params
import cohesity_management_sdk.models_v2.hdfs_params
import cohesity_management_sdk.models_v2.exchange_params
import cohesity_management_sdk.models_v2.search_public_folder_request_params

class SearchIndexedObjectsRequestParams(object):

    """Implementation of the 'Search indexed objects request params.' model.

    Specifies the request parameters to search for indexed objects.

    Attributes:
        protection_group_ids (list of string): Specifies a list of Protection
            Group ids to filter the indexed objects. If specified, the objects
            indexed by specified Protection Group ids will be returned.
        storage_domain_ids (list of long|int): Specifies the Storage Domain
            ids to filter indexed objects for which Protection Groups are
            writing data to Cohesity Views on the specified Storage Domains.
        tenant_id (string): TenantId contains id of the tenant for which
            objects are to be returned.
        include_tenants (bool): If true, the response will include objects
            which belongs to all tenants which the current user has permission
            to see. Default value is false.
        tags (list of string): Specifies a list of tags. Only files containing
            specified tags will be returned.
        snapshot_tags (list of string): Specifies a list of snapshot tags.
            Only files containing specified snapshot tags will be returned.
        must_have_tag_ids (list of string): Specifies tags which must be all
            present in the document.
        might_have_tag_ids (list of string): Specifies list of tags, one or
            more of which might be present in the document. These are OR'ed
            together and the resulting criteria AND'ed with the rest of the
            query.
        must_have_snapshot_tag_ids (list of string): Specifies snapshot tags
            which must be all present in the document.
        might_have_snapshot_tag_ids (list of string): Specifies list of
            snapshot tags, one or more of which might be present in the
            document. These are OR''ed together and the resulting criteria
            AND''ed with the rest of the query.
        pagination_cookie (string): Specifies the pagination cookie with which
            subsequent parts of the response can be fetched.
        count (int): Specifies the number of indexed obejcts to be fetched for
            the specified pagination cookie.
        object_type (ObjectType1Enum): Specifies the object type to be
            searched for.
        email_params (SearchEmailsRequestParams): Specifies the request
            parameters to search for emails and email folders.
        file_params (SearchFilesRequestParams): Specifies the request
            parameters to search for files and file folders.
        cassandra_params (CassandraParams): Specifies the parameters which are
            specific for searching Cassandra objects.
        couchbase_params (CouchbaseParams): Specifies the parameters which are
            specific for searching Couchbase objects.
        hbase_params (HbaseParams): Specifies the parameters which are
            specific for searching Hbase objects.
        hive_params (HiveParams): Specifies the parameters which are specific
            for searching Hive objects.
        mongodb_params (MongodbParams): Specifies the parameters which are
            specific for searching MongoDB objects.
        hdfs_params (HdfsParams): Specifies the parameters for searching HDFS
            Folders and Files.
        exchange_params (ExchangeParams): Specifies the parameters which are
            specific for searching Exchange mailboxes.
        public_folder_params (SearchPublicFolderRequestParams): Specifies the
            request parameters to search for Public Folder items.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_type":'objectType',
        "protection_group_ids":'protectionGroupIds',
        "storage_domain_ids":'storageDomainIds',
        "tenant_id":'tenantId',
        "include_tenants":'includeTenants',
        "tags":'tags',
        "snapshot_tags":'snapshotTags',
        "must_have_tag_ids":'mustHaveTagIds',
        "might_have_tag_ids":'mightHaveTagIds',
        "must_have_snapshot_tag_ids":'mustHaveSnapshotTagIds',
        "might_have_snapshot_tag_ids":'mightHaveSnapshotTagIds',
        "pagination_cookie":'paginationCookie',
        "count":'count',
        "email_params":'emailParams',
        "file_params":'fileParams',
        "cassandra_params":'cassandraParams',
        "couchbase_params":'couchbaseParams',
        "hbase_params":'hbaseParams',
        "hive_params":'hiveParams',
        "mongodb_params":'mongodbParams',
        "hdfs_params":'hdfsParams',
        "exchange_params":'exchangeParams',
        "public_folder_params":'publicFolderParams'
    }

    def __init__(self,
                 object_type=None,
                 protection_group_ids=None,
                 storage_domain_ids=None,
                 tenant_id=None,
                 include_tenants=False,
                 tags=None,
                 snapshot_tags=None,
                 must_have_tag_ids=None,
                 might_have_tag_ids=None,
                 must_have_snapshot_tag_ids=None,
                 might_have_snapshot_tag_ids=None,
                 pagination_cookie=None,
                 count=None,
                 email_params=None,
                 file_params=None,
                 cassandra_params=None,
                 couchbase_params=None,
                 hbase_params=None,
                 hive_params=None,
                 mongodb_params=None,
                 hdfs_params=None,
                 exchange_params=None,
                 public_folder_params=None):
        """Constructor for the SearchIndexedObjectsRequestParams class"""

        # Initialize members of the class
        self.protection_group_ids = protection_group_ids
        self.storage_domain_ids = storage_domain_ids
        self.tenant_id = tenant_id
        self.include_tenants = include_tenants
        self.tags = tags
        self.snapshot_tags = snapshot_tags
        self.must_have_tag_ids = must_have_tag_ids
        self.might_have_tag_ids = might_have_tag_ids
        self.must_have_snapshot_tag_ids = must_have_snapshot_tag_ids
        self.might_have_snapshot_tag_ids = might_have_snapshot_tag_ids
        self.pagination_cookie = pagination_cookie
        self.count = count
        self.object_type = object_type
        self.email_params = email_params
        self.file_params = file_params
        self.cassandra_params = cassandra_params
        self.couchbase_params = couchbase_params
        self.hbase_params = hbase_params
        self.hive_params = hive_params
        self.mongodb_params = mongodb_params
        self.hdfs_params = hdfs_params
        self.exchange_params = exchange_params
        self.public_folder_params = public_folder_params


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
        object_type = dictionary.get('objectType')
        protection_group_ids = dictionary.get('protectionGroupIds')
        storage_domain_ids = dictionary.get('storageDomainIds')
        tenant_id = dictionary.get('tenantId')
        include_tenants = dictionary.get("includeTenants") if dictionary.get("includeTenants") else False
        tags = dictionary.get('tags')
        snapshot_tags = dictionary.get('snapshotTags')
        must_have_tag_ids = dictionary.get('mustHaveTagIds')
        might_have_tag_ids = dictionary.get('mightHaveTagIds')
        must_have_snapshot_tag_ids = dictionary.get('mustHaveSnapshotTagIds')
        might_have_snapshot_tag_ids = dictionary.get('mightHaveSnapshotTagIds')
        pagination_cookie = dictionary.get('paginationCookie')
        count = dictionary.get('count')
        email_params = cohesity_management_sdk.models_v2.search_emails_request_params.SearchEmailsRequestParams.from_dictionary(dictionary.get('emailParams')) if dictionary.get('emailParams') else None
        file_params = cohesity_management_sdk.models_v2.search_files_request_params.SearchFilesRequestParams.from_dictionary(dictionary.get('fileParams')) if dictionary.get('fileParams') else None
        cassandra_params = cohesity_management_sdk.models_v2.cassandra_params.CassandraParams.from_dictionary(dictionary.get('cassandraParams')) if dictionary.get('cassandraParams') else None
        couchbase_params = cohesity_management_sdk.models_v2.couchbase_params.CouchbaseParams.from_dictionary(dictionary.get('couchbaseParams')) if dictionary.get('couchbaseParams') else None
        hbase_params = cohesity_management_sdk.models_v2.hbase_params.HbaseParams.from_dictionary(dictionary.get('hbaseParams')) if dictionary.get('hbaseParams') else None
        hive_params = cohesity_management_sdk.models_v2.hive_params.HiveParams.from_dictionary(dictionary.get('hiveParams')) if dictionary.get('hiveParams') else None
        mongodb_params = cohesity_management_sdk.models_v2.mongodb_params.MongodbParams.from_dictionary(dictionary.get('mongodbParams')) if dictionary.get('mongodbParams') else None
        hdfs_params = cohesity_management_sdk.models_v2.hdfs_params.HdfsParams.from_dictionary(dictionary.get('hdfsParams')) if dictionary.get('hdfsParams') else None
        exchange_params = cohesity_management_sdk.models_v2.exchange_params.ExchangeParams.from_dictionary(dictionary.get('exchangeParams')) if dictionary.get('exchangeParams') else None
        public_folder_params = cohesity_management_sdk.models_v2.search_public_folder_request_params.SearchPublicFolderRequestParams.from_dictionary(dictionary.get('publicFolderParams')) if dictionary.get('publicFolderParams') else None

        # Return an object of this model
        return cls(object_type,
                   protection_group_ids,
                   storage_domain_ids,
                   tenant_id,
                   include_tenants,
                   tags,
                   snapshot_tags,
                   must_have_tag_ids,
                   might_have_tag_ids,
                   must_have_snapshot_tag_ids,
                   might_have_snapshot_tag_ids,
                   pagination_cookie,
                   count,
                   email_params,
                   file_params,
                   cassandra_params,
                   couchbase_params,
                   hbase_params,
                   hive_params,
                   mongodb_params,
                   hdfs_params,
                   exchange_params,
                   public_folder_params)


