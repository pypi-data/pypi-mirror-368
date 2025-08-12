# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protection_object_input

class ProtectedObjectResumeActionParams(object):

    """Implementation of the 'ProtectedObjectResumeActionParams' model.

    Specifies the request parameters for Resume action on Protected objects.

    Attributes:
        objects (list of ProtectionObjectInput): Specifies the list of objects
            to perform an action. If provided object id is not explicitly
            protected by object protection, then given action will not be
            performed on that.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects'
    }

    def __init__(self,
                 objects=None):
        """Constructor for the ProtectedObjectResumeActionParams class"""

        # Initialize members of the class
        self.objects = objects


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
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.protection_object_input.ProtectionObjectInput.from_dictionary(structure))

        # Return an object of this model
        return cls(objects)


