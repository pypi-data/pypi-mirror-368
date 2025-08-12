# -*- coding: utf-8 -*-


class FleetSubnetType(object):

    """Implementation of the 'Fleet Subnet Type' model.

    Fleet Subnet Type

    Attributes:
        fleet_subnet_type (FleetSubnetType2Enum): Specifies the fleet type of
            the subnet.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "fleet_subnet_type":'fleetSubnetType'
    }

    def __init__(self,
                 fleet_subnet_type=None):
        """Constructor for the FleetSubnetType class"""

        # Initialize members of the class
        self.fleet_subnet_type = fleet_subnet_type


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
        fleet_subnet_type = dictionary.get('fleetSubnetType')

        # Return an object of this model
        return cls(fleet_subnet_type)


