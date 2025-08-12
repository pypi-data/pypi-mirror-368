# -*- coding: utf-8 -*-


class PreparePlannedFailverParams(object):

    """Implementation of the 'PreparePlannedFailverParams' model.

    Specifies parameters of preparation of a planned failover.

    Attributes:
        reverse_replication (bool): Specifies whether a reverse replication
            needs to be set for the view on target cluster after failover.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "reverse_replication":'reverseReplication'
    }

    def __init__(self,
                 reverse_replication=None):
        """Constructor for the PreparePlannedFailverParams class"""

        # Initialize members of the class
        self.reverse_replication = reverse_replication


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
        reverse_replication = dictionary.get('reverseReplication')

        # Return an object of this model
        return cls(reverse_replication)


