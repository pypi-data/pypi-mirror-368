# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.run_object_physical_params

class RunObject(object):

    """Implementation of the 'RunObject' model.

    Specifies the object details to create a protection run.

    Attributes:
        id (long|int): Specifies the id of object.
        app_ids (list of long|int): Specifies a list of ids of applications.
        physical_params (RunObjectPhysicalParams): Specifies physical
            parameters for this run.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "app_ids":'appIds',
        "physical_params":'physicalParams'
    }

    def __init__(self,
                 id=None,
                 app_ids=None,
                 physical_params=None):
        """Constructor for the RunObject class"""

        # Initialize members of the class
        self.id = id
        self.app_ids = app_ids
        self.physical_params = physical_params


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
        app_ids = dictionary.get('appIds')
        physical_params = cohesity_management_sdk.models_v2.run_object_physical_params.RunObjectPhysicalParams.from_dictionary(dictionary.get('physicalParams')) if dictionary.get('physicalParams') else None

        # Return an object of this model
        return cls(id,
                   app_ids,
                   physical_params)


