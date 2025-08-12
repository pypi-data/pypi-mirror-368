# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class AlertVaultInfo(object):

    """Implementation of the 'AlertVaultInfo' model.

    Specifies vault info associated with an Alert.

    Attributes:
        global_vault_id (string): Specifies Global vault id.
        region_id (string): Specifies id of region where vault resides.
        region_name (string): Specifies id of region where vault resides.
        vault_name (string): Specifies name of vault.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "global_vault_id": 'globalVaultId',
        "region_id": 'regionId',
        "region_name": 'regionName',
        "vault_name":'vaultName'
    }

    def __init__(self,
                 global_vault_id=None,
                 region_id=None,
                 region_name=None,
                 vault_name=None):
        """Constructor for the AlertVaultInfo class"""

        # Initialize members of the class
        self.global_vault_id = global_vault_id
        self.region_id = region_id
        self.region_name = region_name
        self.vault_name = vault_name

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
        global_vault_id = dictionary.get('globalVaultId')
        region_id = dictionary.get('regionId')
        region_name = dictionary.get('regionName')
        vault_name = dictionary.get('vaultName')

        # Return an object of this model
        return cls(global_vault_id,
                   region_id,
                   region_name,
                   vault_name)


