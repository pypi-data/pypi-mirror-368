# -*- coding: utf-8 -*-


class FreeDisk(object):

    """Implementation of the 'FreeDisk' model.

    Specifies the details of a free disk.

    Attributes:
        location (string): Specifies the location of disk.
        serial_number (string): Specifies serial number of disk.
        path (string): Specifies path of disk.
        size_in_bytes (long|int): Size of disk.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "serial_number":'serialNumber',
        "location":'location',
        "path":'path',
        "size_in_bytes":'sizeInBytes'
    }

    def __init__(self,
                 serial_number=None,
                 location=None,
                 path=None,
                 size_in_bytes=None):
        """Constructor for the FreeDisk class"""

        # Initialize members of the class
        self.location = location
        self.serial_number = serial_number
        self.path = path
        self.size_in_bytes = size_in_bytes


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
        serial_number = dictionary.get('serialNumber')
        location = dictionary.get('location')
        path = dictionary.get('path')
        size_in_bytes = dictionary.get('sizeInBytes')

        # Return an object of this model
        return cls(serial_number,
                   location,
                   path,
                   size_in_bytes)


