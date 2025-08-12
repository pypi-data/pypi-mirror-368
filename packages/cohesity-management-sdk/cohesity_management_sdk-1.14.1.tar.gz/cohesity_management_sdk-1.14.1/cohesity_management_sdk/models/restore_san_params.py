# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.entity_proto


class RestoreSanParams(object):

    """Implementation of the 'RestoreSanParams' model.

    Attributes:

        transport_mode (int): TODO: Type description here.
        storage_pool (EntityProto): Target storage pool to restore a volume
            or a group. Currently this field
            is used for Ibm FlashSystem SAN environment.
        use_thin_clone (bool): Flag specifying if we should
            preserve object attributes at the time of restore.
    """


    # Create a mapping from Model property names to API property names
    _names = {
        "transport_mode":'transportMode',
        "storage_pool":'storagePool',
        "use_thin_clone":'useThinClone',
    }
    def __init__(self,
                 transport_mode=None,
                 storage_pool=None,
                 use_thin_clone=None,
            ):

        """Constructor for the RestoreSanParams class"""

        # Initialize members of the class
        self.transport_mode = transport_mode
        self.storage_pool = storage_pool
        self.use_thin_clone = use_thin_clone

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
        transport_mode = dictionary.get('transportMode')
        storage_pool = cohesity_management_sdk.models.entity_proto.EntityProto.from_dictionary(dictionary.get('storagePool')) if dictionary.get('storagePool') else None
        use_thin_clone = dictionary.get('useThinClone')

        # Return an object of this model
        return cls(
            transport_mode,
            storage_pool,
            use_thin_clone
)