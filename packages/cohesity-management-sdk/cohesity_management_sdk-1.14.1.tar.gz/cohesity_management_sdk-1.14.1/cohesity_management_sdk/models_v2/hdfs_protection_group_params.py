# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.indexing_policy

class HdfsProtectionGroupParams(object):

    """Implementation of the 'HdfsProtectionGroupParams' model.

    Specifies the parameters for HDFS Protection Group.

    Attributes:
        include_paths (list of string): Specifies the paths to be included in
            the Protection Group.
        exclude_paths (list of string): Specifies the paths to be excluded in
            the Protection Group. excludePaths will ovrride includePaths.
        concurrency (int): Specifies the maximum number of concurrent IO
            Streams that will be created to exchange data with the cluster.
        bandwidth_mbps (long|int): Specifies the maximum network bandwidth
            that each concurrent IO Stream can use for exchanging data with
            the cluster.
        hdfs_source_id (long|int): The object ID of the HDFS source for this
            protection group.
        source_id (long|int): Object ID of the Source on which this protection
            was run .
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.
        source_name (string): Specifies the name of the Source on which this
            protection was run.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "hdfs_source_id":'hdfsSourceId',
        "include_paths":'includePaths',
        "exclude_paths":'excludePaths',
        "concurrency":'concurrency',
        "bandwidth_mbps":'bandwidthMBPS',
        "source_id":'sourceId',
        "indexing_policy":'indexingPolicy',
        "source_name":'sourceName'
    }

    def __init__(self,
                 hdfs_source_id=None,
                 include_paths=None,
                 exclude_paths=None,
                 concurrency=None,
                 bandwidth_mbps=None,
                 source_id=None,
                 indexing_policy=None,
                 source_name=None):
        """Constructor for the HdfsProtectionGroupParams class"""

        # Initialize members of the class
        self.include_paths = include_paths
        self.exclude_paths = exclude_paths
        self.concurrency = concurrency
        self.bandwidth_mbps = bandwidth_mbps
        self.hdfs_source_id = hdfs_source_id
        self.source_id = source_id
        self.indexing_policy = indexing_policy
        self.source_name = source_name


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
        hdfs_source_id = dictionary.get('hdfsSourceId')
        include_paths = dictionary.get('includePaths')
        exclude_paths = dictionary.get('excludePaths')
        concurrency = dictionary.get('concurrency')
        bandwidth_mbps = dictionary.get('bandwidthMBPS')
        source_id = dictionary.get('sourceId')
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        source_name = dictionary.get('sourceName')

        # Return an object of this model
        return cls(hdfs_source_id,
                   include_paths,
                   exclude_paths,
                   concurrency,
                   bandwidth_mbps,
                   source_id,
                   indexing_policy,
                   source_name)


