# -*- coding: utf-8 -*-


class VCDVCenterInfo(object):

    """Implementation of the 'VCD vCenter Info' model.

    Specifies information about a vCetner.

    Attributes:
        name (string): Specifies the name of the vCenter.
        endpoint (string): Specifies the endpoint of the vCenter.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "endpoint":'endpoint'
    }

    def __init__(self,
                 name=None,
                 endpoint=None):
        """Constructor for the VCDVCenterInfo class"""

        # Initialize members of the class
        self.name = name
        self.endpoint = endpoint


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
        name = dictionary.get('name')
        endpoint = dictionary.get('endpoint')

        # Return an object of this model
        return cls(name,
                   endpoint)


