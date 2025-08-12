# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models_v2.recover_vmware_v_ms_new_source_network_configuration

class RestoreObjectCustomization(object):

    """Implementation of the 'RestoreObjectCustomization' model.

    Proto to specify the restore object customization.

    Attributes:
        network_config (RecoverVmwareVmNewSourceNetworkConfig): Specifies the customized network configuration for the VM being
          recovered.
        object_id (int): Specifies the object id of the VM.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "network_config":'networkConfig',
        "object_id":'objectId'

    }

    def __init__(self,
                 network_config=None,
                 object_id=None):
        """Constructor for the RestoreObjectCustomization class"""

        # Initialize members of the class
        self.network_config = network_config
        self.object_id = object_id


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
        network_config = cohesity_management_sdk.models_v2.recover_vmware_v_ms_new_source_network_configuration.RecoverVmwareVMsNewSourceNetworkConfiguration.from_dictionary(dictionary.get('networkConfig')) if dictionary.get('networkConfig') else None
        object_id = dictionary.get('objectId')

        # Return an object of this model
        return cls(network_config,
                   object_id)