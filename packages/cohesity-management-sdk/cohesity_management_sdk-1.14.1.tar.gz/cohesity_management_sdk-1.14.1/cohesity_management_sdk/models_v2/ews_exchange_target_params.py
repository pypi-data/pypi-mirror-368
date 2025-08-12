# -*- coding: utf-8 -*-


class EwsExchangeTargetParam(object):

    """Implementation of the 'EwsExchangeTargetParam' model.

    Describes the Exchange target to recover to.

    Attributes:
        ews_exchange_server_entity_id (long|int64): Specifies the entity ID of the exchange server.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "ews_exchange_server_entity_id":'ewsExchangeServerEntityId'
    }

    def __init__(self,
                 ews_exchange_server_entity_id=None):
        """Constructor for the EwsExchangeTargetParam class"""

        # Initialize members of the class
        self.ews_exchange_server_entity_id = ews_exchange_server_entity_id


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
        ews_exchange_server_entity_id = dictionary.get('ewsExchangeServerEntityId')

        # Return an object of this model
        return cls(ews_exchange_server_entity_id)