# -*- coding: utf-8 -*-


class DeviceTreeLeafNode(object):

    """Implementation of the 'DeviceTreeLeafNode' model.

    Specifies the parameters of a leaf node in device tree.

    Attributes:
        disk_name (string): Specifies the disk name.
        partition_number (int): Specifies the paritition number.
        offset_bytes (long|int): Specifies the offset in bytes where data for
            the LVM volume (for which this device tree is being build) starts
            relative to the start of the partition.
        length_bytes (long|int): Specifies The length of data in bytes for the
            LVM volume (for which this device tree is being built). It does
            not include size of the LVM meta data.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "disk_name":'diskName',
        "partition_number":'partitionNumber',
        "offset_bytes":'offsetBytes',
        "length_bytes":'lengthBytes'
    }

    def __init__(self,
                 disk_name=None,
                 partition_number=None,
                 offset_bytes=None,
                 length_bytes=None):
        """Constructor for the DeviceTreeLeafNode class"""

        # Initialize members of the class
        self.disk_name = disk_name
        self.partition_number = partition_number
        self.offset_bytes = offset_bytes
        self.length_bytes = length_bytes


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
        disk_name = dictionary.get('diskName')
        partition_number = dictionary.get('partitionNumber')
        offset_bytes = dictionary.get('offsetBytes')
        length_bytes = dictionary.get('lengthBytes')

        # Return an object of this model
        return cls(disk_name,
                   partition_number,
                   offset_bytes,
                   length_bytes)


