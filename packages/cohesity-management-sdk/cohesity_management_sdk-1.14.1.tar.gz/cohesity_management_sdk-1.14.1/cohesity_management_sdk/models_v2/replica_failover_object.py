# -*- coding: utf-8 -*-


class ReplicaFailoverObject(object):

    """Implementation of the 'ReplicaFailoverObject' model.

    Specifies the object paring of replicated object and failover object
    created after restore.

    Attributes:
        replica_object_id (long|int): Specifies the object Id existing on the
            replciation cluster.
        failover_object_id (long|int): Specifies the corrosponding object id
            of the failover object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "replica_object_id":'replicaObjectId',
        "failover_object_id":'failoverObjectId'
    }

    def __init__(self,
                 replica_object_id=None,
                 failover_object_id=None):
        """Constructor for the ReplicaFailoverObject class"""

        # Initialize members of the class
        self.replica_object_id = replica_object_id
        self.failover_object_id = failover_object_id


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
        replica_object_id = dictionary.get('replicaObjectId')
        failover_object_id = dictionary.get('failoverObjectId')

        # Return an object of this model
        return cls(replica_object_id,
                   failover_object_id)


