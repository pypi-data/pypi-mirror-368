# -*- coding: utf-8 -*-


class SyslogServerStatus(object):

    """Implementation of the 'SyslogServerStatus' model.

    Remote system logging server.

    Attributes:
        id (int): The id of the syslog server.
        is_reachable (bool): Specify if the syslog server is reachable or
            not.
        message (string): Description for current status.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "is_reachable":'isReachable',
        "message":'message'
    }

    def __init__(self,
                 id=None,
                 is_reachable=None,
                 message=None):
        """Constructor for the SyslogServerStatus class"""

        # Initialize members of the class
        self.id = id
        self.is_reachable = is_reachable
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
        id = dictionary.get('id')
        is_reachable = dictionary.get('isReachable')
        message = dictionary.get('message')

        # Return an object of this model
        return cls(id,
                   is_reachable,
                   message)


