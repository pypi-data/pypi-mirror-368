# -*- coding: utf-8 -*-


class RigelConnectionInfo(object):

    """Implementation of the 'Rigel Connection Info.' model.

    Specifies the Rigel connection info.

    Attributes:
        is_active (bool): Specifies if the connection is active.
        message (string): Specifies possible error message when rigel is not
            able to connect.
        last_connected_timestamp_msecs (long|int): Specifies last timestamp
            for which connection status was known.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "is_active":'isActive',
        "message":'message',
        "last_connected_timestamp_msecs":'lastConnectedTimestampMsecs'
    }

    def __init__(self,
                 is_active=None,
                 message=None,
                 last_connected_timestamp_msecs=None):
        """Constructor for the RigelConnectionInfo class"""

        # Initialize members of the class
        self.is_active = is_active
        self.message = message
        self.last_connected_timestamp_msecs = last_connected_timestamp_msecs


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
        is_active = dictionary.get('isActive')
        message = dictionary.get('message')
        last_connected_timestamp_msecs = dictionary.get('lastConnectedTimestampMsecs')

        # Return an object of this model
        return cls(is_active,
                   message,
                   last_connected_timestamp_msecs)


