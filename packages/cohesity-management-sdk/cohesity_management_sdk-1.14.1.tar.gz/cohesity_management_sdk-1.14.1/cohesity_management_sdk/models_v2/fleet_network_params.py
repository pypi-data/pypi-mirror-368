# -*- coding: utf-8 -*-


class FleetNetworkParams(object):

    """Implementation of the 'Fleet Network Params.' model.

    Specifies various network params for the fleet.

    Attributes:
        vpc (string): Specifies vpc for the fleet.
        subnet (string): Specifies subnet for the fleet.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "vpc":'vpc',
        "subnet":'subnet'
    }

    def __init__(self,
                 vpc=None,
                 subnet=None):
        """Constructor for the FleetNetworkParams class"""

        # Initialize members of the class
        self.vpc = vpc
        self.subnet = subnet


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
        vpc = dictionary.get('vpc')
        subnet = dictionary.get('subnet')

        # Return an object of this model
        return cls(vpc,
                   subnet)


