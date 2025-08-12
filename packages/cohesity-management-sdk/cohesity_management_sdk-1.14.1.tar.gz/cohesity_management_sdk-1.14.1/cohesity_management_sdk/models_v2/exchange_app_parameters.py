# -*- coding: utf-8 -*-


class ExchangeAppParameters(object):

    """Implementation of the 'Exchange App Parameters.' model.

    Specifies the Exchange special parameters for the Protection Group.

    Attributes:
        app_id (long|int): Specifies the application id of the Exchange
            database which has to be protected.
        app_name (string): Specifies the application name of the Exchange
            database which has to be protected.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "app_id":'appId',
        "app_name":'appName'
    }

    def __init__(self,
                 app_id=None,
                 app_name=None):
        """Constructor for the ExchangeAppParameters class"""

        # Initialize members of the class
        self.app_id = app_id
        self.app_name = app_name


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
        app_id = dictionary.get('appId')
        app_name = dictionary.get('appName')

        # Return an object of this model
        return cls(app_id,
                   app_name)


