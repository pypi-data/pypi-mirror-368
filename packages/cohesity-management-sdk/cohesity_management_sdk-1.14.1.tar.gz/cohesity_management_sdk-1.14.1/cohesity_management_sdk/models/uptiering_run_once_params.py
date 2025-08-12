# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class UptieringRunOnceParams(object):

    """Implementation of the 'UptieringRunOnceParams' model.

    Attributes:
        uptier_path (string): Ignore the uptiering policy and uptier the
            pointed by the 'uptier_path'. If path is '/', then uptier
            everything.
        use_entity_id_for_uptier_range (bool): Flag to determine whether
            entity id is used for uptier range.
            This is applicable only for uptier jobs.
            TODO: Exists to support upgrade scenario. Can be deprecated once
            all customers have upgraded beyond 7.0.1.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "uptier_path":'uptierPath',
        "use_entity_id_for_uptier_range": 'useEntityIdForUptierRange'
    }

    def __init__(self,
                 uptier_path=None,
                 use_entity_id_for_uptier_range=None):
        """Constructor for the UptieringRunOnceParams class"""

        # Initialize members of the class
        self.uptier_path = uptier_path
        self.use_entity_id_for_uptier_range = use_entity_id_for_uptier_range


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
        uptier_path = dictionary.get('uptierPath')
        use_entity_id_for_uptier_range = dictionary.get('useEntityIdForUptierRange')

        # Return an object of this model
        return cls(uptier_path,
                   use_entity_id_for_uptier_range)


