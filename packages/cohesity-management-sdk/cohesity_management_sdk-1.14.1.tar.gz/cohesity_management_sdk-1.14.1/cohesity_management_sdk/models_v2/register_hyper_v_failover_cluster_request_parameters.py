# -*- coding: utf-8 -*-


class RegisterHyperVfailoverclusterrequestparameters(object):

    """Implementation of the 'Register HyperV failover cluster request parameters' model.

    Register HyperV failover cluster request parameters

    Attributes:
        endpoint (string): Specifies the endpoint IPaddress, URL or hostname of the host.
        description (string): Specifies the description of the source being registered.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "endpoint":'endpoint',
        "description":'description'
    }

    def __init__(self,
                 endpoint=None,
                 description=None):
        """Constructor for the Register HyperV failover cluster request parameters class"""

        # Initialize members of the class
        self.endpoint = endpoint
        self.description = description


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
        endpoint = dictionary.get('endpoint')
        description = dictionary.get('description')

        # Return an object of this model
        return cls(
                   endpoint,
                   description)