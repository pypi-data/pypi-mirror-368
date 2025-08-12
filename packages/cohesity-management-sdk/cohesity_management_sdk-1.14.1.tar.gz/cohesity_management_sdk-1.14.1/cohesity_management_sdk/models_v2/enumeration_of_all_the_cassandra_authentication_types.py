# -*- coding: utf-8 -*-


class EnumerationOfAllTheCassandraAuthenticationTypes(object):

    """Implementation of the 'Enumeration of all the Cassandra Authentication types.' model.

    Enumeration of all the Cassandra Authentication types.

    Attributes:
        cassandra_auth_type (CassandraAuthTypeEnum): Enumeration of all the
            Cassandra Authentication.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cassandra_auth_type":'CassandraAuthType'
    }

    def __init__(self,
                 cassandra_auth_type=None):
        """Constructor for the EnumerationOfAllTheCassandraAuthenticationTypes class"""

        # Initialize members of the class
        self.cassandra_auth_type = cassandra_auth_type


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
        cassandra_auth_type = dictionary.get('CassandraAuthType')

        # Return an object of this model
        return cls(cassandra_auth_type)


