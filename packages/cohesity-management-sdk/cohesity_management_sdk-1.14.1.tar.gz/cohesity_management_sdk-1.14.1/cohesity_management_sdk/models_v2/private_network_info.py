# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.recovery_object_identifier

class PrivateNetworkInfo(object):

    """Implementation of the 'PrivateNetworkInfo' model.

    Specifies the object parameters to create Azure Snapshot Manager
      Protection Group.

    Attributes:
        location (string): Specifies the subnet for creating a private endpoint.
        region (RecoveryObjectIdentifier): Specifies the region of the virtual network.
        subnet (RecoveryObjectIdentifier): Specifies the subnet for creating a private endpoint.
        vpn (RecoveryObjectIdentifier): Specifies the virtual network for creating a private end point.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "location":'location',
        "region":'region',
        "subnet":'subnet',
        "vpn":'vpn'
    }

    def __init__(self,
                 location=None,
                 region=None,
                 subnet=None,
                 vpn=None):
        """Constructor for the PrivateNetworkInfo class"""

        # Initialize members of the class
        self.location = location
        self.region = region
        self.subnet = subnet
        self.vpn = vpn


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
        location = dictionary.get('location')
        region = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('region')) if dictionary.get('region') else None
        subnet = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('subnet')) if dictionary.get('subnet') else None
        vpn = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('vpn')) if dictionary.get('vpn') else None

        # Return an object of this model
        return cls(location,
                   region,
                   subnet,
                   vpn)