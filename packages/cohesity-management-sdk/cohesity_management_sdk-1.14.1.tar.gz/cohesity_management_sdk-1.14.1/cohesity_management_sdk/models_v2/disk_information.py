# -*- coding: utf-8 -*-


class DiskInformation(object):

    """Implementation of the 'Disk Information' model.

    Specifies information about a disk.

    Attributes:
        controller_type (ControllerTypeEnum): Specifies the disk controller
            type.
        unit_number (long|int): Specifies the disk file name. This is the VMDK
            name and not the flat file name.
        bus_number (long|int): Specifies the Id of the controller bus that
            controls the disk.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "unit_number":'unitNumber',
        "bus_number":'busNumber',
        "controller_type":'controllerType'
    }

    def __init__(self,
                 unit_number=None,
                 bus_number=None,
                 controller_type=None):
        """Constructor for the DiskInformation class"""

        # Initialize members of the class
        self.controller_type = controller_type
        self.unit_number = unit_number
        self.bus_number = bus_number


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
        unit_number = dictionary.get('unitNumber')
        bus_number = dictionary.get('busNumber')
        controller_type = dictionary.get('controllerType')

        # Return an object of this model
        return cls(unit_number,
                   bus_number,
                   controller_type)


