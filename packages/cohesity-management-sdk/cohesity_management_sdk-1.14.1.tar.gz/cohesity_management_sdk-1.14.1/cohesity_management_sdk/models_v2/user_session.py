# -*- coding: utf-8 -*-


class UserSession(object):

    """Implementation of the 'UserSession' model.

    User session response

    Attributes:
        session_id (string): Specifies the session id

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "session_id":'sessionId'
    }

    def __init__(self,
                 session_id=None):
        """Constructor for the UserSession class"""

        # Initialize members of the class
        self.session_id = session_id


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
        session_id = dictionary.get('sessionId')

        # Return an object of this model
        return cls(session_id)


