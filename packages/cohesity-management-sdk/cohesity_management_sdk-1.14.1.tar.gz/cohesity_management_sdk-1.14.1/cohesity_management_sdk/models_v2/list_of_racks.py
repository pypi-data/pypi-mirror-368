# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.rack_specific_response

class ListOfRacks(object):

    """Implementation of the 'List of Racks' model.

    Specifies info about list of racks.

    Attributes:
        racks (list of RackSpecificResponse): Specifies list of racks

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "racks":'racks'
    }

    def __init__(self,
                 racks=None):
        """Constructor for the ListOfRacks class"""

        # Initialize members of the class
        self.racks = racks


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
        racks = None
        if dictionary.get("racks") is not None:
            racks = list()
            for structure in dictionary.get('racks'):
                racks.append(cohesity_management_sdk.models_v2.rack_specific_response.RackSpecificResponse.from_dictionary(structure))

        # Return an object of this model
        return cls(racks)


