# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.aag_replica_info

class AAGInfo(object):

    """Implementation of the 'AAGInfo' model.

    Specifies the information about the AAG.

    Attributes:
        aag_replicas (list of AAGReplicaInfo):  Specifies the list of AAG replicas that are part of the AAG.
        name (string): Specifies the name about the AAG.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "aag_replicas": 'aagReplicas',
        "name": 'name'
    }

    def __init__(self,
                 aag_replicas=None,
                 name=None):
        """Constructor for the AAGInfo class"""

        # Initialize members of the class
        self.aag_replicas = aag_replicas
        self.name = name


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
        name = dictionary.get('name')
        aag_replicas = None
        if dictionary.get('aagReplicas', None):
            aag_replicas = list()
            for structure in dictionary.get('aagReplicas'):
                aag_replicas.append(cohesity_management_sdk.models.aag_replica_info.AAGReplicaInfo.from_dictionary(structure))

        # Return an object of this model
        return cls(aag_replicas,
                   name)


