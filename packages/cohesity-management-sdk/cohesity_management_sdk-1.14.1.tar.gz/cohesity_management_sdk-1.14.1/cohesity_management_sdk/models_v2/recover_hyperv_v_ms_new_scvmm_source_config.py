# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.source
import cohesity_management_sdk.models_v2.host_1
import cohesity_management_sdk.models_v2.volume_6
import cohesity_management_sdk.models_v2.network_config_15

class RecoverHypervVMsNewSCVMMSourceConfig(object):

    """Implementation of the 'Recover HyperV VMs New SCVMM Source Config.' model.

    Specifies the new destination Source configuration where the VMs will be
    recovered.

    Attributes:
        source (Source): Specifies the id of the parent source to recover the
            VMs.
        host (Host1): Specifies the HyperV host where the recovered VMs will
            be attached. For standalone host targets, the host must be the
            same as the source.
        volume (Volume6): Specifies the datastore object where the VMs' files
            should be recovered to.
        network_config (NetworkConfig15): Specifies the networking
            configuration to be applied to the recovered VMs.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source":'source',
        "host":'host',
        "volume":'volume',
        "network_config":'networkConfig'
    }

    def __init__(self,
                 source=None,
                 host=None,
                 volume=None,
                 network_config=None):
        """Constructor for the RecoverHypervVMsNewSCVMMSourceConfig class"""

        # Initialize members of the class
        self.source = source
        self.host = host
        self.volume = volume
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
        host = cohesity_management_sdk.models_v2.host_1.Host1.from_dictionary(dictionary.get('host')) if dictionary.get('host') else None
        volume = cohesity_management_sdk.models_v2.volume_6.Volume6.from_dictionary(dictionary.get('volume')) if dictionary.get('volume') else None
        network_config = cohesity_management_sdk.models_v2.network_config_15.NetworkConfig15.from_dictionary(dictionary.get('networkConfig')) if dictionary.get('networkConfig') else None

        # Return an object of this model
        return cls(source,
                   host,
                   volume,
                   network_config)


