# -*- coding: utf-8 -*-


class AzureSqlSkuOptions(object):

    """Implementation of the 'AzureSqlSkuOptions' model.

    Specifies the SQL SKU parameters which are specific to Azure related
      Object Protection & Recovery.

    Attributes:
        capacity (long|int): Specifies the capacity of the sku. For azure sql dbs, this is
          the number of cores. Default value is 4.
        name (NameEnum): Specifies the sku name for azure sql databases and by default
          Hyperscale is selected.
        tier_type (TierTypeEnum): Specifies the sku tier selection for azure sql databases and
          by default HS_Gen5 is selected. The tiers must match their sku name selected.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "capacity":'capacity',
        "name":'name',
        "tier_type":'tierType'
    }

    def __init__(self,
                 capacity=None,
                 name=None,
                 tier_type=None):
        """Constructor for the AzureSqlSkuOptions class"""

        # Initialize members of the class
        self.capacity = capacity
        self.name = name
        self.tier_type = tier_type


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
        capacity = dictionary.get('capacity')
        name = dictionary.get('name')
        tier_type = dictionary.get('tierType')

        # Return an object of this model
        return cls(capacity,
                   name,
                   tier_type)