# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.network_config_10

class OriginalSourceConfig4(object):

    """Implementation of the 'OriginalSourceConfig4' model.

    Specifies the Source configuration if vApp templates are being recovered
    to Original Source. If not specified, all the configuration parameters
    will be retained.

    Attributes:
        network_config (NetworkConfig10): Specifies the networking
            configuration to be applied to the recovered vApps.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "network_config":'networkConfig'
    }

    def __init__(self,
                 network_config=None):
        """Constructor for the OriginalSourceConfig4 class"""

        # Initialize members of the class
        self.network_config = network_config


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
        network_config = cohesity_management_sdk.models_v2.network_config_10.NetworkConfig10.from_dictionary(dictionary.get('networkConfig')) if dictionary.get('networkConfig') else None

        # Return an object of this model
        return cls(network_config)


