# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.source
import cohesity_management_sdk.models_v2.storage_container
import cohesity_management_sdk.models_v2.network_config

class RecoverAcropolisVMsNewSourceConfig(object):

    """Implementation of the 'Recover Acropolis VMs New Source Config.' model.

    Specifies the new destination Source configuration where the VMs will be
    recovered.

    Attributes:
        source (Source): Specifies the id of the parent source to recover the
            VMs.
        storage_container (StorageContainer): A storage container where the
            VM's files should be restored to.
        network_config (NetworkConfig): Specifies the networking configuration
            to be applied to the recovered VMs.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source":'source',
        "storage_container":'storageContainer',
        "network_config":'networkConfig'
    }

    def __init__(self,
                 source=None,
                 storage_container=None,
                 network_config=None):
        """Constructor for the RecoverAcropolisVMsNewSourceConfig class"""

        # Initialize members of the class
        self.source = source
        self.storage_container = storage_container
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
        source = cohesity_management_sdk.models_v2.source.Source.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None
        storage_container = cohesity_management_sdk.models_v2.storage_container.StorageContainer.from_dictionary(dictionary.get('storageContainer')) if dictionary.get('storageContainer') else None
        network_config = cohesity_management_sdk.models_v2.network_config.NetworkConfig.from_dictionary(dictionary.get('networkConfig')) if dictionary.get('networkConfig') else None

        # Return an object of this model
        return cls(source,
                   storage_container,
                   network_config)


