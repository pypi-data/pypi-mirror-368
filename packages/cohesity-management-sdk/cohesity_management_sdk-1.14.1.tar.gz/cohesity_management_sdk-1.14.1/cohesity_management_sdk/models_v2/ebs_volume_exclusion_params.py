# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.tag_params

class EBSVolumeExclusionParams(object):

    """Implementation of the 'EBSVolumeExclusionParams' model.

    Specifies the parameters to exclude EBS volumes attached to EC2 instances
      at global and object level. A volume satisfying any of these criteria will be
      excluded.

    Attributes:
        device_names (list of string): Array of device names to exclude. Eg - /dev/sda.
        max_volume_size_bytes (long|int): Any volume larger than this size will be excluded.
        raw_query (string): Raw boolean query given as input by the user to exclude volume
          based on tags. In the current version, the query contains only tags. Eg.
          query 1 - "K1" = "V1" AND "K2" IN ("V2", "V3") AND "K4" != "V4" Eg. query
          2 - "K1" != "V1" OR "K2" NOT IN ("V2", "V3") OR "K4" = "V4" All Keys and
          Values must be wrapped inside double quotes. Comparision Operators supported
          - IN, NOT IN, =, !=. Logical Operators supported - AND, OR. We cannot have
          AND, OR together in the query. Only one of them is allowed. The processed
          form for this query is stored in the above tagParamsArray.
        tag_params_array (list of TagParams): Array of TagParams objects. Each TagParams object consists of
          two vectors: for exclusion and inclusion. Each TagPararms object is present
          as an ORed item. User can only input queries of form: (<> AND <> AND <>
          ..) OR (<> AND <> AND <> ..) OR (..) OR (..) OR .. There cannot be an OR
          operator inside the bracket. Example query: (K1 = V1 AND K2 = V2 AND K3
          != V3) OR (K4 = V4 AND K6 != V6). This will lead to formation of two items
          in tagParamsArray. First item: {exclusionTagArray: [(K1, V1),  (K2, V2)],
          inclusionTagArray: [(K3, V3)]} Second item: {exclusionTagArray: [(K4, V4)],
          inclusionTagArray: [(K6, V6)]})
        volume_ids (list of string): Array of volume IDs that are to be excluded. This is only for
          object level exclusion.
        volume_types (list of string): Array of volume types to exclude. Eg - gp2, gp3.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "device_names":'deviceNames',
        "max_volume_size_bytes":'maxVolumeSizeBytes',
        "raw_query":'rawQuery',
        "tag_params_array":'tagParamsArray',
        "volume_ids":'volumeIds',
        "volume_types":'volumeTypes'
    }

    def __init__(self,
                 device_names=None,
                 max_volume_size_bytes=None,
                 raw_query=None,
                 tag_params_array=None,
                 volume_ids=None,
                 volume_types=None):
        """Constructor for the EBSVolumeExclusionParams class"""

        # Initialize members of the class
        self.device_names = device_names
        self.max_volume_size_bytes = max_volume_size_bytes
        self.raw_query = raw_query
        self.tag_params_array = tag_params_array
        self.volume_ids = volume_ids
        self.volume_types = volume_types


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
        device_names = dictionary.get('deviceNames')
        max_volume_size_bytes = dictionary.get('maxVolumeSizeBytes')
        raw_query = dictionary.get('rawQuery')
        tag_params_array = None
        if dictionary.get("tagParamsArray") is not None:
            tag_params_array = list()
            for structure in dictionary.get('tagParamsArray'):
                tag_params_array.append(cohesity_management_sdk.models_v2.tag_params.TagParams.from_dictionary(structure))
        volume_ids = dictionary.get('volumeIds')
        volume_types = dictionary.get('volumeTypes')

        # Return an object of this model
        return cls(device_names,
                   max_volume_size_bytes,
                   raw_query,
                   tag_params_array,
                   volume_ids,
                   volume_types)