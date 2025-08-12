# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class VirtualDiskBasicInfo(object):

    """Implementation of the 'VirtualDiskBasicInfo' model.

    Hyperv Virtual Disk

    Attributes:
        controller_bus_number (long|int): Controller bus number.
        controller_type (string): Controller type.
        unit_number (long|int):  Disk unit number.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "controller_bus_number":'controllerBusNumber',
        "controller_type":'controllerType',
        "unit_number":'unitNumber'
    }

    def __init__(self,
                 controller_bus_number=None,
                 controller_type=None,
                 unit_number=None):
        """Constructor for the VirtualDiskBasicInfo class"""

        # Initialize members of the class
        self.controller_bus_number = controller_bus_number
        self.controller_type = controller_type
        self.unit_number = unit_number


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
        controller_bus_number = dictionary.get('controllerBusNumber')
        controller_type = dictionary.get('controllerType')
        unit_number = dictionary.get('unitNumber')

        # Return an object of this model
        return cls(controller_bus_number,
                   controller_type,
                   unit_number)


