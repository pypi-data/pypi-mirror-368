# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.device_tree

class LogicalVolumeInfo2(object):

    """Implementation of the 'LogicalVolumeInfo2' model.

    Specifies the logical volume info. This fields is for 'LVM' and 'LDM'
    volume type only.

    Attributes:
        volume_group_uuid (string): Specifies the volume group uuid.
        volume_group_name (string): Specifies the volume group name.
        logical_volume_uuid (string): Specifies the logical volume uuid.
        logical_volume_name (string): Specifies the logical volume name.
        device_tree (DeviceTree): Specifies the tree structure of the logical
            volume.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "volume_group_uuid":'volumeGroupUuid',
        "volume_group_name":'volumeGroupName',
        "logical_volume_uuid":'logicalVolumeUuid',
        "logical_volume_name":'logicalVolumeName',
        "device_tree":'deviceTree'
    }

    def __init__(self,
                 volume_group_uuid=None,
                 volume_group_name=None,
                 logical_volume_uuid=None,
                 logical_volume_name=None,
                 device_tree=None):
        """Constructor for the LogicalVolumeInfo2 class"""

        # Initialize members of the class
        self.volume_group_uuid = volume_group_uuid
        self.volume_group_name = volume_group_name
        self.logical_volume_uuid = logical_volume_uuid
        self.logical_volume_name = logical_volume_name
        self.device_tree = device_tree


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
        volume_group_uuid = dictionary.get('volumeGroupUuid')
        volume_group_name = dictionary.get('volumeGroupName')
        logical_volume_uuid = dictionary.get('logicalVolumeUuid')
        logical_volume_name = dictionary.get('logicalVolumeName')
        device_tree = cohesity_management_sdk.models_v2.device_tree.DeviceTree.from_dictionary(dictionary.get('deviceTree')) if dictionary.get('deviceTree') else None

        # Return an object of this model
        return cls(volume_group_uuid,
                   volume_group_name,
                   logical_volume_uuid,
                   logical_volume_name,
                   device_tree)


