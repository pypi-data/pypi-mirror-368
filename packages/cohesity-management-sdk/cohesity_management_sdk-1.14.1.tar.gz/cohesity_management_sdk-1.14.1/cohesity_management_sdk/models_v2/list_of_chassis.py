# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.chassis_specific_response

class ListOfChassis(object):

    """Implementation of the 'List of chassis' model.

    Specifies the list of hardware chassis.

    Attributes:
        chassis (list of ChassisSpecificResponse): Specifies the list of
            chassis.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "chassis":'chassis'
    }

    def __init__(self,
                 chassis=None):
        """Constructor for the ListOfChassis class"""

        # Initialize members of the class
        self.chassis = chassis


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
        chassis = None
        if dictionary.get("chassis") is not None:
            chassis = list()
            for structure in dictionary.get('chassis'):
                chassis.append(cohesity_management_sdk.models_v2.chassis_specific_response.ChassisSpecificResponse.from_dictionary(structure))

        # Return an object of this model
        return cls(chassis)


