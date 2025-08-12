# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.network_config_1

class RecoverAcropolisVMsOriginalSourceConfig(object):

    """Implementation of the 'Recover Acropolis VMs Original Source Config.' model.

    Specifies the Source configuration if VM's are being recovered to Original
    Source.

    Attributes:
        network_config (NetworkConfig1): Specifies the networking
            configuration to be applied to the recovered VMs.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "network_config":'networkConfig'
    }

    def __init__(self,
                 network_config=None):
        """Constructor for the RecoverAcropolisVMsOriginalSourceConfig class"""

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
        network_config = cohesity_management_sdk.models_v2.network_config_1.NetworkConfig1.from_dictionary(dictionary.get('networkConfig')) if dictionary.get('networkConfig') else None

        # Return an object of this model
        return cls(network_config)


