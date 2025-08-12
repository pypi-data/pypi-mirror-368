# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.no_sql_protection_group_object_params

class NoSqlProtectionGroupParams(object):

    """Implementation of the 'NoSqlProtectionGroupParams' model.

    Specifies the source specific parameters for this Protection Group.

    Attributes:
        auto_scale_concurrency (bool): Specifies the flag to automatically scale number of concurrent
          IO Streams that will be created to exchange data with the cluster.
        objects (list of NoSqlProtectionGroupObjectParams): Specifies the
            objects to be included in the Protection Group.
        concurrency (int): Specifies the maximum number of concurrent IO
            Streams that will be created to exchange data with the cluster.
        bandwidth_mbps (long|int): Specifies the maximum network bandwidth
            that each concurrent IO Stream can use for exchanging data with
            the cluster.
        exclude_object_ids (list of long|int): Specifies the objects to be
            excluded in the Protection Group.
        source_id (long|int): Object ID of the Source on which this protection
            was run .
        source_name (string): Specifies the name of the Source on which this
            protection was run.
        custom_source_name (string): The user specified name for the Source on
            which this protection was run.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "auto_scale_concurrency" : 'autoScaleConcurrency',
        "objects":'objects',
        "concurrency":'concurrency',
        "bandwidth_mbps":'bandwidthMBPS',
        "exclude_object_ids":'excludeObjectIds',
        "source_id":'sourceId',
        "source_name":'sourceName',
        "custom_source_name":'customSourceName'
    }

    def __init__(self,
                 auto_scale_concurrency=None,
                 objects=None,
                 concurrency=None,
                 bandwidth_mbps=None,
                 exclude_object_ids=None,
                 source_id=None,
                 source_name=None,
                 custom_source_name=None):
        """Constructor for the NoSqlProtectionGroupParams class"""

        # Initialize members of the class
        self.auto_scale_concurrency = auto_scale_concurrency
        self.objects = objects
        self.concurrency = concurrency
        self.bandwidth_mbps = bandwidth_mbps
        self.exclude_object_ids = exclude_object_ids
        self.source_id = source_id
        self.source_name = source_name
        self.custom_source_name = custom_source_name


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
        auto_scale_concurrency = dictionary.get('autoScaleConcurrency')
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.no_sql_protection_group_object_params.NoSqlProtectionGroupObjectParams.from_dictionary(structure))
        concurrency = dictionary.get('concurrency')
        bandwidth_mbps = dictionary.get('bandwidthMBPS')
        exclude_object_ids = dictionary.get('excludeObjectIds')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        custom_source_name = dictionary.get('customSourceName')

        # Return an object of this model
        return cls(
                   auto_scale_concurrency,
                   objects,
                   concurrency,
                   bandwidth_mbps,
                   exclude_object_ids,
                   source_id,
                   source_name,
                   custom_source_name)