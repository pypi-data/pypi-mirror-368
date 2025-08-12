# -*- coding: utf-8 -*-


class RigelClaimInfo(object):

    """Implementation of the 'Rigel Claim Info.' model.

    Specifies the Rigel registration info.

    Attributes:
        status (Status24Enum): Specifies the registration status.
        message (string): Specifies possible error message during
            registration.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "status":'status',
        "message":'message'
    }

    def __init__(self,
                 status=None,
                 message=None):
        """Constructor for the RigelClaimInfo class"""

        # Initialize members of the class
        self.status = status
        self.message = message


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
        status = dictionary.get('status')
        message = dictionary.get('message')

        # Return an object of this model
        return cls(status,
                   message)


