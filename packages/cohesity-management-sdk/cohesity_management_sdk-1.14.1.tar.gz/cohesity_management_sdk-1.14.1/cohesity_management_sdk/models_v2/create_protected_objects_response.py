# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.object_protection_summary

class CreateProtectedObjectsResponse(object):

    """Implementation of the 'CreateProtectedObjectsResponse' model.

    Specifies the protected objects response.

    Attributes:
        protected_objects (list of ObjectProtectionSummary): Specifies the
            list of protected objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protected_objects":'protectedObjects'
    }

    def __init__(self,
                 protected_objects=None):
        """Constructor for the CreateProtectedObjectsResponse class"""

        # Initialize members of the class
        self.protected_objects = protected_objects


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
        protected_objects = None
        if dictionary.get("protectedObjects") is not None:
            protected_objects = list()
            for structure in dictionary.get('protectedObjects'):
                protected_objects.append(cohesity_management_sdk.models_v2.object_protection_summary.ObjectProtectionSummary.from_dictionary(structure))

        # Return an object of this model
        return cls(protected_objects)


