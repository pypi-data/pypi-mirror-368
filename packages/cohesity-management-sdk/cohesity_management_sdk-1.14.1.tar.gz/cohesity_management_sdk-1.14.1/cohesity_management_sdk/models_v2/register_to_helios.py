# -*- coding: utf-8 -*-


class RegisterToHelios(object):

    """Implementation of the 'Register to Helios.' model.

    Specifies the request to register to Helios.

    Attributes:
        registration_token (string): Specifies the Helios registration token.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "registration_token":'registrationToken'
    }

    def __init__(self,
                 registration_token=None):
        """Constructor for the RegisterToHelios class"""

        # Initialize members of the class
        self.registration_token = registration_token


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
        registration_token = dictionary.get('registrationToken')

        # Return an object of this model
        return cls(registration_token)


