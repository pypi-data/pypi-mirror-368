# -*- coding: utf-8 -*-


class VmwareRecoverTargetSourceDiskParams(object):

    """Implementation of the 'VmwareRecoverTargetSourceDiskParams' model.

    Specifies disk specific parameters for performing a disk recovery.

    Attributes:
        disk_uuid (string): Specifies the UUID of the source disk being
            recovered.
        datastore_id (long|int): Specifies the ID of the datastore on which
            the specified disk will be spun up.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "disk_uuid":'diskUuid',
        "datastore_id":'datastoreId'
    }

    def __init__(self,
                 disk_uuid=None,
                 datastore_id=None):
        """Constructor for the VmwareRecoverTargetSourceDiskParams class"""

        # Initialize members of the class
        self.disk_uuid = disk_uuid
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
        datastore_id = dictionary.get('datastoreId')

        # Return an object of this model
        return cls(disk_uuid,
                   datastore_id)


