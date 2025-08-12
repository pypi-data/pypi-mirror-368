# -*- coding: utf-8 -*-


class NodeIdentifyRequestParameters(object):

    """Implementation of the 'Node Identify Request Parameters.' model.

    Specifies the parameter to identify node.

    Attributes:
        identify (bool): Turn on/off node led light if set to true/false
            respectively.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "identify":'identify'
    }

    def __init__(self,
                 identify=None):
        """Constructor for the NodeIdentifyRequestParameters class"""

        # Initialize members of the class
        self.identify = identify


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
        identify = dictionary.get('identify')

        # Return an object of this model
        return cls(identify)


