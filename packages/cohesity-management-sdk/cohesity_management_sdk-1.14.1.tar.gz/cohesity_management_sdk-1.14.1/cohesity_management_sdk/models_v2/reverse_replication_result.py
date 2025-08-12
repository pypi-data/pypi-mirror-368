# -*- coding: utf-8 -*-


class ReverseReplicationResult(object):

    """Implementation of the 'ReverseReplicationResult' model.

    Specifies the request parameters to create a view failover task.

    Attributes:
        is_reverse_replication_enabled (bool): Specifies whether the reverse
            replication was enabled or not during group creation. It can be
            false, if source cluster is not reachable for reverse
            replication.
        error_reason (string): Specifies the reason of not enabling reverse
            replication.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "is_reverse_replication_enabled":'isReverseReplicationEnabled',
        "error_reason":'errorReason'
    }

    def __init__(self,
                 is_reverse_replication_enabled=None,
                 error_reason=None):
        """Constructor for the ReverseReplicationResult class"""

        # Initialize members of the class
        self.is_reverse_replication_enabled = is_reverse_replication_enabled
        self.error_reason = error_reason


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
        is_reverse_replication_enabled = dictionary.get('isReverseReplicationEnabled')
        error_reason = dictionary.get('errorReason')

        # Return an object of this model
        return cls(is_reverse_replication_enabled,
                   error_reason)


