# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protection_object_input

class GenericNasDataMigrationParams(object):

    """Implementation of the 'GenericNasDataMigrationParams' model.

    Specifies the parameters which are specific to NAS related Protection
    Groups.

    Attributes:
        objects (list of ProtectionObjectInput): Specifies the objects to be
            included in the Protection Group.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects'
    }

    def __init__(self,
                 objects=None):
        """Constructor for the GenericNasDataMigrationParams class"""

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


