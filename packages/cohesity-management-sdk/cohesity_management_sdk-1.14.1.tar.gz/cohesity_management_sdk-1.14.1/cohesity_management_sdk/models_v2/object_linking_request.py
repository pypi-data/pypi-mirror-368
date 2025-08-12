# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.replica_failover_object

class ObjectLinkingRequest(object):

    """Implementation of the 'ObjectLinkingRequest' model.

    Request for linking replicated objects to failover objects on replication
    cluster.

    Attributes:
        object_map (list of ReplicaFailoverObject): Specifies the objectMap
            that will be used to create linking between given replicated
            source entity and newly restored entity on erplication cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_map":'objectMap'
    }

    def __init__(self,
                 object_map=None):
        """Constructor for the ObjectLinkingRequest class"""

        # Initialize members of the class
        self.object_map = object_map


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
        object_map = None
        if dictionary.get("objectMap") is not None:
            object_map = list()
            for structure in dictionary.get('objectMap'):
                object_map.append(cohesity_management_sdk.models_v2.replica_failover_object.ReplicaFailoverObject.from_dictionary(structure))

        # Return an object of this model
        return cls(object_map)


