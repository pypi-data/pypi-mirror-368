# -*- coding: utf-8 -*-

class CassandraProtectionRunParams(object):

    """Implementation of the 'CassandraProtectionRunParams' model.

    Specifies the parameters for Cassandra Adapter protection run.

    Attributes:
        set_primary_for_log (bool): Specifies the parameters to set this cluster as primary and trigger
          a new protection run for Log backup job. Default value is false.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "set_primary_for_log":'setPrimaryForLog'
    }

    def __init__(self,
                 set_primary_for_log=None):
        """Constructor for the CassandraProtectionRunParams class"""

        # Initialize members of the class
        self.set_primary_for_log = set_primary_for_log

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
        set_primary_for_log = dictionary.get('setPrimaryForLog')

        # Return an object of this model
        return cls(set_primary_for_log)