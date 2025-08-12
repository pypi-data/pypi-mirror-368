# -*- coding: utf-8 -*-


class AzureSubscription(object):

    """Implementation of the 'AzureSubscription' model.

    Specifies the details of an Azure subscription

    Attributes:
        subscription_id (string): Specifies the id of Azure subscription.
            """

    # Create a mapping from Model property names to API property names
    _names = {
        "subscription_id":'subscriptionId'
    }

    def __init__(self,
                 subscription_id=None
                 ):
        """Constructor for the AzureSubscription class"""

        # Initialize members of the class
        self.subscription_id = subscription_id

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
        subscription_id = dictionary.get('subscriptionId')

        # Return an object of this model
        return cls(subscription_id)