# -*- coding: utf-8 -*-


class VmwareRecoverOriginalSourceDiskParams(object):

    """Implementation of the 'VmwareRecoverOriginalSourceDiskParams' model.

    Specifies disk specific parameters for performing a disk recovery.

    Attributes:
        disk_uuid (string): Specifies the UUID of the source disk being
            recovered.
        overwrite_original_disk (bool): Specifies whether or not to overwrite
            the original disk. If this is set to true, then datastoreId should
            not be specified. Otherwise, datastoreId must be specified.
        datastore_id (long|int): Specifies the ID of the datastore on which
            the specified disk will be spun up.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "disk_uuid":'diskUuid',
        "overwrite_original_disk":'overwriteOriginalDisk',
        "datastore_id":'datastoreId'
    }

    def __init__(self,
                 disk_uuid=None,
                 overwrite_original_disk=None,
                 datastore_id=None):
        """Constructor for the VmwareRecoverOriginalSourceDiskParams class"""

        # Initialize members of the class
        self.disk_uuid = disk_uuid
        self.overwrite_original_disk = overwrite_original_disk
        self.datastore_id = datastore_id


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
        disk_uuid = dictionary.get('diskUuid')
        overwrite_original_disk = dictionary.get('overwriteOriginalDisk')
        datastore_id = dictionary.get('datastoreId')

        # Return an object of this model
        return cls(disk_uuid,
                   overwrite_original_disk,
                   datastore_id)


