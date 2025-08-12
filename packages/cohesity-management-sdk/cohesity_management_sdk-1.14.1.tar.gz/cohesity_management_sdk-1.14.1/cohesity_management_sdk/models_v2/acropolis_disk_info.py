# -*- coding: utf-8 -*-


class AcropolisDiskInfo(object):

    """Implementation of the 'AcropolisDiskInfo' model.

    Specifies information about a disk to be filtered.

    Attributes:
        controller_type (ControllerTypeEnum): Specifies the disk controller type.
        unit_number (long|int): Specifies the disk index number.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "controller_type":'controllerType',
        "unit_number":'unitNumber'
    }

    def __init__(self,
                 controller_type=None,
                 unit_number=None):
        """Constructor for the AcropolisDiskInfo class"""

        # Initialize members of the class
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
        controller_type = dictionary.get('controllerType')
        unit_number = dictionary.get('unitNumber')

        # Return an object of this model
        return cls(controller_type,
                   unit_number)