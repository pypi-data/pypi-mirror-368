# -*- coding: utf-8 -*-


class MsSQLCommonConnectionParams(object):

    """Implementation of the 'MsSQLCommonConnectionParams' model.

    Specifies the common parameters to connect to a SQL node/cluster

    Attributes:
        host_identifier (string): Specifies the unique identifier to locate
            the SQL node or cluster. The host identifier can be IP address or
            FQDN.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "host_identifier":'hostIdentifier'
    }

    def __init__(self,
                 host_identifier=None):
        """Constructor for the MsSQLCommonConnectionParams class"""

        # Initialize members of the class
        self.host_identifier = host_identifier


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
        host_identifier = dictionary.get('hostIdentifier')

        # Return an object of this model
        return cls(host_identifier)


