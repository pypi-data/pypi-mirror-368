# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.failover_objects

class FailoverSourceCluster(object):

    """Implementation of the 'Failover source cluster.' model.

    Specifies the details about replication cluster involved in the failover
    operation.

    Attributes:
        objects (list of FailoverObjects): Specifies the details about the
            objects being failed over. In case if view based orchastrator is
            calling this then they should pass a object id for replicated view
            entity which belongs to the live tracking view on replication
            cluster.
        protection_group_id (string): Specifies the protection group id from
            the replication cluster from where the objects being failed over.
            If this is not specified then it will be infer from the list of
            objects being failed over. The protection group id must be
            specified in this format
            <cluster_id>:<cluster_incarnation_id:jobid>

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "protection_group_id":'protectionGroupId'
    }

    def __init__(self,
                 objects=None,
                 protection_group_id=None):
        """Constructor for the FailoverSourceCluster class"""

        # Initialize members of the class
        self.objects = objects
        self.protection_group_id = protection_group_id


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
                objects.append(cohesity_management_sdk.models_v2.failover_objects.FailoverObjects.from_dictionary(structure))
        protection_group_id = dictionary.get('protectionGroupId')

        # Return an object of this model
        return cls(objects,
                   protection_group_id)


