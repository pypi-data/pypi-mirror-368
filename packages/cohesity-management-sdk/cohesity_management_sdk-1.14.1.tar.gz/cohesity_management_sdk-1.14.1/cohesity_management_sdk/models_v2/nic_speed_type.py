# -*- coding: utf-8 -*-


class NICSpeedType(object):

    """Implementation of the 'NIC Speed Type' model.

    Speed of a network interface.

    Attributes:
        nic_speed_type (NicSpeedType1Enum): Specifies the network interface
            speed.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "nic_speed_type":'nicSpeedType'
    }

    def __init__(self,
                 nic_speed_type=None):
        """Constructor for the NICSpeedType class"""

        # Initialize members of the class
        self.nic_speed_type = nic_speed_type


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
        nic_speed_type = dictionary.get('nicSpeedType')

        # Return an object of this model
        return cls(nic_speed_type)


