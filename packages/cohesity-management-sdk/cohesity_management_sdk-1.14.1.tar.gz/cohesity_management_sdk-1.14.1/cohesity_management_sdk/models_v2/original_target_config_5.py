# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.server_credentials

class OriginalTargetConfig5(object):

    """Implementation of the 'OriginalTargetConfig5' model.

    Specifies the configuration for mounting to the original target.

    Attributes:
        server_credentials (ServerCredentials): Specifies credentials to
            access the target server. This is required if the server is of
            Linux OS.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "server_credentials":'serverCredentials'
    }

    def __init__(self,
                 server_credentials=None):
        """Constructor for the OriginalTargetConfig5 class"""

        # Initialize members of the class
        self.server_credentials = server_credentials


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
        server_credentials = cohesity_management_sdk.models_v2.server_credentials.ServerCredentials.from_dictionary(dictionary.get('serverCredentials')) if dictionary.get('serverCredentials') else None

        # Return an object of this model
        return cls(server_credentials)


