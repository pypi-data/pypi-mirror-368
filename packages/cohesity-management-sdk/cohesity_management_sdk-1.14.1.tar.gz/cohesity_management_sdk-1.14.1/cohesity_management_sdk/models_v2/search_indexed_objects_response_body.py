# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.email
import cohesity_management_sdk.models_v2.file
import cohesity_management_sdk.models_v2.cassandra_indexed_object
import cohesity_management_sdk.models_v2.couchbase_indexed_object
import cohesity_management_sdk.models_v2.hbase_indexed_object
import cohesity_management_sdk.models_v2.hive_indexed_object
import cohesity_management_sdk.models_v2.mongo_indexed_object
import cohesity_management_sdk.models_v2.hdfs_indexed_object
import cohesity_management_sdk.models_v2.public_folder_item

class SearchIndexedObjectsResponseBody(object):

    """Implementation of the 'Search Indexed objects response body.' model.

    Specifies the search indexed objects response body.

    Attributes:
        object_type (ObjectType2Enum): Specifies the object type.
        count (int): Specifies the total number of indexed objects that match
            the filter and search criteria. Use this value to determine how
            many additional requests are required to get the full result.
        pagination_cookie (string): Specifies cookie for resuming search if
            pagination is being used.
        emails (list of Email): Specifies the indexed emails and email
            folders.
        files (list of string): Specifies the indexed files and file folders.
        cassandra_objects (list of CassandraIndexedObject): Specifies the
            indexed Cassandra objects.
        couchbase_objects (list of CouchbaseIndexedObject): Specifies the
            indexed Couchbase objects.
        hbase_objects (list of HbaseIndexedObject): Specifies the indexed
            Hbase objects.
        hive_objects (list of HiveIndexedObject): Specifies the indexed Hive
            objects.
        mongo_objects (list of MongoIndexedObject): Specifies the indexed
            Mongo objects.
        hdfs_objects (list of HDFSIndexedObject): Specifies the indexed HDFS
            objects.
        public_folder_items (list of PublicFolderItem): Specifies the indexed
            Public folder items.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_type":'objectType',
        "count":'count',
        "pagination_cookie":'paginationCookie',
        "emails":'emails',
        "files":'files',
        "cassandra_objects":'cassandraObjects',
        "couchbase_objects":'couchbaseObjects',
        "hbase_objects":'hbaseObjects',
        "hive_objects":'hiveObjects',
        "mongo_objects":'mongoObjects',
        "hdfs_objects":'hdfsObjects',
        "public_folder_items":'publicFolderItems'
    }

    def __init__(self,
                 object_type=None,
                 count=None,
                 pagination_cookie=None,
                 emails=None,
                 files=None,
                 cassandra_objects=None,
                 couchbase_objects=None,
                 hbase_objects=None,
                 hive_objects=None,
                 mongo_objects=None,
                 hdfs_objects=None,
                 public_folder_items=None):
        """Constructor for the SearchIndexedObjectsResponseBody class"""

        # Initialize members of the class
        self.object_type = object_type
        self.count = count
        self.pagination_cookie = pagination_cookie
        self.emails = emails
        self.files = files
        self.cassandra_objects = cassandra_objects
        self.couchbase_objects = couchbase_objects
        self.hbase_objects = hbase_objects
        self.hive_objects = hive_objects
        self.mongo_objects = mongo_objects
        self.hdfs_objects = hdfs_objects
        self.public_folder_items = public_folder_items


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
        count = dictionary.get('count')
        pagination_cookie = dictionary.get('paginationCookie')
        emails = None
        if dictionary.get("emails") is not None:
            emails = list()
            for structure in dictionary.get('emails'):
                emails.append(cohesity_management_sdk.models_v2.email.Email.from_dictionary(structure))
        files = None
        if dictionary.get("files") is not None:
            files = list()
            for structure in dictionary.get('files'):
                files.append(cohesity_management_sdk.models_v2.file.File.from_dictionary(structure))
        cassandra_objects = None
        if dictionary.get("cassandraObjects") is not None:
            cassandra_objects = list()
            for structure in dictionary.get('cassandraObjects'):
                cassandra_objects.append(cohesity_management_sdk.models_v2.cassandra_indexed_object.CassandraIndexedObject.from_dictionary(structure))
        couchbase_objects = None
        if dictionary.get("couchbaseObjects") is not None:
            couchbase_objects = list()
            for structure in dictionary.get('couchbaseObjects'):
                couchbase_objects.append(cohesity_management_sdk.models_v2.couchbase_indexed_object.CouchbaseIndexedObject.from_dictionary(structure))
        hbase_objects = None
        if dictionary.get("hbaseObjects") is not None:
            hbase_objects = list()
            for structure in dictionary.get('hbaseObjects'):
                hbase_objects.append(cohesity_management_sdk.models_v2.hbase_indexed_object.HbaseIndexedObject.from_dictionary(structure))
        hive_objects = None
        if dictionary.get("hiveObjects") is not None:
            hive_objects = list()
            for structure in dictionary.get('hiveObjects'):
                hive_objects.append(cohesity_management_sdk.models_v2.hive_indexed_object.HiveIndexedObject.from_dictionary(structure))
        mongo_objects = None
        if dictionary.get("mongoObjects") is not None:
            mongo_objects = list()
            for structure in dictionary.get('mongoObjects'):
                mongo_objects.append(cohesity_management_sdk.models_v2.mongo_indexed_object.MongoIndexedObject.from_dictionary(structure))
        hdfs_objects = None
        if dictionary.get("hdfsObjects") is not None:
            hdfs_objects = list()
            for structure in dictionary.get('hdfsObjects'):
                hdfs_objects.append(cohesity_management_sdk.models_v2.hdfs_indexed_object.HDFSIndexedObject.from_dictionary(structure))
        public_folder_items = None
        if dictionary.get("publicFolderItems") is not None:
            public_folder_items = list()
            for structure in dictionary.get('publicFolderItems'):
                public_folder_items.append(cohesity_management_sdk.models_v2.public_folder_item.PublicFolderItem.from_dictionary(structure))

        # Return an object of this model
        return cls(object_type,
                   count,
                   pagination_cookie,
                   emails,
                   files,
                   cassandra_objects,
                   couchbase_objects,
                   hbase_objects,
                   hive_objects,
                   mongo_objects,
                   hdfs_objects,
                   public_folder_items)


