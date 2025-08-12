# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class Entity_SKU(object):

    """Implementation of the 'Entity_SKU' model.

    Specifies an Object representing Universal Data Adapter.

    Attributes:
        capacity (int): Capacity of the sku.
            For azure sql dbs, this is the number of cores.
        name (string): Can be one of Name_Type enum above.
        name_type (int): Enum representation of name for UI selection purpose.
        tier (string):  Can be one of Tier_Type enum above.
        tier_type (int): Enum representation of tier for UI selection purpose.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "capacity":'capacity',
        "name":'name',
        "name_type":'nameType',
        "tier":'tier',
        "tier_type":'tierType'
    }

    def __init__(self,
                 capacity=None,
                 name=None,
                 name_type=None,
                 tier=None,
                 tier_type=None):
        """Constructor for the Entity_SKU class"""

        # Initialize members of the class
        self.capacity = capacity
        self.name = name
        self.name_type = name_type
        self.tier = tier
        self.tier_type = tier_type


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The names
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        capacity =  dictionary.get('capacity')
        name = dictionary.get('name')
        name_type =dictionary.get('nameType')
        tier = dictionary.get('tier')
        tier_type = dictionary.get('tierType')

        # Return an object of this model
        return cls(capacity,
                   name,
                   name_type,
                   tier,
                   tier_type)


