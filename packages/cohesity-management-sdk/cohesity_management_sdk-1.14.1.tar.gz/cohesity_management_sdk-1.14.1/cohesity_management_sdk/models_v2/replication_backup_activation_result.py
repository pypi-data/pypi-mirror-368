# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.reverse_replication_result
import cohesity_management_sdk.models_v2.failover_objects

class ReplicationBackupActivationResult(object):

    """Implementation of the 'ReplicationBackupActivationResult' model.

    Specifies the result returned after creating a protection group for
    backing up failover objects on replication cluster.

    Attributes:
        protection_group_id (string): Specifies the protection group id that
            will be returned upon creation of new group or existing group for
            backing up failover entities.
        reverse_replication_result (ReverseReplicationResult): Specifies the
            request parameters to create a view failover task.
        objects (list of FailoverObjects): Specifies the list of failover
            object that are going to be protected on replication cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_group_id":'protectionGroupId',
        "reverse_replication_result":'reverseReplicationResult',
        "objects":'objects'
    }

    def __init__(self,
                 protection_group_id=None,
                 reverse_replication_result=None,
                 objects=None):
        """Constructor for the ReplicationBackupActivationResult class"""

        # Initialize members of the class
        self.protection_group_id = protection_group_id
        self.reverse_replication_result = reverse_replication_result
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
        protection_group_id = dictionary.get('protectionGroupId')
        reverse_replication_result = cohesity_management_sdk.models_v2.reverse_replication_result.ReverseReplicationResult.from_dictionary(dictionary.get('reverseReplicationResult')) if dictionary.get('reverseReplicationResult') else None
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.failover_objects.FailoverObjects.from_dictionary(structure))

        # Return an object of this model
        return cls(protection_group_id,
                   reverse_replication_result,
                   objects)


