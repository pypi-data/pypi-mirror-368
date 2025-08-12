# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.agent_based_azure_protection_group_request_params
import cohesity_management_sdk.models_v2.azure_native_protection_group_request_params
import cohesity_management_sdk.models_v2.create_azure_snapshot_manager_protection_group_request_body

class AzureProtectionGroupRequestParams(object):

    """Implementation of the 'Azure Protection Group Request Params.' model.

    Specifies the parameters which are specific to Azure related Protection
    Groups.

    Attributes:
        protection_type (ProtectionType2Enum): Specifies the Azure Protection
            Group type.
        agent_protection_type_params
            (AgentBasedAzureProtectionGroupRequestParams): Specifies the
            parameters which are specific to Azure related Protection Groups
            using cohesity protection-service installed on the instance.
            Objects must be specified.
        native_protection_type_params
            (AzureNativeProtectionGroupRequestParams): Specifies the
            parameters which are specific to Azure related Protection Groups
            using Azure native snapshot APIs. Objects must be specified.
        snapshot_manager_protection_type_params
            (CreateAzureSnapshotManagerProtectionGroupRequestBody): Specifies
            the parameters which are specific to Azure related Protection
            Groups using Azure native snapshot orchestration with snapshot
            manager. Objects must be specified.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_type":'protectionType',
        "agent_protection_type_params":'agentProtectionTypeParams',
        "native_protection_type_params":'nativeProtectionTypeParams',
        "snapshot_manager_protection_type_params":'snapshotManagerProtectionTypeParams'
    }

    def __init__(self,
                 protection_type=None,
                 agent_protection_type_params=None,
                 native_protection_type_params=None,
                 snapshot_manager_protection_type_params=None):
        """Constructor for the AzureProtectionGroupRequestParams class"""

        # Initialize members of the class
        self.protection_type = protection_type
        self.agent_protection_type_params = agent_protection_type_params
        self.native_protection_type_params = native_protection_type_params
        self.snapshot_manager_protection_type_params = snapshot_manager_protection_type_params


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
        protection_type = dictionary.get('protectionType')
        agent_protection_type_params = cohesity_management_sdk.models_v2.agent_based_azure_protection_group_request_params.AgentBasedAzureProtectionGroupRequestParams.from_dictionary(dictionary.get('agentProtectionTypeParams')) if dictionary.get('agentProtectionTypeParams') else None
        native_protection_type_params = cohesity_management_sdk.models_v2.azure_native_protection_group_request_params.AzureNativeProtectionGroupRequestParams.from_dictionary(dictionary.get('nativeProtectionTypeParams')) if dictionary.get('nativeProtectionTypeParams') else None
        snapshot_manager_protection_type_params = cohesity_management_sdk.models_v2.create_azure_snapshot_manager_protection_group_request_body.CreateAzureSnapshotManagerProtectionGroupRequestBody.from_dictionary(dictionary.get('snapshotManagerProtectionTypeParams')) if dictionary.get('snapshotManagerProtectionTypeParams') else None

        # Return an object of this model
        return cls(protection_type,
                   agent_protection_type_params,
                   native_protection_type_params,
                   snapshot_manager_protection_type_params)


