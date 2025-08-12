# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.logical_volume_info_2

class VolumeInfo(object):

    """Implementation of the 'VolumeInfo' model.

    Specifies info of logical volume (filesystem).

    Attributes:
        name (string): Specifies the volume name.
        is_supported (bool): Specifies if this volume is supported.
        volume_type (VolumeTypeEnum): Specifies the volume type.
        filesystem_type (string): Specifies the filesystem type.
        filesystem_uuid (string): Specifies the filesystem uuid.
        volume_guid (string): Specifies the volume guid.
        volume_size_in_bytes (long|int): Specifies volume size in bytes.
        logical_volume_info (LogicalVolumeInfo2): Specifies the logical volume
            info. This fields is for 'LVM' and 'LDM' volume type only.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "is_supported":'isSupported',
        "volume_type":'volumeType',
        "filesystem_type":'filesystemType',
        "filesystem_uuid":'filesystemUuid',
        "volume_guid":'volumeGuid',
        "volume_size_in_bytes":'volumeSizeInBytes',
        "logical_volume_info":'logicalVolumeInfo'
    }

    def __init__(self,
                 name=None,
                 is_supported=None,
                 volume_type=None,
                 filesystem_type=None,
                 filesystem_uuid=None,
                 volume_guid=None,
                 volume_size_in_bytes=None,
                 logical_volume_info=None):
        """Constructor for the VolumeInfo class"""

        # Initialize members of the class
        self.name = name
        self.is_supported = is_supported
        self.volume_type = volume_type
        self.filesystem_type = filesystem_type
        self.filesystem_uuid = filesystem_uuid
        self.volume_guid = volume_guid
        self.volume_size_in_bytes = volume_size_in_bytes
        self.logical_volume_info = logical_volume_info


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
        is_supported = dictionary.get('isSupported')
        volume_type = dictionary.get('volumeType')
        filesystem_type = dictionary.get('filesystemType')
        filesystem_uuid = dictionary.get('filesystemUuid')
        volume_guid = dictionary.get('volumeGuid')
        volume_size_in_bytes = dictionary.get('volumeSizeInBytes')
        logical_volume_info = cohesity_management_sdk.models_v2.logical_volume_info_2.LogicalVolumeInfo2.from_dictionary(dictionary.get('logicalVolumeInfo')) if dictionary.get('logicalVolumeInfo') else None

        # Return an object of this model
        return cls(name,
                   is_supported,
                   volume_type,
                   filesystem_type,
                   filesystem_uuid,
                   volume_guid,
                   volume_size_in_bytes,
                   logical_volume_info)


