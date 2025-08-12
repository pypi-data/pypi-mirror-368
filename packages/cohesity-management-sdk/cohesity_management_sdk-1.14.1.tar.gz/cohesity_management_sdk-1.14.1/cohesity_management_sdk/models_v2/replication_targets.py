# -*- coding: utf-8 -*-


class ReplicationTargets(object):

    """Implementation of the 'ReplicationTargets' model.

    Replication Targets

    Attributes:
        replication_targets (ReplicationTargets1Enum): Specifies the
            replication target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "replication_targets":'replicationTargets'
    }

    def __init__(self,
                 replication_targets=None):
        """Constructor for the ReplicationTargets class"""

        # Initialize members of the class
        self.replication_targets = replication_targets


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
        replication_targets = dictionary.get('replicationTargets')

        # Return an object of this model
        return cls(replication_targets)


