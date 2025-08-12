# -*- coding: utf-8 -*-


class AzureTargetConfiguration(object):

    """Implementation of the 'Azure Target Configuration' model.

    Specifies the configuration for adding Azure as replication target

    Attributes:
        source_id (long|int): Specifies the source id of the Azure protection
            source registered on Cohesity cluster.
        name (string): Specifies the name of the Azure Replication target.
        resource_group (long|int): Specifies id of the Azure resource group
            used to filter regions in UI.
        resource_group_name (string): Specifies name of the Azure resource
            group used to filter regions in UI.
        storage_account (int): Specifies id of the storage account of Azure
            replication target which will contain storage container.
        storage_account_name (string): Specifies name of the storage account
            of Azure replication target which will contain storage container.
        storage_container (int): Specifies id of the storage container of
            Azure Replication target.
        storage_container_name (string): Specifies name of the storage
            container of Azure Replication target.
        storage_resource_group (int): Specifies id of the storage resource
            group of Azure Replication target.
        storage_resource_group_name (string): Specifies name of the storage
            resource group of Azure Replication target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source_id":'sourceId',
        "name":'name',
        "resource_group":'resourceGroup',
        "resource_group_name":'resourceGroupName',
        "storage_account":'storageAccount',
        "storage_account_name":'storageAccountName',
        "storage_container":'storageContainer',
        "storage_container_name":'storageContainerName',
        "storage_resource_group":'storageResourceGroup',
        "storage_resource_group_name":'storageResourceGroupName'
    }

    def __init__(self,
                 source_id=None,
                 name=None,
                 resource_group=None,
                 resource_group_name=None,
                 storage_account=None,
                 storage_account_name=None,
                 storage_container=None,
                 storage_container_name=None,
                 storage_resource_group=None,
                 storage_resource_group_name=None):
        """Constructor for the AzureTargetConfiguration class"""

        # Initialize members of the class
        self.source_id = source_id
        self.name = name
        self.resource_group = resource_group
        self.resource_group_name = resource_group_name
        self.storage_account = storage_account
        self.storage_account_name = storage_account_name
        self.storage_container = storage_container
        self.storage_container_name = storage_container_name
        self.storage_resource_group = storage_resource_group
        self.storage_resource_group_name = storage_resource_group_name


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
        source_id = dictionary.get('sourceId')
        name = dictionary.get('name')
        resource_group = dictionary.get('resourceGroup')
        resource_group_name = dictionary.get('resourceGroupName')
        storage_account = dictionary.get('storageAccount')
        storage_account_name = dictionary.get('storageAccountName')
        storage_container = dictionary.get('storageContainer')
        storage_container_name = dictionary.get('storageContainerName')
        storage_resource_group = dictionary.get('storageResourceGroup')
        storage_resource_group_name = dictionary.get('storageResourceGroupName')

        # Return an object of this model
        return cls(source_id,
                   name,
                   resource_group,
                   resource_group_name,
                   storage_account,
                   storage_account_name,
                   storage_container,
                   storage_container_name,
                   storage_resource_group,
                   storage_resource_group_name)


