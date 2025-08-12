# -*- coding: utf-8 -*-


class CommonRemoteStorageInfo(object):

    """Implementation of the 'Common Remote Storage Info' model.

    Specifies the details of common remote storage info.

    Attributes:
        id (long|int): Specifies unique id of the registered remote storage.
        product (string): Specifies the product type of the remote storage.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "product":'product',
        "id":'id'
    }

    def __init__(self,
                 product='FlashBlade',
                 id=None):
        """Constructor for the CommonRemoteStorageInfo class"""

        # Initialize members of the class
        self.id = id
        self.product = product


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
        product = dictionary.get("product") if dictionary.get("product") else 'FlashBlade'
        id = dictionary.get('id')

        # Return an object of this model
        return cls(product,
                   id)


