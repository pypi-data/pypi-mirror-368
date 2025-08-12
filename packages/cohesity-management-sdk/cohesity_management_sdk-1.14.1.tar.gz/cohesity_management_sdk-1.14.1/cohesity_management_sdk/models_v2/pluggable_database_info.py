# -*- coding: utf-8 -*-


class PluggableDatabaseInfo(object):

    """Implementation of the 'PluggableDatabaseInfo' model.

    Specifies the information about Pluggable databases.

    Attributes:
        database_id (string): Specifies the database Id of the Pluggable DB.
        database_name (string): Specifies the name of the Pluggable DB.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "database_id":'databaseId',
        "database_name":'databaseName'
    }

    def __init__(self,
                 database_id=None,
                 database_name=None):
        """Constructor for the PluggableDatabaseInfo class"""

        # Initialize members of the class
        self.database_id = database_id
        self.database_name = database_name


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
        database_id = dictionary.get('databaseId')
        database_name = dictionary.get('databaseName')

        # Return an object of this model
        return cls(database_id,
                   database_name)


