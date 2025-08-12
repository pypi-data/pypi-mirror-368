# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recovery

class ListOfRecoveries(object):

    """Implementation of the 'List of Recoveries.' model.

    Specifies list of Recoveries.

    Attributes:
        recoveries (list of Recovery): Specifies list of Recoveries.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recoveries":'recoveries'
    }

    def __init__(self,
                 recoveries=None):
        """Constructor for the ListOfRecoveries class"""

        # Initialize members of the class
        self.recoveries = recoveries


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
        recoveries = None
        if dictionary.get("recoveries") is not None:
            recoveries = list()
            for structure in dictionary.get('recoveries'):
                recoveries.append(cohesity_management_sdk.models_v2.recovery.Recovery.from_dictionary(structure))

        # Return an object of this model
        return cls(recoveries)


