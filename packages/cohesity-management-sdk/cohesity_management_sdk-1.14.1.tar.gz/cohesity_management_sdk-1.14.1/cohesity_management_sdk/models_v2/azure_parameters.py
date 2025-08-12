# -*- coding: utf-8 -*-


class AzureParameters(object):

    """Implementation of the 'Azure Parameters.' model.

    Specifies various resources when converting and deploying a VM to Azure.

    Attributes:
        availability_set_id (long|int): Specifies the availability set.
        network_resource_group_id (long|int): Specifies id of the resource
            group for the selected virtual network.
        resource_group_id (long|int): Specifies id of the Azure resource
            group. Its value is globally unique within Azure.
        storage_account_id (long|int): Specifies id of the storage account
            that will contain the storage container within which we will
            create the blob that will become the VHD disk for the cloned VM.
        storage_container_id (long|int): Specifies id of the storage container
            within the above storage account.
        storage_resource_group_id (long|int): Specifies id of the resource
            group for the selected storage account.
        temp_vm_resource_group_id (long|int): Specifies id of the temporary
            Azure resource group.
        temp_vm_storage_account_id (long|int): Specifies id of the temporary
            VM storage account that will contain the storage container within
            which we will create the blob that will become the VHD disk for
            the cloned VM.
        temp_vm_storage_container_id (long|int): Specifies id of the temporary
            VM storage container within the above storage account.
        temp_vm_subnet_id (long|int): Specifies Id of the temporary VM subnet
            within the above virtual network.
        temp_vm_virtual_network_id (long|int): Specifies Id of the temporary
            VM Virtual Network.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "availability_set_id":'availabilitySetId',
        "network_resource_group_id":'networkResourceGroupId',
        "resource_group_id":'resourceGroupId',
        "storage_account_id":'storageAccountId',
        "storage_container_id":'storageContainerId',
        "storage_resource_group_id":'storageResourceGroupId',
        "temp_vm_resource_group_id":'tempVmResourceGroupId',
        "temp_vm_storage_account_id":'tempVmStorageAccountId',
        "temp_vm_storage_container_id":'tempVmStorageContainerId',
        "temp_vm_subnet_id":'tempVmSubnetId',
        "temp_vm_virtual_network_id":'tempVmVirtualNetworkId'
    }

    def __init__(self,
                 availability_set_id=None,
                 network_resource_group_id=None,
                 resource_group_id=None,
                 storage_account_id=None,
                 storage_container_id=None,
                 storage_resource_group_id=None,
                 temp_vm_resource_group_id=None,
                 temp_vm_storage_account_id=None,
                 temp_vm_storage_container_id=None,
                 temp_vm_subnet_id=None,
                 temp_vm_virtual_network_id=None):
        """Constructor for the AzureParameters class"""

        # Initialize members of the class
        self.availability_set_id = availability_set_id
        self.network_resource_group_id = network_resource_group_id
        self.resource_group_id = resource_group_id
        self.storage_account_id = storage_account_id
        self.storage_container_id = storage_container_id
        self.storage_resource_group_id = storage_resource_group_id
        self.temp_vm_resource_group_id = temp_vm_resource_group_id
        self.temp_vm_storage_account_id = temp_vm_storage_account_id
        self.temp_vm_storage_container_id = temp_vm_storage_container_id
        self.temp_vm_subnet_id = temp_vm_subnet_id
        self.temp_vm_virtual_network_id = temp_vm_virtual_network_id


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
        availability_set_id = dictionary.get('availabilitySetId')
        network_resource_group_id = dictionary.get('networkResourceGroupId')
        resource_group_id = dictionary.get('resourceGroupId')
        storage_account_id = dictionary.get('storageAccountId')
        storage_container_id = dictionary.get('storageContainerId')
        storage_resource_group_id = dictionary.get('storageResourceGroupId')
        temp_vm_resource_group_id = dictionary.get('tempVmResourceGroupId')
        temp_vm_storage_account_id = dictionary.get('tempVmStorageAccountId')
        temp_vm_storage_container_id = dictionary.get('tempVmStorageContainerId')
        temp_vm_subnet_id = dictionary.get('tempVmSubnetId')
        temp_vm_virtual_network_id = dictionary.get('tempVmVirtualNetworkId')

        # Return an object of this model
        return cls(availability_set_id,
                   network_resource_group_id,
                   resource_group_id,
                   storage_account_id,
                   storage_container_id,
                   storage_resource_group_id,
                   temp_vm_resource_group_id,
                   temp_vm_storage_account_id,
                   temp_vm_storage_container_id,
                   temp_vm_subnet_id,
                   temp_vm_virtual_network_id)