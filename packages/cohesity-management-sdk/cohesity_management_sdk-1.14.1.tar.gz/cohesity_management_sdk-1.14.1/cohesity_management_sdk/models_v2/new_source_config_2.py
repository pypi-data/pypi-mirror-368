# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.source
import cohesity_management_sdk.models_v2.region_1
import cohesity_management_sdk.models_v2.key_pair
import cohesity_management_sdk.models_v2.encryption_configuration
import cohesity_management_sdk.models_v2.network_config_3

class NewSourceConfig2(object):

    """Implementation of the 'NewSourceConfig2' model.

    Specifies the new destination Source configuration parameters where the
    VMs will be recovered. This is mandatory if recoverToNewSource is set to
    true.

    Attributes:
        encryption_config (): Specifies the encryption configuration.
        source (Source): Specifies the id of the parent source to recover the
            VMs.
        region (Region1): Specifies the AWS region in which to deploy the VM.
        key_pair (KeyPair): Specifies the pair of public and private key used
            to login into the VM
        network_config (NetworkConfig3): Specifies the networking
            configuration to be applied to the recovered VMs.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "encryption_config":'encryptionConfig',
        "source":'source',
        "region":'region',
        "network_config":'networkConfig',
        "key_pair":'keyPair'
    }

    def __init__(self,
                 encryption_config=None,
                 source=None,
                 region=None,
                 network_config=None,
                 key_pair=None):
        """Constructor for the NewSourceConfig2 class"""

        # Initialize members of the class
        self.encryption_config = encryption_config
        self.source = source
        self.region = region
        self.network_config = network_config
        self.key_pair = key_pair


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
        encryption_config = cohesity_management_sdk.models_v2.encryption_configuration.EncryptionConfiguration.from_dictionary(
            dictionary.get('encryptionConfig')) if dictionary.get('encryptionConfig') else None
        source = cohesity_management_sdk.models_v2.source.Source.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None
        region = cohesity_management_sdk.models_v2.region_1.Region1.from_dictionary(dictionary.get('region')) if dictionary.get('region') else None
        network_config = cohesity_management_sdk.models_v2.network_config_3.NetworkConfig3.from_dictionary(dictionary.get('networkConfig')) if dictionary.get('networkConfig') else None
        key_pair = cohesity_management_sdk.models_v2.key_pair.KeyPair.from_dictionary(dictionary.get('keyPair')) if dictionary.get('keyPair') else None

        # Return an object of this model
        return cls(encryption_config,
                   source,
                   region,
                   network_config,
                   key_pair)