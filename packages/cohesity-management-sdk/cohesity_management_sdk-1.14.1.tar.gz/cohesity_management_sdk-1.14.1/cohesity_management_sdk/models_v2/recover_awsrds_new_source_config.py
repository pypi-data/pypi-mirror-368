# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.source_1
import cohesity_management_sdk.models_v2.region
import cohesity_management_sdk.models_v2.network_config_2

class RecoverAWSRDSNewSourceConfig(object):

    """Implementation of the 'Recover AWS RDS New Source Config.' model.

    Specifies the new destination Source configuration where the RDS instances
    will be recovered.

    Attributes:
        source (Source1): Specifies the id of the parent source to recover the
            RDS.
        region (Region): Specifies the AWS region in which to deploy the RDS
            instance.
        network_config (NetworkConfig2): Specifies the networking
            configuration to be applied to the recovered VMs.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source":'source',
        "region":'region',
        "network_config":'networkConfig'
    }

    def __init__(self,
                 source=None,
                 region=None,
                 network_config=None):
        """Constructor for the RecoverAWSRDSNewSourceConfig class"""

        # Initialize members of the class
        self.source = source
        self.region = region
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
        source = cohesity_management_sdk.models_v2.source_1.Source1.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None
        region = cohesity_management_sdk.models_v2.region.Region.from_dictionary(dictionary.get('region')) if dictionary.get('region') else None
        network_config = cohesity_management_sdk.models_v2.network_config_2.NetworkConfig2.from_dictionary(dictionary.get('networkConfig')) if dictionary.get('networkConfig') else None

        # Return an object of this model
        return cls(source,
                   region,
                   network_config)


