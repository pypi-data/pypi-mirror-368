# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.source
import cohesity_management_sdk.models_v2.resource_group
import cohesity_management_sdk.models_v2.storage_account
import cohesity_management_sdk.models_v2.storage_container_1
import cohesity_management_sdk.models_v2.network_config_4
import cohesity_management_sdk.models_v2.storage_resource_group
import cohesity_management_sdk.models_v2.recovery_object_identifier
import cohesity_management_sdk.models_v2.data_transfer_info_request

class NewSourceConfig3(object):

    """Implementation of the 'NewSourceConfig3' model.

    Specifies the new destination Source configuration parameters where the
    VMs will be recovered. This is mandatory if recoverToNewSource is set to
    true.

    Attributes:
        source (Source): Specifies the id of the parent source to recover the
            VMs.
        resource_group (ResourceGroup): Specifies the Azure resource group.
        storage_account (StorageAccount): Specifies the storage account that
            will contain the storage container
        storage_container (StorageContainer1): Specifies the storage container
            within the above storage account.
        network_config (NetworkConfig4): Specifies the networking
            configuration to be applied to the recovered VMs.
        storage_resource_group (StorageResourceGroup): Specifies id of the
            resource group for the selected storage account.
        subscription (RecoveryObjectIdentifier): Specifies the subscription id to recover the VMs. Applicable
          for Tenant based registration on DMaaS.
        region (RecoveryObjectIdentifier): Specifies the region to recover the VMs. Applicable for Tenant
          based registration on DMaaS.
        data_transfer_info (DataTransferInfoRequest): Specifies the the details of network used in transferring the
          data from source account to Cohesity cluster.
        compute_option (RecoveryObjectIdentifier): Specifies the type of VM (e.g. small, medium, large) when cloning/restoring
          the VM in Azure.
        availability_set (RecoveryObjectIdentifier): Specifies the availability set.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source":'source',
        "resource_group":'resourceGroup',
        "storage_account":'storageAccount',
        "storage_container":'storageContainer',
        "network_config":'networkConfig',
        "storage_resource_group":'storageResourceGroup',
        "subscription":'subscription',
        "region":'region',
        "data_transfer_info":'dataTransferInfo',
        "compute_option":"computeOption",
        "availability_set":'availabilitySet'
    }

    def __init__(self,
                 source=None,
                 resource_group=None,
                 storage_account=None,
                 storage_container=None,
                 network_config=None,
                 storage_resource_group=None,
                 subscription=None,
                 region=None,
                 data_transfer_info=None,
                 compute_option=None,
                 availability_set=None):
        """Constructor for the NewSourceConfig3 class"""

        # Initialize members of the class
        self.source = source
        self.resource_group = resource_group
        self.storage_account = storage_account
        self.storage_container = storage_container
        self.network_config = network_config
        self.storage_resource_group = storage_resource_group
        self.subscription= subscription
        self.region = region
        self.data_transfer_info = data_transfer_info
        self.compute_option = compute_option
        self.availability_set = availability_set


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
        resource_group = cohesity_management_sdk.models_v2.resource_group.ResourceGroup.from_dictionary(dictionary.get('resourceGroup')) if dictionary.get('resourceGroup') else None
        storage_account = cohesity_management_sdk.models_v2.storage_account.StorageAccount.from_dictionary(dictionary.get('storageAccount')) if dictionary.get('storageAccount') else None
        storage_container = cohesity_management_sdk.models_v2.storage_container_1.StorageContainer1.from_dictionary(dictionary.get('storageContainer')) if dictionary.get('storageContainer') else None
        network_config = cohesity_management_sdk.models_v2.network_config_4.NetworkConfig4.from_dictionary(dictionary.get('networkConfig')) if dictionary.get('networkConfig') else None
        storage_resource_group = cohesity_management_sdk.models_v2.storage_resource_group.StorageResourceGroup.from_dictionary(dictionary.get('storageResourceGroup')) if dictionary.get('storageResourceGroup') else None
        subscription = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(
            dictionary.get('subscription')) if dictionary.get('subscription') else None
        region = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('region')) if dictionary.get('region') else None
        data_transfer_info = cohesity_management_sdk.models_v2.data_transfer_info_request.DataTransferInfoRequest.from_dictionary(
            dictionary.get('dataTransferInfo')) if dictionary.get('dataTransferInfo') else None
        compute_option = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(
            dictionary.get('computeOption')) if dictionary.get('computeOption') else None
        availability_set = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(
            dictionary.get('availabilitySet')) if dictionary.get('availabilitySet') else None

        # Return an object of this model
        return cls(source,
                   resource_group,
                   storage_account,
                   storage_container,
                   network_config,
                   storage_resource_group,
                   subscription,
                   region,
                   data_transfer_info,
                   compute_option,
                   availability_set)