# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.flashblade_params

class RemoteStorageRegistrationParameters(object):

    """Implementation of the 'Remote storage Registration parameters.' model.

    Specifies the remote storage Registration parameters.

    Attributes:
        id (long|int): Specifies unique id of the registered remote storage.
        product (string): Specifies the product type of the remote storage.
        flashblade_params (FlashbladeParams): Specifies the information
            related to Registered Pure Flashblade.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "product":'product',
        "id":'id',
        "flashblade_params":'flashbladeParams'
    }

    def __init__(self,
                 product='FlashBlade',
                 id=None,
                 flashblade_params=None):
        """Constructor for the RemoteStorageRegistrationParameters class"""

        # Initialize members of the class
        self.id = id
        self.product = product
        self.flashblade_params = flashblade_params


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
        flashblade_params = cohesity_management_sdk.models_v2.flashblade_params.FlashbladeParams.from_dictionary(dictionary.get('flashbladeParams')) if dictionary.get('flashbladeParams') else None

        # Return an object of this model
        return cls(product,
                   id,
                   flashblade_params)


