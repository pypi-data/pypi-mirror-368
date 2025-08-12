# -*- coding: utf-8 -*-


class SourceReplicaObject(object):

    """Implementation of the 'SourceReplicaObject' model.

    Specifies the response after succesfully initiating the failover request.

    Attributes:
        replica_object_id (long|int): Specifies the object Id existing on the
            replciation cluster.
        source_object_id (long|int): Specifies the corrosponding object id
            existing on the source cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "replica_object_id":'replicaObjectId',
        "source_object_id":'sourceObjectId'
    }

    def __init__(self,
                 replica_object_id=None,
                 source_object_id=None):
        """Constructor for the SourceReplicaObject class"""

        # Initialize members of the class
        self.replica_object_id = replica_object_id
        self.source_object_id = source_object_id


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
        source_object_id = dictionary.get('sourceObjectId')

        # Return an object of this model
        return cls(replica_object_id,
                   source_object_id)


