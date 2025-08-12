# -*- coding: utf-8 -*-


class DiskStatus(object):

    """Implementation of the 'Disk Status' model.

    Disk Status

    Attributes:
        disk_status (DiskStatus1Enum): Disk Status

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "disk_status":'diskStatus'
    }

    def __init__(self,
                 disk_status=None):
        """Constructor for the DiskStatus class"""

        # Initialize members of the class
        self.disk_status = disk_status


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
        disk_status = dictionary.get('diskStatus')

        # Return an object of this model
        return cls(disk_status)


