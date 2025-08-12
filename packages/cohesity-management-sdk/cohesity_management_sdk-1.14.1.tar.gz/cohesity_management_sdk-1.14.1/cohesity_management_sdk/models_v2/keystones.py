# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.keystone

class Keystones(object):

    """Implementation of the 'Keystones' model.

    Specifies a list of Keystones.

    Attributes:
        keystones (list of Keystone): Specifies a list of Keystones.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "keystones":'keystones'
    }

    def __init__(self,
                 keystones=None):
        """Constructor for the Keystones class"""

        # Initialize members of the class
        self.keystones = keystones


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
        keystones = None
        if dictionary.get("keystones") is not None:
            keystones = list()
            for structure in dictionary.get('keystones'):
                keystones.append(cohesity_management_sdk.models_v2.keystone.Keystone.from_dictionary(structure))

        # Return an object of this model
        return cls(keystones)


