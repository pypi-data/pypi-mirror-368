# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.



class RestoreOutlookParams_EwsExchangeTarget(object):

    """Implementation of the 'RestoreOutlookParams_EwsExchangeTarget' model.

    TODO: type description here.


    Attributes:
        ews_exchange_server_entity_id (long|int): Entity ID of the on prem exchange server that we will recover to.
          Must be set when doing a kRecoverO365ToExchangeServer recovery.
    """


    # Create a mapping from Model property names to API property names
    _names = {
        "ews_exchange_server_entity_id": 'ewsExchangeServerEntityId'
    }
    def __init__(self,
                 ews_exchange_server_entity_id=None
            ):

        """Constructor for the RestoreOutlookParams_EwsExchangeTarget class"""

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
        return cls(
            ews_exchange_server_entity_id)