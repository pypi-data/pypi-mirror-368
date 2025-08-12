# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.fleet_network_params_2
import cohesity_management_sdk.models_v2.fleet_tags

class RecoverAsFleetConfig(object):

    """Implementation of the 'Recover as fleet config.' model.

    Specifies various resources while deploying fleet params.

    Attributes:
        fleet_subnet_type (FleetSubnetType3Enum): Specifies the subnet type of
            the fleet.
        fleet_network_params (FleetNetworkParams2): Specifies the network
            security groups within above VPC.
        fleet_tags (list of FleetTags): Specifies the network security groups
            within above VPC.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "fleet_subnet_type":'fleetSubnetType',
        "fleet_network_params":'fleetNetworkParams',
        "fleet_tags":'fleetTags'
    }

    def __init__(self,
                 fleet_subnet_type=None,
                 fleet_network_params=None,
                 fleet_tags=None):
        """Constructor for the RecoverAsFleetConfig class"""

        # Initialize members of the class
        self.fleet_subnet_type = fleet_subnet_type
        self.fleet_network_params = fleet_network_params
        self.fleet_tags = fleet_tags


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
        fleet_network_params = cohesity_management_sdk.models_v2.fleet_network_params_2.FleetNetworkParams2.from_dictionary(dictionary.get('fleetNetworkParams')) if dictionary.get('fleetNetworkParams') else None
        fleet_tags = None
        if dictionary.get("fleetTags") is not None:
            fleet_tags = list()
            for structure in dictionary.get('fleetTags'):
                fleet_tags.append(cohesity_management_sdk.models_v2.fleet_tags.FleetTags.from_dictionary(structure))

        # Return an object of this model
        return cls(fleet_subnet_type,
                   fleet_network_params,
                   fleet_tags)


