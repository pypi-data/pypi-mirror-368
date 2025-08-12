# -*- coding: utf-8 -*-


class FlashBladeRegistrationInfo(object):

    """Implementation of the 'FlashBladeRegistrationInfo' model.

    Specifies the information specific to flashblade registration.

    Attributes:
        ip (string): Specifies management ip of pure flashblade server.
        api_token (string): Specifies the api token of the pure flashblade.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "api_token":'apiToken',
        "ip":'ip'
    }

    def __init__(self,
                 api_token=None,
                 ip=None):
        """Constructor for the FlashBladeRegistrationInfo class"""

        # Initialize members of the class
        self.ip = ip
        self.api_token = api_token


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
        api_token = dictionary.get('apiToken')
        ip = dictionary.get('ip')

        # Return an object of this model
        return cls(api_token,
                   ip)


